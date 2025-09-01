"""
Test suite for plateau detection and breaking in optimization.
"""

import pytest
import numpy as np
from unittest.mock import Mock, MagicMock
from typing import Dict, Any, List, Tuple
import warnings

# Skip tests if plateau_breaker imports fail (e.g., DANTE not available)
pytest.importorskip("plogic.optimization.plateau_breaker")
from plogic.optimization.plateau_breaker import PlateauBreaker, AdaptiveOptimizer, PlateauMetrics


def test_plateau_detection():
    """Test plateau detection functionality."""
    print("Testing plateau detection...")
    
    # Create plateau breaker
    pb = PlateauBreaker(dims=8, plateau_patience=3)
    
    # Simulate plateau (same score multiple times)
    for i in range(5):
        pb.update_history(
            best_score=10.0,  # Same score
            best_params=np.ones(8) * 0.5,  # Same parameters
            r2_score=0.8,
            mae=0.05
        )
    
    is_plateau, metrics = pb.detect_plateau()
    assert is_plateau, "Should detect plateau after repeated same scores"
    assert metrics.iterations_since_improvement >= 3
    print(f"[PASS] Plateau detected after {metrics.iterations_since_improvement} iterations")
    
    # Test improvement resets counter
    pb.update_history(
        best_score=5.0,  # Better score
        best_params=np.ones(8) * 0.3,
        r2_score=0.9,
        mae=0.03
    )
    
    is_plateau, metrics = pb.detect_plateau()
    assert not is_plateau, "Should not be plateau after improvement"
    assert metrics.iterations_since_improvement == 0
    print("[PASS] Improvement resets plateau detection")


def test_sobol_points():
    """Test Sobol quasi-random point generation."""
    print("\nTesting Sobol point generation...")
    
    pb = PlateauBreaker(
        dims=4,
        bounds=np.array([[0, 1], [0, 2], [0, 3], [0, 4]]),
        sobol_points=10
    )
    
    points = pb.get_sobol_points(n_points=10)
    
    assert points.shape == (10, 4), "Should generate correct number of points"
    assert np.all(points[:, 0] >= 0) and np.all(points[:, 0] <= 1), "Dim 0 bounds"
    assert np.all(points[:, 1] >= 0) and np.all(points[:, 1] <= 2), "Dim 1 bounds"
    assert np.all(points[:, 2] >= 0) and np.all(points[:, 2] <= 3), "Dim 2 bounds"
    assert np.all(points[:, 3] >= 0) and np.all(points[:, 3] <= 4), "Dim 3 bounds"
    
    print(f"[PASS] Generated {points.shape[0]} Sobol points within bounds")


def test_perturbation():
    """Test perturbation around best point."""
    print("\nTesting perturbation strategy...")
    
    pb = PlateauBreaker(
        dims=3,
        bounds=np.array([[0, 1], [0, 1], [0, 1]])
    )
    
    center = np.array([0.5, 0.5, 0.5])
    perturbed = pb.get_perturbed_points(center, n_points=5, noise_scale=0.1)
    
    assert perturbed.shape == (5, 3), "Should generate correct number of perturbed points"
    assert np.all(perturbed >= 0) and np.all(perturbed <= 1), "Points within bounds"
    
    # Check points are near center
    distances = np.linalg.norm(perturbed - center, axis=1)
    assert np.all(distances < 0.5), "Perturbed points should be near center"
    
    print(f"[PASS] Generated {perturbed.shape[0]} perturbed points near center")


def test_stuck_dimensions():
    """Test detection of stuck dimensions."""
    print("\nTesting stuck dimension detection...")
    
    pb = PlateauBreaker(dims=4, variance_threshold=1e-4)
    
    # Simulate stuck dimensions (dims 0 and 2 don't change)
    for i in range(5):
        params = np.array([
            0.5,  # Stuck
            np.random.rand(),  # Varying
            0.3,  # Stuck
            np.random.rand()  # Varying
        ])
        pb.update_history(10.0 + i * 0.1, params)
    
    is_plateau, metrics = pb.detect_plateau()
    
    # Check stuck dimensions detected
    assert 0 in metrics.stuck_dimensions, "Dimension 0 should be stuck"
    assert 2 in metrics.stuck_dimensions, "Dimension 2 should be stuck"
    assert 1 not in metrics.stuck_dimensions, "Dimension 1 should not be stuck"
    assert 3 not in metrics.stuck_dimensions, "Dimension 3 should not be stuck"
    
    print(f"[PASS] Detected stuck dimensions: {metrics.stuck_dimensions}")


def test_acquisition_selection():
    """Test adaptive acquisition function selection."""
    print("\nTesting acquisition function selection...")
    
    pb = PlateauBreaker(dims=8)
    
    # Test with poor R² score
    metrics1 = PlateauMetrics(
        best_score=10.0,
        score_variance=0.01,
        parameter_variance=0.01,
        r2_score=0.2,  # Poor
        mae=0.5,
        iterations_since_improvement=5,
        stuck_dimensions=[]
    )
    
    acq1 = pb.select_acquisition_function(metrics1)
    assert acq1['type'] == 'ucb', "Should use UCB for poor model"
    assert acq1['strategy'] == 'high_exploration'
    print(f"[PASS] Poor R² ({metrics1.r2_score:.2f}) → {acq1['strategy']}")
    
    # Test with many stuck dimensions
    metrics2 = PlateauMetrics(
        best_score=10.0,
        score_variance=0.01,
        parameter_variance=0.01,
        r2_score=0.8,
        mae=0.1,
        iterations_since_improvement=3,
        stuck_dimensions=[0, 1, 2, 3, 4]  # Many stuck
    )
    
    acq2 = pb.select_acquisition_function(metrics2)
    assert acq2['type'] == 'ucb', "Should use UCB for stuck dimensions"
    assert 'focus_dims' in acq2
    print(f"[PASS] {len(metrics2.stuck_dimensions)} stuck dims → {acq2['strategy']}")


def test_surrogate_selection():
    """Test surrogate model selection."""
    print("\nTesting surrogate model selection...")
    
    pb = PlateauBreaker(dims=8)
    
    # Test with small data
    metrics1 = PlateauMetrics(
        best_score=10.0,
        score_variance=0.01,
        parameter_variance=0.01,
        r2_score=0.2,
        mae=0.1,
        iterations_since_improvement=3,
        stuck_dimensions=[]
    )
    
    surrogate1 = pb.select_surrogate_model(metrics1, data_size=15)
    print(f"[PASS] Small data (15 points) → {surrogate1}")
    
    # Test with high MAE
    metrics2 = PlateauMetrics(
        best_score=10.0,
        score_variance=0.01,
        parameter_variance=0.01,
        r2_score=0.7,
        mae=0.3,  # High error
        iterations_since_improvement=3,
        stuck_dimensions=[]
    )
    
    surrogate2 = pb.select_surrogate_model(metrics2, data_size=100)
    print(f"[PASS] High MAE ({metrics2.mae:.2f}) → {surrogate2}")


def test_breakthrough_strategy():
    """Test complete breakthrough strategy generation."""
    print("\nTesting breakthrough strategy...")
    
    pb = PlateauBreaker(
        dims=8,
        bounds=np.array([[0, 2]] * 8),
        plateau_patience=3
    )
    
    # Create plateau condition
    for i in range(5):
        pb.update_history(
            best_score=10.0,
            best_params=np.ones(8),
            r2_score=0.4,
            mae=0.2
        )
    
    # Get breakthrough strategy
    current_best = np.ones(8)
    breakthrough = pb.break_plateau(current_best)
    
    assert 'strategy' in breakthrough
    assert 'points' in breakthrough
    assert 'acquisition' in breakthrough
    assert 'surrogate' in breakthrough
    
    print(f"[PASS] Strategies used: {breakthrough['strategy']}")
    print(f"[PASS] Generated {len(breakthrough['points'])} breakthrough points")
    print(f"[PASS] Recommended acquisition: {breakthrough['acquisition']['type']}")
    print(f"[PASS] Recommended surrogate: {breakthrough['surrogate']}")


def test_diagnostics():
    """Test diagnostic information."""
    print("\nTesting diagnostics...")
    
    pb = PlateauBreaker(dims=4)
    
    # Add some history
    for i in range(10):
        score = 10.0 - i * 0.5 if i < 3 else 8.5  # Plateau after 3 iterations
        pb.update_history(
            best_score=score,
            best_params=np.random.rand(4),
            r2_score=0.7 - i * 0.05,
            mae=0.1 + i * 0.01
        )
    
    diag = pb.get_diagnostics()
    
    assert 'iteration_count' in diag
    assert 'plateau_count' in diag
    assert 'is_plateau' in diag
    assert 'iterations_since_improvement' in diag
    assert 'current_best_score' in diag
    
    print("[PASS] Diagnostic information:")
    print(f"  - Iterations: {diag['iteration_count']}")
    print(f"  - Plateaus detected: {diag['plateau_count']}")
    print(f"  - Currently in plateau: {diag['is_plateau']}")
    print(f"  - Iterations since improvement: {diag['iterations_since_improvement']}")
    
    if 'recommendations' in diag:
        print(f"  - Recommended strategies: {diag['recommendations']['strategies']}")


def test_adaptive_optimizer_integration():
    """Test integration with base optimizer."""
    print("\nTesting AdaptiveOptimizer integration...")
    
    # Mock base optimizer
    class MockOptimizer:
        def __init__(self):
            self.iteration = 0
            self.best_params = np.ones(4) * 0.5
        
        def suggest(self, n_points):
            # Simple random suggestions
            return np.random.rand(n_points, 4)
        
        def get_best_params(self):
            return self.best_params
        
        def update(self, X, y):
            best_idx = np.argmin(y)
            self.best_params = X[best_idx]
            self.iteration += 1
    
    # Create adaptive optimizer
    base_opt = MockOptimizer()
    pb = PlateauBreaker(dims=4, plateau_patience=2)
    adaptive_opt = AdaptiveOptimizer(base_opt, pb, auto_break=True)
    
    # Simulate optimization with plateau
    for i in range(5):
        # Get suggestions
        X = adaptive_opt.suggest(n_points=4)
        
        # Simulate evaluations (plateau after iteration 2)
        if i < 2:
            y = np.random.rand(len(X)) * 10
        else:
            y = np.ones(len(X)) * 5.0  # Plateau
        
        # Update
        adaptive_opt.update(X, y)
    
    # Check plateau was detected and handled
    assert pb.plateau_count > 0, "Should have detected plateau"
    print(f"[PASS] Adaptive optimizer detected {pb.plateau_count} plateau(s)")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("PLATEAU BREAKER MODULE TESTS")
    print("=" * 60)
    
    test_plateau_detection()
    test_sobol_points()
    test_perturbation()
    test_stuck_dimensions()
    test_acquisition_selection()
    test_surrogate_selection()
    test_breakthrough_strategy()
    test_diagnostics()
    test_adaptive_optimizer_integration()
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! [PASS]")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
