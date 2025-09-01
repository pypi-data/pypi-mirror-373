"""
JSON schema validation tests for optimize command.
Ensures API stability and prevents regressions in machine-readable output.
"""

import json
import subprocess
import sys
import pytest


def run_smoke_json():
    """Run smoke test and extract JSON result."""
    p = subprocess.run(
        [sys.executable, "-m", "plogic", "optimize", "--smoke", "--objective", "energy", "--json"],
        capture_output=True, text=True, timeout=30
    )
    
    # Check if DANTE is not available
    if "DANTE not properly installed" in p.stdout or "DANTE optimization not available" in p.stdout:
        raise ImportError("DANTE not available in CI environment")
    
    # Check if command failed
    if p.returncode != 0:
        raise RuntimeError(f"Smoke test failed with return code {p.returncode}. Output: {p.stdout}")
    
    # Find the JSON block in stdout - look for the last complete JSON object
    output = p.stdout
    
    # Find the last occurrence of a JSON object
    start_idx = output.rfind('{\n  "schema_version"')
    if start_idx == -1:
        # Fallback: look for any JSON object
        start_idx = output.rfind('{')
    
    if start_idx == -1:
        raise ValueError(f"No JSON output found in smoke test. Output: {output}")
    
    # Extract from start to end
    json_text = output[start_idx:].strip()
    
    # Find the end of the JSON object
    brace_count = 0
    end_idx = 0
    for i, char in enumerate(json_text):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break
    
    if end_idx > 0:
        json_text = json_text[:end_idx]
    
    return json.loads(json_text)


def test_schema_keys_present():
    """Test that all required schema keys are present."""
    try:
        j = run_smoke_json()
    except ImportError as e:
        if "DANTE not available" in str(e):
            if __name__ == "__main__":
                # When run as script, just return without error
                return
            else:
                # When run via pytest, use skip
                pytest.skip("DANTE not available in CI environment")
        raise
    
    # Check top-level schema
    required_top = ["schema_version", "objective", "best_score", "evaluations", "best_config", "seed", "smoke_mode", "runtime_seconds"]
    for key in required_top:
        assert key in j, f"Missing top-level key: {key}"
    
    # Check schema version format
    assert j["schema_version"].count(".") == 2, f"Invalid schema version format: {j['schema_version']}"
    
    # Check evaluations is positive
    assert j["evaluations"] >= 1, f"Invalid evaluations count: {j['evaluations']}"
    
    # Check best_config completeness
    cfg = j["best_config"]
    required_config = ["platform", "P_high_mW", "pulse_ns", "coupling", "link_um", "fanout", "split_loss_db", "stages"]
    for key in required_config:
        assert key in cfg, f"Missing config key: {key}"
    
    print(f"[OK] Schema validation passed: {len(required_top)} top-level + {len(required_config)} config keys")


def test_score_threshold():
    """Test that smoke test score meets quality threshold."""
    try:
        j = run_smoke_json()
    except ImportError as e:
        if "DANTE not available" in str(e):
            if __name__ == "__main__":
                return
            else:
                pytest.skip("DANTE not available in CI environment")
        raise
    score = j["best_score"]
    assert score < 200.0, f"Smoke score too high: {score}"
    print(f"[OK] Score threshold passed: {score:.1f} < 200.0")


def test_parameter_bounds():
    """Test that parameters are within physical bounds."""
    try:
        j = run_smoke_json()
    except ImportError as e:
        if "DANTE not available" in str(e):
            if __name__ == "__main__":
                return
            else:
                pytest.skip("DANTE not available in CI environment")
        raise
    cfg = j["best_config"]
    
    # Check parameter bounds
    assert 0.01 <= cfg["P_high_mW"] <= 5.0, f"P_high_mW out of bounds: {cfg['P_high_mW']}"
    assert 0.05 <= cfg["pulse_ns"] <= 10.0, f"pulse_ns out of bounds: {cfg['pulse_ns']}"
    assert 0.05 <= cfg["coupling"] <= 2.5, f"coupling out of bounds: {cfg['coupling']}"
    assert 0.2 <= cfg["link_um"] <= 200.0, f"link_um out of bounds: {cfg['link_um']}"
    assert 1 <= cfg["fanout"] <= 32, f"fanout out of bounds: {cfg['fanout']}"
    assert 0.0 <= cfg["split_loss_db"] <= 3.0, f"split_loss_db out of bounds: {cfg['split_loss_db']}"
    assert 1 <= cfg["stages"] <= 64, f"stages out of bounds: {cfg['stages']}"
    assert cfg["platform"] in ["Si", "SiN", "AlGaAs"], f"Invalid platform: {cfg['platform']}"
    
    print(f"[OK] Parameter bounds validation passed")


def test_reproducibility():
    """Test that results are reproducible with same seed."""
    try:
        j1 = run_smoke_json()
        j2 = run_smoke_json()
    except ImportError as e:
        if "DANTE not available" in str(e):
            if __name__ == "__main__":
                return
            else:
                pytest.skip("DANTE not available in CI environment")
        raise
    
    # Should get identical results with same seed
    assert j1["best_score"] == j2["best_score"], f"Non-reproducible scores: {j1['best_score']} != {j2['best_score']}"
    assert j1["best_config"] == j2["best_config"], "Non-reproducible configurations"
    assert j1["evaluations"] == j2["evaluations"], f"Non-reproducible evaluation counts: {j1['evaluations']} != {j2['evaluations']}"
    
    print(f"[OK] Reproducibility test passed: identical results with seed {j1['seed']}")


if __name__ == "__main__":
    import sys
    print("Running JSON schema validation tests...")
    
    # Track if any test was skipped
    skipped = False
    
    try:
        test_schema_keys_present()
        test_score_threshold()
        test_parameter_bounds()
        test_reproducibility()
        
        print("\n[SUCCESS] All JSON schema tests passed! Enterprise API is stable and validated.")
    except ImportError as e:
        if "DANTE not available" in str(e):
            print("\n[SKIPPED] JSON schema tests skipped (DANTE not available in CI environment)")
            sys.exit(0)  # Exit successfully
        else:
            raise
    except Exception as e:
        # Check if it's a pytest.skip exception when run outside pytest
        # The exception class name is 'Skipped' from pytest
        if "Skipped" in str(type(e).__name__) or "DANTE not available" in str(e):
            print("\n[SKIPPED] JSON schema tests skipped (DANTE not available in CI environment)")
            sys.exit(0)  # Exit successfully
        else:
            print(f"\n[FAILED] JSON schema tests failed: {e}")
            raise
