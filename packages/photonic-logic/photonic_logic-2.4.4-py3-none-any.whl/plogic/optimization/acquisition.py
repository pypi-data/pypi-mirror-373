"""Enhanced acquisition functions for plateau breaking optimization."""
import numpy as np
from typing import Tuple, Optional, Union, List
from scipy.stats import norm
from plogic.opt_utils.array_safety import ensure_1d, ensure_2d_row


def pick_next(surrogate, X_grid):
    """Pick next point to evaluate using acquisition function.
    
    Args:
        surrogate: Surrogate model with predict method
        X_grid: Candidate points to evaluate
        
    Returns:
        Next point to evaluate as 2D array (1, d)
    """
    X_grid = np.asarray(X_grid, dtype=float)
    if X_grid.ndim == 1:  # single candidate
        X_grid = X_grid.reshape(1, -1)
    
    mu = surrogate.predict(X_grid, return_std=False)
    mu = ensure_1d(mu)
    
    best_idx = int(np.argmin(mu))
    x_next = ensure_2d_row(X_grid[best_idx])
    return x_next


def expected_improvement(X, surrogate, y_best, xi=0.01):
    """Calculate expected improvement acquisition function.
    
    Args:
        X: Points to evaluate
        surrogate: Surrogate model with predict method
        y_best: Best observed value so far
        xi: Exploration parameter
        
    Returns:
        Expected improvement values
    """
    X = ensure_2d_row(X)
    mu, std = surrogate.predict(X, return_std=True)
    mu = ensure_1d(mu)
    std = ensure_1d(std) if std is not None else np.ones_like(mu)
    
    # Prevent division by zero
    std = np.maximum(std, 1e-9)
    
    # Calculate EI
    improvement = y_best - mu - xi
    Z = improvement / std
    ei = improvement * norm.cdf(Z) + std * norm.pdf(Z)
    
    # Handle numerical issues
    ei[std < 1e-9] = 0.0
    
    return ensure_1d(ei)


def upper_confidence_bound(X, surrogate, kappa=2.0):
    """Calculate upper confidence bound acquisition function.
    
    Args:
        X: Points to evaluate
        surrogate: Surrogate model with predict method
        kappa: Exploration parameter
        
    Returns:
        UCB values (lower is better for minimization)
    """
    X = ensure_2d_row(X)
    mu, std = surrogate.predict(X, return_std=True)
    mu = ensure_1d(mu)
    std = ensure_1d(std) if std is not None else np.ones_like(mu)
    
    # For minimization, we want lower values
    ucb = mu - kappa * std
    
    return ensure_1d(ucb)


class AcquisitionScheduler:
    """
    Adaptive acquisition function scheduler for plateau breaking.
    
    Starts with high exploration (UCB) and gradually transitions to
    exploitation (EI) as the optimization progresses.
    """
    
    def __init__(self, 
                 start_kappa: float = 2.0,
                 end_kappa: float = 0.7,
                 warmup_iters: int = 6,
                 ei_xi: float = 0.1):
        """
        Initialize acquisition scheduler.
        
        Args:
            start_kappa: Initial UCB exploration parameter
            end_kappa: Final UCB exploration parameter
            warmup_iters: Number of iterations to use UCB before switching to EI
            ei_xi: EI exploration parameter
        """
        self.start_kappa = start_kappa
        self.end_kappa = end_kappa
        self.warmup_iters = warmup_iters
        self.ei_xi = ei_xi
    
    def select_acquisition(self, X: np.ndarray, surrogate, y_best: float, 
                          iter_idx: int) -> Tuple[np.ndarray, str]:
        """
        Select appropriate acquisition function based on iteration.
        
        Args:
            X: Candidate points
            surrogate: Surrogate model
            y_best: Best observed value
            iter_idx: Current iteration index
            
        Returns:
            Tuple of (acquisition_values, strategy_name)
        """
        if iter_idx < self.warmup_iters:
            # UCB phase with decaying kappa
            frac = iter_idx / max(1, self.warmup_iters - 1)
            kappa = self.start_kappa + frac * (self.end_kappa - self.start_kappa)
            acq_vals = upper_confidence_bound(X, surrogate, kappa)
            return acq_vals, f"ucb_k{kappa:.2f}"
        else:
            # EI phase
            acq_vals = expected_improvement(X, surrogate, y_best, self.ei_xi)
            return acq_vals, f"ei_xi{self.ei_xi}"


def batch_q_ei(candidates: np.ndarray, surrogate, y_best: float, 
               q: int = 6, method: str = "greedy") -> np.ndarray:
    """
    Select a batch of points using quasi-Expected Improvement.
    
    This implements a greedy approximation to q-EI that selects
    points sequentially to maximize diversity and expected improvement.
    
    Args:
        candidates: Candidate points to select from (n_candidates, n_dims)
        surrogate: Surrogate model
        y_best: Best observed value so far
        q: Number of points to select
        method: Selection method ("greedy" or "diverse")
        
    Returns:
        Selected batch of points (q, n_dims)
    """
    candidates = ensure_2d_row(candidates)
    q = min(q, len(candidates))
    
    if q == 1:
        # Single point selection
        ei_vals = expected_improvement(candidates, surrogate, y_best)
        best_idx = int(np.argmax(ei_vals))
        return candidates[best_idx:best_idx+1]
    
    if method == "greedy":
        return _greedy_batch_selection(candidates, surrogate, y_best, q)
    elif method == "diverse":
        return _diverse_batch_selection(candidates, surrogate, y_best, q)
    else:
        raise ValueError(f"Unknown batch selection method: {method}")


def _greedy_batch_selection(candidates: np.ndarray, surrogate, 
                           y_best: float, q: int) -> np.ndarray:
    """Greedy batch selection based on EI values."""
    selected = []
    remaining = candidates.copy()
    
    for _ in range(q):
        if len(remaining) == 0:
            break
            
        # Compute EI for remaining candidates
        ei_vals = expected_improvement(remaining, surrogate, y_best)
        
        # Select best candidate
        best_idx = int(np.argmax(ei_vals))
        selected.append(remaining[best_idx])
        
        # Remove selected candidate
        remaining = np.delete(remaining, best_idx, axis=0)
    
    return np.array(selected)


def _diverse_batch_selection(candidates: np.ndarray, surrogate,
                            y_best: float, q: int) -> np.ndarray:
    """Diverse batch selection balancing EI and distance."""
    selected = []
    remaining = candidates.copy()
    
    # Select first point with highest EI
    ei_vals = expected_improvement(remaining, surrogate, y_best)
    best_idx = int(np.argmax(ei_vals))
    selected.append(remaining[best_idx])
    remaining = np.delete(remaining, best_idx, axis=0)
    
    # Select remaining points balancing EI and diversity
    for _ in range(q - 1):
        if len(remaining) == 0:
            break
        
        # Compute EI for remaining candidates
        ei_vals = expected_improvement(remaining, surrogate, y_best)
        ei_vals = (ei_vals - np.min(ei_vals)) / (np.max(ei_vals) - np.min(ei_vals) + 1e-12)
        
        # Compute minimum distance to selected points
        selected_array = np.array(selected)
        min_distances = np.array([
            np.min(np.linalg.norm(remaining - sel, axis=1))
            for sel in selected_array
        ])
        min_dist = np.min(min_distances, axis=0)
        min_dist = (min_dist - np.min(min_dist)) / (np.max(min_dist) - np.min(min_dist) + 1e-12)
        
        # Combined score (balance EI and diversity)
        combined_score = 0.7 * ei_vals + 0.3 * min_dist
        
        # Select best candidate
        best_idx = int(np.argmax(combined_score))
        selected.append(remaining[best_idx])
        remaining = np.delete(remaining, best_idx, axis=0)
    
    return np.array(selected)


def probability_of_improvement(X, surrogate, y_best, xi=0.01):
    """
    Calculate probability of improvement acquisition function.
    
    Args:
        X: Points to evaluate
        surrogate: Surrogate model
        y_best: Best observed value so far
        xi: Exploration parameter
        
    Returns:
        Probability of improvement values
    """
    X = ensure_2d_row(X)
    mu, std = surrogate.predict(X, return_std=True)
    mu = ensure_1d(mu)
    std = ensure_1d(std) if std is not None else np.ones_like(mu)
    
    # Prevent division by zero
    std = np.maximum(std, 1e-9)
    
    # Calculate PI
    improvement = y_best - mu - xi
    Z = improvement / std
    pi = norm.cdf(Z)
    
    return ensure_1d(pi)


def entropy_search(X, surrogate, y_best, n_samples=1000):
    """
    Entropy-based acquisition function for global optimization.
    
    This is a simplified version that approximates the information gain.
    
    Args:
        X: Points to evaluate
        surrogate: Surrogate model
        y_best: Best observed value so far
        n_samples: Number of samples for entropy estimation
        
    Returns:
        Entropy search values
    """
    X = ensure_2d_row(X)
    mu, std = surrogate.predict(X, return_std=True)
    mu = ensure_1d(mu)
    std = ensure_1d(std) if std is not None else np.ones_like(mu)
    
    # Prevent division by zero
    std = np.maximum(std, 1e-9)
    
    # Approximate entropy as uncertainty weighted by improvement probability
    pi = probability_of_improvement(X, surrogate, y_best)
    entropy = pi * std
    
    return ensure_1d(entropy)
