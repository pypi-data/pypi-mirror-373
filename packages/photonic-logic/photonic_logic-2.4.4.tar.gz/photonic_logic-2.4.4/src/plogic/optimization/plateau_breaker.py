"""
Plateau Breaker Module for Photonic Logic Optimization

Intelligent plateau detection and breaking strategies to prevent premature
convergence in Bayesian optimization. Includes Sobol quasi-random sampling,
adaptive acquisition functions, and dynamic restart strategies.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass
import warnings
from collections import deque

# Handle optional imports gracefully
try:
    from scipy.stats import qmc
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    warnings.warn("scipy not available, using fallback random sampling instead of Sobol")

try:
    from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import Matern
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    warnings.warn("scikit-learn not available, surrogate switching disabled")

# Import our enhanced components
from ..utils.plateau_utils import (
    TrustRegionManager, 
    dedupe_with_jitter, 
    generate_latin_hypercube,
    update_normalization_stats
)
from .acquisition import AcquisitionScheduler, batch_q_ei


@dataclass
class PlateauMetrics:
    """Metrics for plateau detection."""
    best_score: float
    score_variance: float
    parameter_variance: float
    r2_score: float
    mae: float
    iterations_since_improvement: int
    stuck_dimensions: List[int]


class PlateauBreaker:
    """
    Advanced plateau detection and breaking for optimization.
    
    This module provides multiple strategies to escape local minima:
    - Sobol quasi-random point injection
    - Adaptive acquisition function switching
    - Smart perturbation around best points
    - Dynamic restart from promising regions
    - Surrogate model switching based on performance
    """
    
    def __init__(self,
                 dims: int,
                 bounds: Optional[np.ndarray] = None,
                 exploration_boost: float = 3.0,
                 sobol_points: int = 20,
                 plateau_patience: int = 5,
                 r2_threshold: float = 0.5,
                 mae_threshold: float = 0.1,
                 variance_threshold: float = 1e-6,
                 history_window: int = 10):
        """
        Initialize the plateau breaker.
        
        Args:
            dims: Problem dimensionality
            bounds: Parameter bounds (dims x 2 array)
            exploration_boost: UCB beta multiplier when plateau detected
            sobol_points: Number of quasi-random points to inject
            plateau_patience: Iterations before declaring plateau
            r2_threshold: R² below which to switch strategies
            mae_threshold: MAE above which to consider model poor
            variance_threshold: Variance below which parameters are stuck
            history_window: Window size for tracking improvements
        """
        self.dims = dims
        self.bounds = bounds if bounds is not None else np.array([[0, 2]] * dims)
        self.exploration_boost = exploration_boost
        self.sobol_points = sobol_points
        self.plateau_patience = plateau_patience
        self.r2_threshold = r2_threshold
        self.mae_threshold = mae_threshold
        self.variance_threshold = variance_threshold
        self.history_window = history_window
        
        # State tracking
        self.iteration_count = 0
        self.plateau_count = 0
        self.best_score_history = deque(maxlen=history_window)
        self.parameter_history = deque(maxlen=history_window)
        self.r2_history = deque(maxlen=history_window)
        self.mae_history = deque(maxlen=history_window)
        self.iterations_since_improvement = 0
        self.current_best = None
        self.strategy_scores = {
            'sobol': 0.0,
            'ucb': 0.0,
            'perturbation': 0.0,
            'restart': 0.0
        }
        
        # Initialize Sobol sequence if available
        if SCIPY_AVAILABLE:
            self.sobol_engine = qmc.Sobol(d=dims, scramble=True)
        else:
            self.sobol_engine = None
    
    def update_history(self,
                      best_score: float,
                      best_params: np.ndarray,
                      r2_score: Optional[float] = None,
                      mae: Optional[float] = None) -> None:
        """
        Update internal history with latest optimization results.
        
        Args:
            best_score: Current best objective value
            best_params: Current best parameters
            r2_score: R² score of surrogate model
            mae: Mean absolute error of surrogate model
        """
        self.iteration_count += 1
        
        # Track improvement
        if self.current_best is None or best_score < self.current_best:
            self.iterations_since_improvement = 0
            self.current_best = best_score
        else:
            self.iterations_since_improvement += 1
        
        # Update histories
        self.best_score_history.append(best_score)
        self.parameter_history.append(best_params.copy())
        
        if r2_score is not None:
            self.r2_history.append(r2_score)
        if mae is not None:
            self.mae_history.append(mae)
    
    def detect_plateau(self) -> Tuple[bool, PlateauMetrics]:
        """
        Detect if optimization is stuck in a plateau.
        
        Returns:
            Tuple of (is_plateau, metrics)
        """
        if len(self.best_score_history) < min(3, self.plateau_patience):
            return False, None
        
        # Calculate metrics
        score_variance = np.var(list(self.best_score_history))
        
        param_variance = 0.0
        stuck_dims = []
        if len(self.parameter_history) >= 2:
            param_array = np.array(list(self.parameter_history))
            param_variance = np.mean(np.var(param_array, axis=0))
            
            # Find stuck dimensions
            dim_variances = np.var(param_array, axis=0)
            stuck_dims = [i for i, v in enumerate(dim_variances) 
                         if v < self.variance_threshold]
        
        # Get latest model metrics
        r2_score = self.r2_history[-1] if self.r2_history else 1.0
        mae = self.mae_history[-1] if self.mae_history else 0.0
        
        metrics = PlateauMetrics(
            best_score=self.current_best,
            score_variance=score_variance,
            parameter_variance=param_variance,
            r2_score=r2_score,
            mae=mae,
            iterations_since_improvement=self.iterations_since_improvement,
            stuck_dimensions=stuck_dims
        )
        
        # Plateau detection logic
        is_plateau = (
            self.iterations_since_improvement >= self.plateau_patience or
            (score_variance < self.variance_threshold and len(self.best_score_history) >= 3) or
            (param_variance < self.variance_threshold and len(self.parameter_history) >= 3) or
            (r2_score < self.r2_threshold and mae > self.mae_threshold) or
            len(stuck_dims) > self.dims * 0.5  # More than half dimensions stuck
        )
        
        if is_plateau:
            self.plateau_count += 1
        
        return is_plateau, metrics
    
    def get_sobol_points(self, n_points: Optional[int] = None) -> np.ndarray:
        """
        Generate Sobol quasi-random points for better space coverage.
        
        Args:
            n_points: Number of points to generate
            
        Returns:
            Array of Sobol points scaled to bounds
        """
        n_points = n_points or self.sobol_points
        
        if SCIPY_AVAILABLE and self.sobol_engine is not None:
            # Generate Sobol points
            points = self.sobol_engine.random(n_points)
            
            # Scale to bounds
            lower = self.bounds[:, 0]
            upper = self.bounds[:, 1]
            scaled_points = lower + points * (upper - lower)
            
            return scaled_points
        else:
            # Fallback to Latin Hypercube or random
            return self._latin_hypercube_sample(n_points)
    
    def _latin_hypercube_sample(self, n_points: int) -> np.ndarray:
        """
        Generate Latin Hypercube samples as fallback for Sobol.
        
        Args:
            n_points: Number of points to generate
            
        Returns:
            Array of LHS points
        """
        points = np.zeros((n_points, self.dims))
        
        for d in range(self.dims):
            # Create evenly spaced intervals
            intervals = np.linspace(0, 1, n_points + 1)
            
            # Random point within each interval
            for i in range(n_points):
                points[i, d] = np.random.uniform(intervals[i], intervals[i + 1])
        
        # Random permutation for each dimension
        for d in range(self.dims):
            points[:, d] = points[np.random.permutation(n_points), d]
        
        # Scale to bounds
        lower = self.bounds[:, 0]
        upper = self.bounds[:, 1]
        scaled_points = lower + points * (upper - lower)
        
        return scaled_points
    
    def get_perturbed_points(self,
                            center: np.ndarray,
                            n_points: int = 10,
                            noise_scale: float = 0.1) -> np.ndarray:
        """
        Generate points perturbed around a center point.
        
        Args:
            center: Center point for perturbation
            n_points: Number of perturbed points
            noise_scale: Scale of noise relative to bounds
            
        Returns:
            Array of perturbed points
        """
        points = []
        lower = self.bounds[:, 0]
        upper = self.bounds[:, 1]
        range_scale = (upper - lower) * noise_scale
        
        for _ in range(n_points):
            # Adaptive noise based on stuck dimensions
            noise = np.random.randn(self.dims) * range_scale
            
            # Increase noise for stuck dimensions
            if hasattr(self, '_last_metrics') and self._last_metrics:
                for dim in self._last_metrics.stuck_dimensions:
                    noise[dim] *= 2.0
            
            # Apply perturbation and clip to bounds
            perturbed = center + noise
            perturbed = np.clip(perturbed, lower, upper)
            points.append(perturbed)
        
        return np.array(points)
    
    def get_restart_points(self, n_points: int = 10) -> np.ndarray:
        """
        Generate restart points from promising regions.
        
        Args:
            n_points: Number of restart points
            
        Returns:
            Array of restart points
        """
        if len(self.parameter_history) < 3:
            # Not enough history, use random
            return self._latin_hypercube_sample(n_points)
        
        # Get best historical points
        scores = np.array(list(self.best_score_history))
        params = np.array(list(self.parameter_history))
        
        # Find top-k best points
        k = min(5, len(scores))
        best_indices = np.argsort(scores)[:k]
        best_params = params[best_indices]
        
        # Generate points around best historical points
        points = []
        points_per_center = n_points // k
        
        for center in best_params:
            perturbed = self.get_perturbed_points(
                center, points_per_center, noise_scale=0.15
            )
            points.extend(perturbed)
        
        # Fill remaining with Sobol/random
        remaining = n_points - len(points)
        if remaining > 0:
            points.extend(self.get_sobol_points(remaining))
        
        return np.array(points[:n_points])
    
    def select_acquisition_function(self, metrics: PlateauMetrics) -> Dict[str, Any]:
        """
        Select appropriate acquisition function based on plateau metrics.
        
        Args:
            metrics: Current plateau metrics
            
        Returns:
            Dictionary with acquisition function parameters
        """
        if metrics.r2_score < 0.3:
            # Model is poor, use high exploration
            return {
                'type': 'ucb',
                'beta': self.exploration_boost * 2.0,
                'strategy': 'high_exploration'
            }
        elif metrics.iterations_since_improvement > self.plateau_patience * 2:
            # Long plateau, switch to pure exploration
            return {
                'type': 'random',
                'strategy': 'pure_exploration'
            }
        elif len(metrics.stuck_dimensions) > self.dims * 0.3:
            # Many stuck dimensions, use targeted UCB
            return {
                'type': 'ucb',
                'beta': self.exploration_boost,
                'focus_dims': metrics.stuck_dimensions,
                'strategy': 'targeted_exploration'
            }
        else:
            # Standard plateau, moderate exploration boost
            return {
                'type': 'ei',
                'xi': 0.1,  # Increased from default 0.01
                'strategy': 'balanced'
            }
    
    def select_surrogate_model(self, metrics: PlateauMetrics, data_size: int) -> str:
        """
        Select appropriate surrogate model based on metrics.
        
        Args:
            metrics: Current plateau metrics
            data_size: Number of data points available
            
        Returns:
            Name of recommended surrogate model
        """
        if not SKLEARN_AVAILABLE:
            return 'default'
        
        if metrics.r2_score < 0.3 or data_size < 20:
            # Poor fit or little data, use robust model
            return 'random_forest'
        elif metrics.mae > self.mae_threshold * 2:
            # High error, use ensemble
            return 'extra_trees'
        elif data_size < 50:
            # Small data, GP works well
            return 'gaussian_process'
        elif len(metrics.stuck_dimensions) > 0:
            # Discrete-like behavior, use trees
            return 'extra_trees'
        else:
            # Default to ensemble for robustness
            return 'ensemble'
    
    def break_plateau(self,
                     current_best: np.ndarray,
                     metrics: Optional[PlateauMetrics] = None) -> Dict[str, Any]:
        """
        Generate breakthrough strategy and points.
        
        Args:
            current_best: Current best parameters
            metrics: Plateau metrics (will detect if not provided)
            
        Returns:
            Dictionary with breakthrough strategy and points
        """
        # Detect plateau if metrics not provided
        if metrics is None:
            is_plateau, metrics = self.detect_plateau()
            if not is_plateau:
                return {'strategy': 'none', 'points': np.array([])}
        
        self._last_metrics = metrics
        
        # Collect breakthrough points from multiple strategies
        all_points = []
        strategies_used = []
        
        # Strategy 1: Sobol quasi-random injection
        if metrics.iterations_since_improvement >= self.plateau_patience:
            sobol_points = self.get_sobol_points()
            all_points.append(sobol_points)
            strategies_used.append('sobol')
            self.strategy_scores['sobol'] += 1
        
        # Strategy 2: Perturbation around best
        if metrics.parameter_variance < self.variance_threshold:
            perturbed_points = self.get_perturbed_points(
                current_best, n_points=10, noise_scale=0.2
            )
            all_points.append(perturbed_points)
            strategies_used.append('perturbation')
            self.strategy_scores['perturbation'] += 1
        
        # Strategy 3: Restart from promising regions
        if metrics.iterations_since_improvement >= self.plateau_patience * 2:
            restart_points = self.get_restart_points(n_points=10)
            all_points.append(restart_points)
            strategies_used.append('restart')
            self.strategy_scores['restart'] += 1
        
        # Combine all points
        if all_points:
            breakthrough_points = np.vstack(all_points)
        else:
            # Fallback to Sobol if no strategy triggered
            breakthrough_points = self.get_sobol_points()
            strategies_used.append('sobol_fallback')
        
        # Get acquisition function recommendation
        acq_params = self.select_acquisition_function(metrics)
        
        # Get surrogate model recommendation
        surrogate_type = self.select_surrogate_model(
            metrics, len(self.best_score_history)
        )
        
        return {
            'strategy': strategies_used,
            'points': breakthrough_points,
            'acquisition': acq_params,
            'surrogate': surrogate_type,
            'metrics': metrics,
            'plateau_count': self.plateau_count
        }
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """
        Get comprehensive diagnostics of plateau breaker state.
        
        Returns:
            Dictionary with diagnostic information
        """
        is_plateau, metrics = self.detect_plateau()
        
        diagnostics = {
            'iteration_count': self.iteration_count,
            'plateau_count': self.plateau_count,
            'is_plateau': is_plateau,
            'iterations_since_improvement': self.iterations_since_improvement,
            'current_best_score': self.current_best,
            'strategy_usage': dict(self.strategy_scores),
            'history_length': len(self.best_score_history)
        }
        
        if metrics:
            diagnostics.update({
                'score_variance': metrics.score_variance,
                'parameter_variance': metrics.parameter_variance,
                'r2_score': metrics.r2_score,
                'mae': metrics.mae,
                'stuck_dimensions': metrics.stuck_dimensions,
                'stuck_ratio': len(metrics.stuck_dimensions) / self.dims
            })
        
        # Add recommendations
        if is_plateau:
            breakthrough = self.break_plateau(
                np.array(list(self.parameter_history)[-1]) 
                if self.parameter_history else np.zeros(self.dims),
                metrics
            )
            diagnostics['recommendations'] = {
                'strategies': breakthrough['strategy'],
                'n_breakthrough_points': len(breakthrough['points']),
                'acquisition_type': breakthrough['acquisition']['type'],
                'surrogate_type': breakthrough['surrogate']
            }
        
        return diagnostics
    
    def reset(self) -> None:
        """Reset the plateau breaker state."""
        self.iteration_count = 0
        self.plateau_count = 0
        self.best_score_history.clear()
        self.parameter_history.clear()
        self.r2_history.clear()
        self.mae_history.clear()
        self.iterations_since_improvement = 0
        self.current_best = None
        self.strategy_scores = {k: 0.0 for k in self.strategy_scores}
        
        # Reset Sobol engine
        if SCIPY_AVAILABLE:
            self.sobol_engine = qmc.Sobol(d=self.dims, scramble=True)


class AdaptiveOptimizer:
    """
    Wrapper class that integrates PlateauBreaker with existing optimizers.
    """
    
    def __init__(self,
                 base_optimizer: Any,
                 plateau_breaker: PlateauBreaker,
                 auto_break: bool = True):
        """
        Initialize adaptive optimizer with plateau breaking.
        
        Args:
            base_optimizer: Base optimizer instance
            plateau_breaker: PlateauBreaker instance
            auto_break: Automatically break plateaus when detected
        """
        self.base_optimizer = base_optimizer
        self.plateau_breaker = plateau_breaker
        self.auto_break = auto_break
        self.iteration = 0
    
    def suggest(self, n_points: int = 1) -> np.ndarray:
        """
        Suggest next points with plateau breaking.
        
        Args:
            n_points: Number of points to suggest
            
        Returns:
            Array of suggested points
        """
        # Get base suggestions
        base_suggestions = self.base_optimizer.suggest(n_points)
        
        if not self.auto_break:
            return base_suggestions
        
        # Check for plateau
        is_plateau, metrics = self.plateau_breaker.detect_plateau()
        
        if is_plateau:
            print(f"[PlateauBreaker] Plateau detected at iteration {self.iteration}")
            
            # Get breakthrough points
            breakthrough = self.plateau_breaker.break_plateau(
                self.base_optimizer.get_best_params() 
                if hasattr(self.base_optimizer, 'get_best_params')
                else base_suggestions[0],
                metrics
            )
            
            # Log strategy
            print(f"[PlateauBreaker] Using strategies: {breakthrough['strategy']}")
            print(f"[PlateauBreaker] Adding {len(breakthrough['points'])} breakthrough points")
            
            # Combine base suggestions with breakthrough points
            combined = np.vstack([base_suggestions, breakthrough['points']])
            
            # Limit to requested number of points
            if len(combined) > n_points:
                # Prioritize breakthrough points
                n_breakthrough = min(n_points // 2, len(breakthrough['points']))
                n_base = n_points - n_breakthrough
                combined = np.vstack([
                    base_suggestions[:n_base],
                    breakthrough['points'][:n_breakthrough]
                ])
            
            return combined
        
        return base_suggestions
    
    def update(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Update optimizer with new observations.
        
        Args:
            X: Observed points
            y: Observed values
        """
        # Update base optimizer
        if hasattr(self.base_optimizer, 'update'):
            self.base_optimizer.update(X, y)
        
        # Update plateau breaker
        best_idx = np.argmin(y)
        best_score = y[best_idx]
        best_params = X[best_idx]
        
        # Get model metrics if available
        r2_score = None
        mae = None
        if hasattr(self.base_optimizer, 'get_model_metrics'):
            metrics = self.base_optimizer.get_model_metrics()
            r2_score = metrics.get('r2', None)
            mae = metrics.get('mae', None)
        
        self.plateau_breaker.update_history(best_score, best_params, r2_score, mae)
        self.iteration += 1
