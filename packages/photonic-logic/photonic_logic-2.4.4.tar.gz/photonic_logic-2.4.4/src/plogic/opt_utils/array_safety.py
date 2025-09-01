"""Array safety utilities for robust optimization."""
import numpy as np


def ensure_1d(a):
    """Return a 1D array, even if input is scalar."""
    a = np.asarray(a)
    return a.reshape(1,) if a.ndim == 0 else a.ravel()


def ensure_2d(a):
    """Return a 2D array."""
    a = np.asarray(a)
    if a.ndim == 0:
        return a.reshape(1, 1)
    elif a.ndim == 1:
        return a.reshape(-1, 1)
    else:
        return a


def ensure_2d_row(x):
    """Return shape (1, d) when a single point is passed."""
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        return x.reshape(1, -1)
    if x.ndim == 2:
        return x
    return x.reshape(1, -1)


def safe_last_n(arr, n):
    """Safely get last n elements from array."""
    v = ensure_1d(arr)
    n = max(0, min(n, v.shape[0]))
    return v[-n:] if n else v[:0]


def safe_topk_indices(values, k: int):
    """Safely get top-k indices from array."""
    v = ensure_1d(values)
    n = v.shape[0]
    if n == 0:
        return np.array([], dtype=int)
    k = max(1, min(k, n))
    part = np.argpartition(v, k-1)[:k]
    return part[np.argsort(v[part])]
