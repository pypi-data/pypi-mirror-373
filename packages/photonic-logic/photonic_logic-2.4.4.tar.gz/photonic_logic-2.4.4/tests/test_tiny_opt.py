"""Test tiny optimization runs to prevent scalar indexing errors."""
from subprocess import run, PIPE
import json
import sys
import pytest


def test_tiny_run_no_crash():
    """Test that tiny optimization runs don't crash with scalar errors."""
    p = run(
        [sys.executable, "-m", "plogic", "optimize",
         "--objective", "energy", "--iterations", "1",
         "--initial-samples", "2", "--dims", "8", "--timeout", "10"],
        stdout=PIPE, stderr=PIPE, text=True
    )
    
    # Check for successful completion
    assert p.returncode == 0, f"Command failed with return code {p.returncode}\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}"
    
    # Check for absence of scalar indexing errors
    assert "invalid index to scalar variable" not in p.stdout
    assert "invalid index to scalar variable" not in p.stderr
    
    # Check for absence of other common array errors
    assert "IndexError" not in p.stderr
    assert "ValueError: setting an array element" not in p.stderr


def test_single_point_prediction():
    """Test that single-point predictions don't cause scalar issues."""
    import numpy as np
    from plogic.opt_utils.array_safety import ensure_1d, ensure_2d_row
    
    # Test scalar to 1D conversion
    scalar = np.array(5.0)
    arr_1d = ensure_1d(scalar)
    assert arr_1d.shape == (1,)
    assert arr_1d[0] == 5.0
    
    # Test single point to 2D row
    point = np.array([1.0, 2.0, 3.0])
    arr_2d = ensure_2d_row(point)
    assert arr_2d.shape == (1, 3)
    
    # Test already 2D stays 2D
    matrix = np.array([[1.0, 2.0], [3.0, 4.0]])
    arr_2d = ensure_2d_row(matrix)
    assert arr_2d.shape == (2, 2)


def test_safe_slicing():
    """Test safe slicing functions."""
    import numpy as np
    from plogic.opt_utils.array_safety import safe_last_n, safe_topk_indices
    
    # Test safe_last_n with various edge cases
    arr = np.array([1, 2, 3, 4, 5])
    
    # Normal case
    assert np.array_equal(safe_last_n(arr, 2), np.array([4, 5]))
    
    # Request more than available
    assert np.array_equal(safe_last_n(arr, 10), arr)
    
    # Empty array
    empty = np.array([])
    assert len(safe_last_n(empty, 5)) == 0
    
    # Single element
    single = np.array([42])
    assert np.array_equal(safe_last_n(single, 1), single)
    
    # Test safe_topk_indices
    values = np.array([3, 1, 4, 1, 5])
    
    # Normal case (get indices of 2 smallest values)
    top2 = safe_topk_indices(values, 2)
    assert len(top2) == 2
    assert all(idx in [1, 3] for idx in top2)  # indices of the two 1's
    
    # Request more than available
    topall = safe_topk_indices(values, 10)
    assert len(topall) == len(values)
    
    # Empty array
    empty_top = safe_topk_indices(np.array([]), 5)
    assert len(empty_top) == 0


def test_surrogate_wrapper():
    """Test surrogate wrapper handles scalars correctly."""
    import numpy as np
    
    # Skip test if sklearn not available
    try:
        from sklearn.ensemble import RandomForestRegressor
    except ImportError:
        import pytest
        pytest.skip("sklearn not available")
    
    from plogic.optimization.surrogates import SklearnSurrogateWrapper
    
    # Create a simple model
    model = RandomForestRegressor(n_estimators=10, random_state=42)
    wrapper = SklearnSurrogateWrapper(model)
    
    # Train with minimal data
    X_train = np.array([[1, 2], [3, 4], [5, 6]])
    y_train = np.array([1.0, 2.0, 3.0])
    wrapper.fit(X_train, y_train)
    
    # Test single point prediction (should not return scalar)
    X_single = np.array([[2, 3]])
    y_pred = wrapper.predict(X_single)
    assert y_pred.ndim == 1  # Should be 1D array, not scalar
    assert y_pred.shape[0] >= 1
    
    # Test with return_std
    y_pred, std = wrapper.predict(X_single, return_std=True)
    assert y_pred.ndim == 1
    assert std.ndim == 1
    assert y_pred.shape == std.shape


def test_acquisition_functions():
    """Test acquisition functions handle edge cases."""
    import numpy as np
    
    # Skip test if sklearn not available
    try:
        from sklearn.ensemble import RandomForestRegressor
    except ImportError:
        import pytest
        pytest.skip("sklearn not available")
    
    from plogic.optimization.surrogates import SklearnSurrogateWrapper
    from plogic.optimization.acquisition import pick_next
    
    # Create and train a simple surrogate
    model = RandomForestRegressor(n_estimators=10, random_state=42)
    surrogate = SklearnSurrogateWrapper(model)
    
    X_train = np.array([[1, 2], [3, 4], [5, 6]])
    y_train = np.array([1.0, 2.0, 3.0])
    surrogate.fit(X_train, y_train)
    
    # Test with single candidate
    X_single = np.array([2.5, 3.5])
    x_next = pick_next(surrogate, X_single)
    assert x_next.shape == (1, 2)
    
    # Test with multiple candidates
    X_multi = np.array([[2, 3], [4, 5], [6, 7]])
    x_next = pick_next(surrogate, X_multi)
    assert x_next.shape == (1, 2)


def test_bounds_sanitization():
    """Test parameter bounds sanitization."""
    from plogic.optimization.bounds import sanitize_config
    
    # Test with out-of-bounds values
    cfg = {
        "pulse_ns": -1.0,  # Below minimum
        "P_high_mW": 100.0,  # Above maximum
        "fanout": 0.5,  # Should be integer >= 1
        "stages": 100,  # Above maximum
    }
    
    sanitized = sanitize_config(cfg)
    
    # Check bounds are enforced
    assert sanitized["pulse_ns"] >= 0.05
    assert sanitized["P_high_mW"] <= 5.0
    assert isinstance(sanitized["fanout"], int)
    assert sanitized["fanout"] >= 1
    assert sanitized["stages"] <= 64


if __name__ == "__main__":
    # Run the critical test
    test_tiny_run_no_crash()
    print("[PASS] Tiny optimization run completed without scalar errors")
    
    # Run other tests
    test_single_point_prediction()
    print("[PASS] Single point predictions handled correctly")
    
    test_safe_slicing()
    print("[PASS] Safe slicing functions work correctly")
    
    test_surrogate_wrapper()
    print("[PASS] Surrogate wrapper prevents scalar issues")
    
    test_acquisition_functions()
    print("[PASS] Acquisition functions handle edge cases")
    
    test_bounds_sanitization()
    print("[PASS] Bounds sanitization works correctly")
    
    print("\nAll array safety tests passed!")
