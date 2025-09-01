"""
Optimization utilities for safe array operations and robust surrogate models.
Prevents crashes with tiny datasets and provides fallback models.
Enhanced with bulletproof array safety utilities.
"""

import numpy as np
from typing import Union, Optional, Dict, Any

# Import enhanced array safety utilities
from ..opt_utils.array_safety import ensure_1d, ensure_2d_row, safe_last_n, safe_topk_indices
from ..optimization.bounds import BOUNDS, sanitize_config, sanitize_best_params, validate_bounds

# Legacy constants for backward compatibility
EPS = 1e-6


# Legacy wrapper functions for backward compatibility
def last_n(arr: Union[list, np.ndarray], n: int) -> Union[list, np.ndarray]:
    """Legacy wrapper for safe_last_n."""
    return safe_last_n(arr, n)


def safe_slice(arr: Union[list, np.ndarray], start: int, end: Optional[int] = None) -> Union[list, np.ndarray]:
    """
    Safely slice array with bounds checking.
    
    Args:
        arr: Array to slice
        start: Start index (can be negative)
        end: End index (optional)
        
    Returns:
        Safely sliced array
    """
    if len(arr) == 0:
        return arr[:0]
    
    n = len(arr)
    
    # Handle negative start index
    if start < 0:
        start = max(0, n + start)
    else:
        start = min(start, n)
    
    # Handle end index
    if end is None:
        end = n
    elif end < 0:
        end = max(start, n + end)
    else:
        end = min(end, n)
    
    return arr[start:end]


class SklearnSurrogateWrapper:
    """Wrapper to make sklearn models compatible with DANTE interface."""
    
    def __init__(self, model):
        self.model = model
        self.is_fitted = False
    
    def __call__(self, X, y):
        """Train the model and return self for DANTE compatibility."""
        self.model.fit(X, y)
        self.is_fitted = True
        return self
    
    def predict(self, X, return_std=False, **kwargs):
        """
        Predict using the trained model with DANTE compatibility.
        
        Args:
            X: Input features (may be 2D or 3D from DANTE)
            return_std: Whether to return uncertainty estimates
            **kwargs: Additional arguments (e.g., verbose) - ignored gracefully
            
        Returns:
            Predictions, optionally with uncertainty estimates
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Handle DANTE's 3D input format (reshape to 2D for sklearn)
        X_input = np.array(X)
        if X_input.ndim == 3:
            # DANTE format: (n_samples, n_features, 1) -> (n_samples, n_features)
            X_input = X_input.squeeze(-1)
        elif X_input.ndim == 1:
            # Single sample: (n_features,) -> (1, n_features)
            X_input = X_input.reshape(1, -1)
        
        # Check if underlying model supports return_std
        try:
            from inspect import signature, Parameter
            sig = signature(self.model.predict)
            params = sig.parameters
            supports_return_std = ("return_std" in params and
                                 params["return_std"].kind in
                                 (Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY))
        except Exception:
            supports_return_std = False
        
        # Filter kwargs to only those the model accepts
        try:
            sig = signature(self.model.predict)
            valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        except Exception:
            valid_kwargs = {}
        
        if supports_return_std:
            result = self.model.predict(X_input, return_std=return_std, **valid_kwargs)
            # Ensure array outputs
            if return_std:
                yhat, std = result
                yhat = ensure_1d(yhat)
                std = ensure_1d(std)
                return yhat, std
            else:
                return ensure_1d(result)
        else:
            # Tree models don't support return_std
            yhat = self.model.predict(X_input, **valid_kwargs)
            yhat = ensure_1d(yhat)  # Force array output, prevent scalar issues
            if return_std:
                # Provide dummy constant std for compatibility
                std = np.full_like(yhat, fill_value=0.1, dtype=float)
                return yhat, std
            return yhat


def build_robust_surrogate(n_samples: int, input_dims: int):
    """
    Build surrogate model appropriate for dataset size.
    
    Args:
        n_samples: Number of training samples
        input_dims: Input dimensionality
        
    Returns:
        Appropriate surrogate model for the dataset size
    """
    if n_samples < 20:
        # Use tree-based model for tiny datasets
        from sklearn.ensemble import ExtraTreesRegressor
        model = ExtraTreesRegressor(
            n_estimators=min(300, max(50, n_samples * 10)),
            random_state=42,
            min_samples_split=2,
            min_samples_leaf=1,
            bootstrap=False,
            max_features="sqrt"
        )
        return SklearnSurrogateWrapper(model)
    else:
        # Use neural network for larger datasets
        try:
            from dante.neural_surrogate import AckleySurrogateModel
            return AckleySurrogateModel(input_dims=input_dims, epochs=20)
        except ImportError:
            # Fallback to ExtraTrees if DANTE not available
            from sklearn.ensemble import ExtraTreesRegressor
            model = ExtraTreesRegressor(
                n_estimators=300,
                random_state=42,
                min_samples_split=2,
                min_samples_leaf=1,
                bootstrap=False
            )
            return SklearnSurrogateWrapper(model)


def add_exploration_noise(y: np.ndarray, noise_scale: float = 0.01, min_noise: float = 1e-6) -> np.ndarray:
    """
    Add small exploration noise to break ties in target values.
    
    Args:
        y: Target values
        noise_scale: Scale of noise relative to std(y)
        min_noise: Minimum absolute noise level
        
    Returns:
        Target values with small noise added
    """
    if len(y) == 0:
        return y
    
    std_y = np.std(y)
    noise_level = max(min_noise, noise_scale * std_y)
    
    rng = np.random.default_rng(42)  # Fixed seed for reproducibility
    noise = rng.normal(0, noise_level, size=len(y))
    
    return y + noise


def safe_convergence_check(values: np.ndarray, window: int = 5, tolerance: float = 1e-6) -> bool:
    """
    Safely check for convergence without array bounds errors.
    
    Args:
        values: Array of optimization values
        window: Number of recent values to check
        tolerance: Convergence tolerance
        
    Returns:
        True if converged, False otherwise
    """
    if len(values) < window:
        return False
    
    recent = last_n(values, window)
    if len(recent) < 2:
        return False
    
    # Check if recent values are within tolerance
    return np.std(recent) < tolerance


def ensure_1d(a) -> np.ndarray:
    """Guarantee a 1D array even if a is a scalar."""
    a = np.asarray(a)
    return a.reshape(1,) if a.ndim == 0 else a.ravel()


def ensure_2d_row(x) -> np.ndarray:
    """Guarantee shape (1, d) for single-candidate points."""
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        return x.reshape(1, -1)
    if x.ndim == 2:
        return x
    return x.reshape(1, -1)


def safe_last_n(arr, n: int):
    """Safely get last n elements with scalar protection."""
    v = ensure_1d(arr)
    n = max(0, min(n, v.shape[0]))
    return v[-n:] if n else v[:0]


def safe_topk_indices_enhanced(values, k: int) -> np.ndarray:
    """Enhanced safe top-k with scalar protection."""
    v = ensure_1d(values)
    n = v.shape[0]
    if n == 0:
        return np.array([], dtype=int)
    k = max(1, min(k, n))
    if k == 1:
        return np.array([np.argmax(v)])
    part = np.argpartition(v, k-1)[:k]
    return part[np.argsort(v[part])]


def sanitize_config(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize configuration parameters to valid bounds.
    
    Args:
        cfg: Configuration dictionary
        
    Returns:
        Sanitized configuration with valid parameter values
    """
    sanitized = cfg.copy()
    
    # Float parameters
    if "pulse_ns" in sanitized:
        sanitized["pulse_ns"] = float(np.clip(sanitized["pulse_ns"], *BOUNDS["pulse_ns"]))
    if "P_high_mW" in sanitized:
        sanitized["P_high_mW"] = float(np.clip(sanitized["P_high_mW"], *BOUNDS["P_high_mW"]))
    if "coupling" in sanitized:
        sanitized["coupling"] = float(np.clip(sanitized["coupling"], *BOUNDS["coupling"]))
    if "link_um" in sanitized:
        sanitized["link_um"] = float(np.clip(sanitized["link_um"], *BOUNDS["link_um"]))
    if "split_loss_db" in sanitized:
        sanitized["split_loss_db"] = float(np.clip(sanitized["split_loss_db"], *BOUNDS["split_loss_db"]))
    
    # Integer parameters
    if "fanout" in sanitized:
        sanitized["fanout"] = int(np.clip(int(round(sanitized["fanout"])), *BOUNDS["fanout"]))
    if "stages" in sanitized:
        sanitized["stages"] = int(np.clip(int(round(sanitized["stages"])), *BOUNDS["stages"]))
    
    return sanitized


def sanitize_best_params(best_params: np.ndarray) -> Dict[str, Any]:
    """
    Sanitize best parameters array for display.
    
    Args:
        best_params: Parameter array from optimization
        
    Returns:
        Sanitized parameter dictionary
    """
    if len(best_params) < 8:
        return {}
    
    # Map array indices to parameter names
    param_map = {
        1: "P_high_mW",
        2: "pulse_ns", 
        3: "coupling",
        4: "link_um",
        5: "fanout",
        6: "split_loss_db",
        7: "stages"
    }
    
    cfg = {}
    for idx, param_name in param_map.items():
        if idx < len(best_params):
            cfg[param_name] = best_params[idx]
    
    return sanitize_config(cfg)


def validate_bounds(x: np.ndarray, lb: np.ndarray, ub: np.ndarray) -> np.ndarray:
    """
    Validate and clip parameters to bounds.
    
    Args:
        x: Parameter vector
        lb: Lower bounds
        ub: Upper bounds
        
    Returns:
        Clipped parameter vector
    """
    return np.clip(x, lb, ub)
