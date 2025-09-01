"""
Critical fixes for the photonic accelerator optimizer.
Implements best score tracking, surrogate stability, and proper metrics.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Any, Tuple, Optional, Callable
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
    evaluator: Callable,
    suggest: Callable,
    n_iters: int,
    run_dir: Path,
    seed: int = 42,
    verbose: bool = True
) -> Tuple[BestState, list]:
    """
    Run optimization with proper best score tracking.
    
    Args:
        evaluator: Function to evaluate solutions
        suggest: Function to suggest new solutions
        n_iters: Number of iterations
        run_dir: Directory for outputs
        seed: Random seed
        verbose: Print progress
    
    Returns:
        Tuple of (best_state, history)
    """
    rng = np.random.default_rng(seed)
    best = BestState()
    history = []
    
    for i in range(n_iters):
        # Get new candidate
        x = suggest(best, i, n_iters, rng)
        
        # Evaluate
        score, metrics = evaluator(x)
        
        # Extract key metrics
        power_W = float(metrics.get("power_W", metrics.get("total_power_W", np.inf)))
        tops = float(metrics.get("tops", metrics.get("sustained_tops", 0)))
        yield_factor = float(metrics.get("yield_factor", 0))
        
        # Update best if improved (minimization)
        if score < best.score:
            best = BestState(
                score=score,
                x=x.copy(),
                power_W=power_W,
                tops=tops,
                yield_factor=yield_factor,
                iteration=i + 1,
                metrics=metrics.copy()
            )
        
        # Record history
        history.append({
            "iteration": i + 1,
            "current_score": score,
            "best_score": best.score,
            "current_power_W": power_W,
            "current_tops": tops,
            "best_power_W": best.power_W,
            "best_tops": best.tops
        })
        
        # Print progress with CORRECT best tracking
        if verbose:
            print(f"Iter {i+1}/{n_iters}: "
                  f"current={score:.4f} best={best.score:.4f} "
                  f"power={power_W:.2f}W tops={tops:.2f} "
                  f"(best: {best.power_W:.2f}W {best.tops:.2f}TOPS)")
    
    return best, history


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
    heater_uW: float,
    laser_W: float,
    dsp_W: float,
    clock_ghz: float,
    array_scope: str = "global",
    active_fraction: float = 0.8,
    utilization: float = 0.7
) -> None:
    """
    Print detailed architecture totals and power breakdown.
    
    Args:
        rows: Ring array rows
        cols: Ring array columns
        lanes: Number of lanes
        heater_uW: Heater power per ring (microWatts)
        laser_W: Laser power (Watts)
        dsp_W: DSP/SRAM power (Watts)
        clock_ghz: Clock frequency (GHz)
        array_scope: "global" or "per_lane"
        active_fraction: Fraction of active rings
        utilization: System utilization
    """
    from .physics_validation import tops_from_spec, power_breakdown
    
    # Calculate TOPS
    tops, total_rings = tops_from_spec(
        rows=rows,
        cols=cols,
        lanes=lanes,
        macs_per_ring=2,
        clock_ghz=clock_ghz,
        utilization=utilization,
        array_scope=array_scope
    )
    
    # Calculate power
    pb = power_breakdown(
        heater_uW_per_ring=heater_uW,
        active_fraction=active_fraction,
        total_rings=total_rings,
        laser_W=laser_W,
        dsp_sram_W=dsp_W,
        misc_W=0.1
    )
    
    print("\n" + "="*60)
    print("ARCHITECTURE TOTALS")
    print("="*60)
    print(f"Ring Array: {rows}×{cols} = {rows*cols} rings")
    print(f"Array Scope: {array_scope}")
    print(f"Total Rings: {total_rings:,} {'(global)' if array_scope=='global' else '('+str(lanes)+' lanes)'}")
    print(f"Active Rings: {pb['active_rings']:,} ({active_fraction:.0%})")
    
    print(f"\nPower Breakdown:")
    print(f"  Heaters : {pb['heaters_W']:.3f} W ({pb['active_rings']:,} × {heater_uW:.1f} µW)")
    print(f"  Lasers  : {pb['laser_W']:.3f} W")
    print(f"  DSP/SRAM: {pb['dsp_sram_W']:.3f} W")
    print(f"  Misc    : {pb['misc_W']:.3f} W")
    print(f"  ────────────────")
    print(f"  TOTAL   : {pb['total_W']:.3f} W")
    
    print(f"\nPerformance:")
    print(f"  Clock: {clock_ghz:.2f} GHz")
    print(f"  Utilization: {utilization:.0%}")
    print(f"  Throughput: {tops:.2f} TOPS")
    print(f"  Efficiency: {tops/pb['total_W']:.2f} TOPS/W")
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
