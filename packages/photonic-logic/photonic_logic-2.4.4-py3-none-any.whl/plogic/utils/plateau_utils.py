"""
Plateau Breaking Utilities for Photonic Logic Optimization

Advanced utilities for breaking optimization plateaus including:
- Boundary reparameterization (unbounded ↔ bounded transforms)
- Dataset deduplication and jittering
- Normalization statistics tracking
- Trust region management
"""

import numpy as np
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class NormStats:
    """Statistics for normalizing objective components."""
    mu: float
    sigma: float


def sigmoid(z: np.ndarray) -> np.ndarray:
    """Numerically stable sigmoid function."""
    z = np.asarray(z, dtype=float)
    # Clip to prevent overflow
    z = np.clip(z, -500, 500)
    return 1.0 / (1.0 + np.exp(-z))


def z_to_x(z: np.ndarray, bounds: np.ndarray) -> np.ndarray:
    """
    Map unbounded z to bounded x via sigmoid transformation.
    
    This prevents parameters from sticking to boundaries by optimizing
    in unbounded space and mapping to bounded space.
    
    Args:
        z: Unbounded parameters
        bounds: Parameter bounds (n_params, 2)
        
    Returns:
        Bounded parameters in [a, b]
    """
    z = np.asarray(z, dtype=float)
    bounds = np.asarray(bounds, dtype=float)
    
    a, b = bounds[:, 0], bounds[:, 1]
    return a + (b - a) * sigmoid(z)


def x_to_z(x: np.ndarray, bounds: np.ndarray) -> np.ndarray:
    """
    Inverse map bounded x back to unbounded z.
    
    Args:
        x: Bounded parameters in [a, b]
        bounds: Parameter bounds (n_params, 2)
        
    Returns:
        Unbounded parameters
    """
    x = np.asarray(x, dtype=float)
    bounds = np.asarray(bounds, dtype=float)
    
    a, b = bounds[:, 0], bounds[:, 1]
    
    # Normalize to [0, 1]
    y = (x - a) / (b - a + 1e-12)
    
    # Clip to prevent numerical issues
    y = np.clip(y, 1e-9, 1 - 1e-9)
    
    # Inverse sigmoid (logit)
    return np.log(y) - np.log1p(-y)


def dedupe_with_jitter(X: np.ndarray, y: np.ndarray, 
                      tol: float = 1e-3) -> Tuple[np.ndarray, np.ndarray]:
    """
    Remove near-duplicate rows in X and add tiny jitter for numerical stability.
    
    This prevents surrogate models from overfitting to duplicate points
    and adds small perturbations to improve conditioning.
    
    Args:
        X: Input parameters (n_samples, n_dims)
        y: Objective values (n_samples,)
        tol: Tolerance for considering points duplicates
        
    Returns:
        Deduplicated and jittered (X, y)
    """
    if len(X) == 0:
        return X, y
    
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    
    # Hash with rounding to find duplicates
    rX = np.round(X / tol) * tol
    _, idx = np.unique(rX, axis=0, return_index=True)
    
    # Keep unique points
    Xu, yu = X[idx], y[idx]
    
    # Add small jitter to improve numerical conditioning
    rng = np.random.default_rng(42)
    jitter = rng.normal(size=Xu.shape) * tol * 0.1
    
    return Xu + jitter, yu


def compute_edge_penalty(x: np.ndarray, bounds: np.ndarray, 
                        weight: float = 1e-3, delta: float = 1.0) -> float:
    """
    Compute penalty for being too close to parameter boundaries.
    
    This encourages the optimizer to stay in the interior unless
    the boundary is truly optimal.
    
    Args:
        x: Parameter values
        bounds: Parameter bounds (n_params, 2)
        weight: Penalty weight
        delta: Offset to prevent division by zero
        
    Returns:
        Edge penalty value
    """
    x = np.asarray(x, dtype=float)
    bounds = np.asarray(bounds, dtype=float)
    
    a, b = bounds[:, 0], bounds[:, 1]
    
    # Penalty increases as we approach boundaries
    left_penalty = 1.0 / (x - a + delta)
    right_penalty = 1.0 / (b - x + delta)
    
    total_penalty = np.sum(left_penalty + right_penalty)
    
    return weight * total_penalty


def update_normalization_stats(values: List[float]) -> NormStats:
    """
    Compute normalization statistics from a list of values.
    
    Args:
        values: List of values to normalize
        
    Returns:
        Normalization statistics
    """
    if not values:
        return NormStats(0.0, 1.0)
    
    v = np.asarray(values, dtype=float)
    mu = float(np.nanmean(v))
    sigma = float(np.nanstd(v) + 1e-9)  # Prevent division by zero
    
    return NormStats(mu, sigma)


def normalize_value(value: float, stats: NormStats) -> float:
    """
    Normalize a value using provided statistics.
    
    Args:
        value: Value to normalize
        stats: Normalization statistics
        
    Returns:
        Normalized value
    """
    return (value - stats.mu) / stats.sigma


class TrustRegionManager:
    """
    Manages trust region for local optimization around promising points.
    
    The trust region expands when improvements are found and contracts
    when the local model is poor.
    """
    
    def __init__(self, bounds: np.ndarray, 
                 initial_width: float = 0.15,
                 min_width: float = 0.05,
                 max_width: float = 0.5,
                 expand_factor: float = 1.5,
                 contract_factor: float = 0.7):
        """
        Initialize trust region manager.
        
        Args:
            bounds: Parameter bounds (n_params, 2)
            initial_width: Initial trust region width as fraction of bounds
            min_width: Minimum trust region width
            max_width: Maximum trust region width
            expand_factor: Factor to expand trust region on success
            contract_factor: Factor to contract trust region on failure
        """
        self.bounds = np.asarray(bounds, dtype=float)
        self.dim = self.bounds.shape[0]
        self.initial_width = initial_width
        self.min_width = min_width
        self.max_width = max_width
        self.expand_factor = expand_factor
        self.contract_factor = contract_factor
        
        # State
        self._center = None
        self._width = None
        self._initialized = False
    
    def initialize(self, center: np.ndarray) -> None:
        """Initialize trust region around a center point."""
        self._center = np.asarray(center, dtype=float).copy()
        
        # Compute initial width based on bounds
        bound_ranges = self.bounds[:, 1] - self.bounds[:, 0]
        self._width = bound_ranges * self.initial_width
        
        self._initialized = True
    
    def get_bounds(self) -> np.ndarray:
        """
        Get current trust region bounds.
        
        Returns:
            Trust region bounds (n_params, 2)
        """
        if not self._initialized:
            return self.bounds.copy()
        
        # Compute trust region bounds
        a = np.maximum(self.bounds[:, 0], self._center - self._width)
        b = np.minimum(self.bounds[:, 1], self._center + self._width)
        
        return np.stack([a, b], axis=1)
    
    def update_center(self, new_center: np.ndarray) -> None:
        """Update trust region center."""
        if not self._initialized:
            self.initialize(new_center)
        else:
            self._center = np.asarray(new_center, dtype=float).copy()
    
    def adapt(self, improved: bool) -> None:
        """
        Adapt trust region size based on success/failure.
        
        Args:
            improved: Whether the last iteration improved the objective
        """
        if not self._initialized:
            return
        
        bound_ranges = self.bounds[:, 1] - self.bounds[:, 0]
        
        if improved:
            # Expand trust region
            self._width = np.minimum(
                self._width * self.expand_factor,
                bound_ranges * self.max_width
            )
        else:
            # Contract trust region
            self._width = np.maximum(
                self._width * self.contract_factor,
                bound_ranges * self.min_width
            )
    
    def get_width_fraction(self) -> np.ndarray:
        """Get current trust region width as fraction of bounds."""
        if not self._initialized:
            return np.full(self.dim, self.initial_width)
        
        bound_ranges = self.bounds[:, 1] - self.bounds[:, 0]
        return self._width / (bound_ranges + 1e-12)
    
    def is_initialized(self) -> bool:
        """Check if trust region is initialized."""
        return self._initialized


def generate_latin_hypercube(n_samples: int, bounds: np.ndarray, 
                           seed: Optional[int] = None) -> np.ndarray:
    """
    Generate Latin Hypercube samples within bounds.
    
    Args:
        n_samples: Number of samples to generate
        bounds: Parameter bounds (n_params, 2)
        seed: Random seed for reproducibility
        
    Returns:
        Latin Hypercube samples (n_samples, n_params)
    """
    bounds = np.asarray(bounds, dtype=float)
    n_params = bounds.shape[0]
    
    if seed is not None:
        np.random.seed(seed)
    
    # Generate LHS in [0, 1]^d
    samples = np.zeros((n_samples, n_params))
    
    for d in range(n_params):
        # Create evenly spaced intervals
        intervals = np.linspace(0, 1, n_samples + 1)
        
        # Random point within each interval
        for i in range(n_samples):
            samples[i, d] = np.random.uniform(intervals[i], intervals[i + 1])
    
    # Random permutation for each dimension
    for d in range(n_params):
        samples[:, d] = samples[np.random.permutation(n_samples), d]
    
    # Scale to bounds
    a, b = bounds[:, 0], bounds[:, 1]
    scaled_samples = a + (b - a) * samples
    
    return scaled_samples


def squared_hinge_penalty(value: float, threshold: float, 
                         weight: float = 1.0, epsilon: float = 0.02) -> float:
    """
    Compute squared hinge penalty for constraint violations.
    
    This creates a smooth penalty that is zero within epsilon of the
    threshold and grows quadratically beyond that.
    
    Args:
        value: Current value
        threshold: Constraint threshold
        weight: Penalty weight
        epsilon: Dead zone around threshold
        
    Returns:
        Penalty value
    """
    violation = max(0.0, value - (threshold + epsilon))
    return weight * (violation ** 2)
