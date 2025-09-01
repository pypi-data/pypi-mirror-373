"""
Reproducibility utilities for consistent optimization results.
Ensures deterministic behavior across runs and platforms.
"""

import os
import random
import numpy as np


def set_global_seed(seed: int = 42):
    """
    Set global random seed for reproducible results.
    
    Args:
        seed: Random seed value (default: 42)
    """
    # Python hash seed (must be set before import)
    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    
    # Python random
    random.seed(seed)
    
    # NumPy random
    np.random.seed(seed)
    
    # TensorFlow random (if available)
    try:
        import tensorflow as tf
        tf.random.set_seed(seed)
    except ImportError:
        pass
    
    # PyTorch random (if available)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


def quiet_tensorflow_logs():
    """
    Suppress noisy TensorFlow/oneDNN log messages.
    """
    # Suppress TensorFlow info/warning messages
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")  # 0=ALL, 1=INFO, 2=WARNING, 3=ERROR
    
    # Suppress oneDNN optimization messages
    os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
    
    # Additional TensorFlow logging control
    try:
        import tensorflow as tf
        tf.get_logger().setLevel('ERROR')
    except ImportError:
        pass


def setup_reproducible_environment(seed: int = 42):
    """
    Set up reproducible environment with quiet logging.
    
    Args:
        seed: Random seed value (default: 42)
    """
    quiet_tensorflow_logs()
    set_global_seed(seed)
