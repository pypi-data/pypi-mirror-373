"""
Test to prevent regression of Keras input_shape/input_dim deprecation warnings.
This ensures that our Keras Functional API fixes stay fixed.
"""

import subprocess
import sys
import re
import pytest


def test_no_inputshape_warning():
    """Test that CLI commands don't produce Keras input_shape/input_dim warnings."""
    # Run a command that uses DANTE neural surrogate models
    result = subprocess.run(
        [sys.executable, "-m", "plogic", "optimize", "--smoke", "--objective", "energy"],
        capture_output=True,
        text=True,
        check=True
    )
    
    # Combine stdout and stderr to check all output
    combined_output = result.stdout + result.stderr
    
    # Check for the specific Keras deprecation warning
    keras_warning_pattern = r"Do not pass (input_shape|input_dim)"
    
    if re.search(keras_warning_pattern, combined_output, re.IGNORECASE):
        pytest.fail(
            f"Keras input_shape/input_dim deprecation warning detected!\n"
            f"This indicates that Sequential API is being used instead of Functional API.\n"
            f"Output:\n{combined_output}"
        )


def test_no_inputshape_warning_accelerator():
    """Test that accelerator command doesn't produce Keras warnings."""
    # Run accelerator command with fallback to avoid DANTE dependency issues
    result = subprocess.run(
        [sys.executable, "-m", "plogic", "accelerator", 
         "--iterations", "1", "--initial-samples", "2", "--use-fallback"],
        capture_output=True,
        text=True,
        check=False  # May fail, but we still want to check warnings
    )
    
    # Combine stdout and stderr to check all output
    combined_output = result.stdout + result.stderr
    
    # Check for the specific Keras deprecation warning
    keras_warning_pattern = r"Do not pass (input_shape|input_dim)"
    
    if re.search(keras_warning_pattern, combined_output, re.IGNORECASE):
        pytest.fail(
            f"Keras input_shape/input_dim deprecation warning detected in accelerator!\n"
            f"This indicates that Sequential API is being used instead of Functional API.\n"
            f"Output:\n{combined_output}"
        )


def test_dante_models_use_functional_api():
    """Test that DANTE models are using Functional API by checking imports."""
    try:
        # Try to import and check DANTE models
        from DANTE.dante.neural_surrogate import (
            AckleySurrogateModel, RastriginSurrogateModel, RosenbrockSurrogateModel
        )
        
        # Create a small test model to verify it uses Input layers
        model_class = AckleySurrogateModel
        model = model_class(dims=2)
        
        # Build the model to trigger any warnings
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            model.build_model()
            
            # Check if any warnings contain the deprecated pattern
            for warning in w:
                if re.search(r"Do not pass (input_shape|input_dim)", str(warning.message)):
                    pytest.fail(
                        f"Keras deprecation warning in {model_class.__name__}: {warning.message}"
                    )
                    
    except ImportError:
        pytest.skip("DANTE not available for testing")


if __name__ == "__main__":
    # Run the tests directly
    print("Testing for Keras input_shape/input_dim warnings...")
    
    try:
        test_no_inputshape_warning()
        print("✅ No Keras warnings in optimize command")
    except Exception as e:
        print(f"❌ Keras warning test failed: {e}")
        
    try:
        test_no_inputshape_warning_accelerator()
        print("✅ No Keras warnings in accelerator command")
    except Exception as e:
        print(f"❌ Accelerator warning test failed: {e}")
        
    try:
        test_dante_models_use_functional_api()
        print("✅ DANTE models use Functional API")
    except Exception as e:
        print(f"❌ DANTE model test failed: {e}")
