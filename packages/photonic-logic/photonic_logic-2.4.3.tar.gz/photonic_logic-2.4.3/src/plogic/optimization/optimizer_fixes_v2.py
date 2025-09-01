"""
Critical fixes for the photonic accelerator optimizer (Version 2).
Implements best score tracking, surrogate stability, and proper metrics.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Any, Tuple, Optional, Callable, List
from pathlib import Path
import datetime
from sklearn.model_selection import KFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score


@dataclass
class BestState:
    """Track the best solution found during optimization."""
    score: float = float("inf")
    x: Optional[np.ndarray] = None
    power_W: float = float("inf")
    tops: float = 0.0
    yield_factor: float = 0.0
    iteration: int = 0
    metrics: Dict[str, Any] = field(default_factory=dict)


def safe_mape(y_true: np.ndarray, y_pred: np.ndarray, eps: float = 1e-6) -> float:
    """
    Calculate Mean Absolute Percentage Error safely.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        eps: Small epsilon to avoid division by zero
    
    Returns:
        MAPE in percentage
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    
    # Avoid division by zero
    denom = np.clip(np.abs(y_true), eps, None)
    
    # Calculate MAPE
    mape = float(np.mean(np.abs((y_true - y_pred) / denom)) * 100.0)
    
    return mape


def build_robust_surrogate(n_features: int, use_neural: bool = True):
    """
    Build a robust surrogate model with fallback.
    
    Args:
        n_features: Number of input features
        use_neural: Whether to try neural network first
    
    Returns:
        Fit function that returns trained model and metrics
    """
    def _cv_r2(model, X, y):
        """Calculate cross-validated R² score."""
        cv = KFold(n_splits=min(5, len(X)), shuffle=True, random_state=42)
        scores = cross_val_score(model, X, y, cv=cv, scoring="r2")
        return float(np.mean(scores))
    
    def fit(X: np.ndarray, y: np.ndarray) -> Tuple[Any, Dict[str, float]]:
        """
        Fit surrogate model with automatic fallback.
        
        Args:
            X: Input features
            y: Target values
        
        Returns:
            Tuple of (fitted_model, metrics_dict)
        """
        # Start with RandomForest as it's more stable
        pipe = make_pipeline(
            StandardScaler(with_mean=True, with_std=True),
            RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
        )
        
        # Calculate CV score
        try:
            cv_r2 = _cv_r2(pipe, X, y)
        except:
            cv_r2 = -1.0
        
        # Fit the model
        pipe.fit(X, y)
        yhat = pipe.predict(X)
        
        # Calculate metrics
        train_r2 = r2_score(y, yhat)
        train_mape = safe_mape(y, yhat)
        
        metrics = {
            "cv_r2": cv_r2,
            "train_r2": train_r2,
            "train_mape": train_mape,
            "model_type": "RandomForest"
        }
        
        # Print metrics for debugging
        print(f"Surrogate: CV R²={cv_r2:.3f}, Train R²={train_r2:.3f}, MAPE={train_mape:.1f}%")
        
        return pipe, metrics
    
    return fit


def add_exploration_noise(
    x: np.ndarray,
    iter_idx: int,
    max_iters: int,
    rng: np.random.Generator,
    bounds: Tuple[np.ndarray, np.ndarray],
    discrete_idx: Tuple[int, ...] = ()
) -> np.ndarray:
    """
    Add exploration noise with cosine annealing schedule.
    
    Args:
        x: Current solution
        iter_idx: Current iteration
        max_iters: Maximum iterations
        rng: Random number generator
        bounds: (lower_bounds, upper_bounds)
        discrete_idx: Indices of discrete variables
    
    Returns:
        Solution with exploration noise added
    """
    # Cosine annealing: more noise early, less late
    scale = 0.15 * (1 + np.cos(np.pi * iter_idx / max_iters)) / 2
    
    # Add Gaussian noise
    noise = rng.normal(0.0, scale, size=x.shape)
    x_new = np.clip(x + noise, bounds[0], bounds[1])
    
    # Don't snap discrete dimensions during exploration
    # Only snap at final evaluation
    
    return x_new


def expected_improvement(
    mu: np.ndarray,
    sigma: np.ndarray,
    best_y: float,
    xi: float = 0.01
) -> np.ndarray:
    """
    Calculate Expected Improvement acquisition function.
    
    Args:
        mu: Predicted mean
        sigma: Predicted standard deviation
        best_y: Best value found so far
        xi: Exploration parameter
    
    Returns:
        Expected improvement values
    """
    from scipy.stats import norm
    
    # Calculate improvement
    imp = best_y - mu - xi
    
    # Avoid division by zero
    sigma_safe = sigma + 1e-9
    
    # Calculate Z-score
    Z = imp / sigma_safe
    
    # Calculate EI
    ei = imp * norm.cdf(Z) + sigma_safe * norm.pdf(Z)
    
    return ei


def run_optimization_with_fixes(
    objective_func: Callable,
    bounds: Tuple[np.ndarray, np.ndarray],
    n_iterations: int = 100,
    initial_samples: int = 20,
    use_fallback: bool = False
) -> Tuple[np.ndarray, float, List[Dict]]:
    """
    Run optimization with proper best score tracking (simplified version).
    
    Args:
        objective_func: Function to minimize
        bounds: (lower_bounds, upper_bounds)
        n_iterations: Number of iterations
        initial_samples: Number of initial random samples
        use_fallback: Use simple random search instead of sophisticated methods
    
    Returns:
        Tuple of (best_x, best_score, history)
    """
    lb, ub = bounds
    ndim = len(lb)
    
    # Initialize
    best_x = None
    best_score = float('inf')
    history = []
    
    # Generate initial samples
    X = []
    y = []
    
    for i in range(initial_samples):
        x = np.random.uniform(lb, ub)
        score = objective_func(x)
        X.append(x)
        y.append(score)
        
        if score < best_score:
            best_score = score
            best_x = x.copy()
        
        history.append({
            'iteration': i,
            'score': score,
            'best_score': best_score
        })
    
    # Continue with random search or more sophisticated method
    for i in range(initial_samples, n_iterations):
        if use_fallback or i % 10 == 0:
            # Random exploration
            x = np.random.uniform(lb, ub)
        else:
            # Small perturbation from best
            if best_x is not None:
                x = best_x + np.random.normal(0, 0.1, size=ndim)
                x = np.clip(x, lb, ub)
            else:
                x = np.random.uniform(lb, ub)
        
        score = objective_func(x)
        X.append(x)
        y.append(score)
        
        if score < best_score:
            best_score = score
            best_x = x.copy()
            print(f"New best at iteration {i}: score={best_score:.4f}")
        
        history.append({
            'iteration': i,
            'score': score,
            'best_score': best_score
        })
    
    return best_x, best_score, history


def create_unique_run_dir(base_dir: str = "photonic_accelerator", run_id: Optional[str] = None) -> Path:
    """
    Create a unique run directory with timestamp.
    
    Args:
        base_dir: Base directory name
        run_id: Optional run ID to append
    
    Returns:
        Path to the created directory
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if run_id:
        run_dir = Path(f"{base_dir}_{run_id}_{timestamp}")
    else:
        run_dir = Path(f"{base_dir}_{timestamp}")
    
    # Ensure unique
    counter = 1
    while run_dir.exists():
        if run_id:
            run_dir = Path(f"{base_dir}_{run_id}_{timestamp}_{counter}")
        else:
            run_dir = Path(f"{base_dir}_{timestamp}_{counter}")
        counter += 1
    
    # Create directory
    run_dir.mkdir(parents=True, exist_ok=False)
    
    return run_dir


def print_architecture_totals(
    rows: int,
    cols: int,
    lanes: int,
    array_scope: str = "global",
    power_breakdown: Optional[Dict[str, float]] = None
) -> None:
    """
    Print detailed architecture totals and power breakdown.
    
    Args:
        rows: Ring array rows
        cols: Ring array columns
        lanes: Number of lanes
        array_scope: "global" or "per_lane"
        power_breakdown: Optional power breakdown dict
    """
    from .physics_validation import tops_from_spec
    
    # Calculate TOPS with default values
    tops, total_rings = tops_from_spec(
        rows=rows,
        cols=cols,
        lanes=lanes,
        macs_per_ring=2,
        clock_ghz=1.0,
        utilization=1.0,
        array_scope=array_scope
    )
    
    print("\n" + "="*60)
    print("ARCHITECTURE TOTALS")
    print("="*60)
    print(f"Ring Array: {rows}×{cols} = {rows*cols} rings")
    print(f"Array Scope: {array_scope}")
    print(f"Total Rings: {total_rings:,} {'(global)' if array_scope=='global' else '('+str(lanes)+' lanes)'}")
    
    if power_breakdown:
        print(f"\nPower Breakdown:")
        for key, value in power_breakdown.items():
            if key != "total_W":
                print(f"  {key:12s}: {value:.3f} W")
        print(f"  ────────────────")
        print(f"  {'total_W':12s}: {power_breakdown.get('total_W', 0):.3f} W")
    
    print(f"\nPerformance:")
    print(f"  Throughput: {tops:.2f} TOPS (at 1.0 GHz)")
    if power_breakdown and power_breakdown.get('total_W', 0) > 0:
        print(f"  Efficiency: {tops/power_breakdown['total_W']:.2f} TOPS/W")
    print("="*60 + "\n")


def fix_keras_model(n_features: int):
    """
    Create Keras model with explicit Input layer to fix warning.
    
    Args:
        n_features: Number of input features
    
    Returns:
        Compiled Keras model
    """
    from tensorflow.keras import Sequential, Input
    from tensorflow.keras.layers import Dense, Dropout
    
    model = Sequential([
        Input(shape=(n_features,)),
        Dense(128, activation="relu"),
        Dropout(0.1),
        Dense(64, activation="relu"),
        Dropout(0.1),
        Dense(32, activation="relu"),
        Dense(1)
    ])
    
    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    
    return model
