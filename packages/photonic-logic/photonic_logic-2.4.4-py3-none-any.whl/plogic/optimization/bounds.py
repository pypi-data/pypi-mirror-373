"""Bounds management and sanitization for optimization."""
import numpy as np


# Physical bounds for photonic system parameters
BOUNDS = {
    "pulse_ns": (0.05, 10.0),
    "P_high_mW": (0.01, 5.0),
    "coupling": (0.05, 2.5),
    "link_um": (0.2, 200.0),
    "split_loss_db": (0.0, 3.0),
    "fanout": (1, 32),   # ints
    "stages": (8, 24),   # ints - aligned with cascade penalty system
}


def decode_parameters(params):
    """Decode raw optimization parameters to configuration dictionary.
    
    Args:
        params: Array of raw parameters from optimizer
        
    Returns:
        Configuration dictionary with named parameters
    """
    # Handle both array and list inputs
    params = np.asarray(params)
    
    # Basic decoding for 8-dimensional optimization
    config = {}
    
    # Platform selection (first parameter)
    platforms = ["AlGaAs", "Si", "SiN"]
    platform_idx = int(np.clip(params[0], 0, 2))
    config["platform"] = platforms[platform_idx]
    
    # Map remaining parameters
    if len(params) >= 8:
        config["P_high_mW"] = float(np.clip(params[1], *BOUNDS["P_high_mW"]))
        config["pulse_ns"] = float(np.clip(params[2], *BOUNDS["pulse_ns"]))
        config["coupling"] = float(np.clip(params[3], *BOUNDS["coupling"]))
        config["link_um"] = float(np.clip(params[4], *BOUNDS["link_um"]))
        config["fanout"] = int(np.clip(params[5], *BOUNDS["fanout"]))
        config["split_loss_db"] = float(np.clip(params[6], *BOUNDS["split_loss_db"]))
        config["stages"] = int(np.clip(params[7], *BOUNDS["stages"]))
    
    return config


def sanitize_config(cfg):
    """Sanitize configuration to ensure physical validity.
    
    Args:
        cfg: Configuration dictionary
        
    Returns:
        Sanitized configuration dictionary
    """
    # Create a copy to avoid modifying the original
    cfg = cfg.copy()
    
    # Apply bounds with proper type conversion
    if "pulse_ns" in cfg:
        cfg["pulse_ns"] = float(np.clip(cfg["pulse_ns"], *BOUNDS["pulse_ns"]))
    
    if "P_high_mW" in cfg:
        cfg["P_high_mW"] = float(np.clip(cfg["P_high_mW"], *BOUNDS["P_high_mW"]))
    
    if "coupling" in cfg:
        cfg["coupling"] = float(np.clip(cfg["coupling"], *BOUNDS["coupling"]))
    
    if "link_um" in cfg:
        cfg["link_um"] = float(np.clip(cfg["link_um"], *BOUNDS["link_um"]))
    
    if "split_loss_db" in cfg:
        cfg["split_loss_db"] = float(np.clip(cfg["split_loss_db"], *BOUNDS["split_loss_db"]))
    
    if "fanout" in cfg:
        cfg["fanout"] = int(np.clip(int(round(cfg["fanout"])), *BOUNDS["fanout"]))
    
    if "stages" in cfg:
        cfg["stages"] = int(np.clip(int(round(cfg["stages"])), *BOUNDS["stages"]))
    
    return cfg


def get_bounds_array(param_names):
    """Get bounds array for given parameter names.
    
    Args:
        param_names: List of parameter names
        
    Returns:
        Array of shape (n_params, 2) with min/max bounds
    """
    bounds_list = []
    for name in param_names:
        if name in BOUNDS:
            bounds_list.append(BOUNDS[name])
        else:
            # Default bounds for unknown parameters
            bounds_list.append((0.0, 1.0))
    
    return np.array(bounds_list)


def clip_to_bounds(X, param_names):
    """Clip values to parameter bounds.
    
    Args:
        X: Array of parameter values (n_samples, n_params)
        param_names: List of parameter names
        
    Returns:
        Clipped array
    """
    X = np.asarray(X)
    if X.ndim == 1:
        X = X.reshape(1, -1)
    
    bounds = get_bounds_array(param_names)
    X_clipped = np.clip(X, bounds[:, 0], bounds[:, 1])
    
    # Handle integer parameters
    for i, name in enumerate(param_names):
        if name in ["fanout", "stages"]:
            X_clipped[:, i] = np.round(X_clipped[:, i])
    
    return X_clipped


def sanitize_best_params(best_params):
    """Sanitize best parameters array for display.
    
    Args:
        best_params: Parameter array from optimization
        
    Returns:
        Sanitized parameter dictionary
    """
    if len(best_params) < 8:
        return {}
    
    # Map array indices to parameter names for 8-dimensional optimization
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


def validate_bounds(x, lb, ub):
    """Validate and clip parameters to bounds.
    
    Args:
        x: Parameter vector
        lb: Lower bounds
        ub: Upper bounds
        
    Returns:
        Clipped parameter vector
    """
    return np.clip(x, lb, ub)
