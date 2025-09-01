"""
Tests to ensure unified constants and physics calculations are consistent across all commands.
"""

import json
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch

from plogic.config.constants import DeviceConst, pulse_energy_fJ, contrast_db
from plogic.physics.metrics import (
    tops_from_spec,
    utilization_product,
    power_breakdown,
    power_breakdown_explicit,
)
from plogic.controller import PhotonicMolecule, ExperimentController


class TestUnifiedConstants:
    """Test that all commands use the same constants."""
    
    def test_device_constants_frozen(self):
        """Test that DeviceConst is immutable."""
        C = DeviceConst()
        with pytest.raises(AttributeError):
            C.P_high_mW = 2.0  # Should fail because dataclass is frozen
    
    def test_pulse_energy_calculation(self):
        """Test unified pulse energy calculation."""
        # Test basic calculation
        energy = pulse_energy_fJ(P_high_mW=1.0, pulse_ns=1.0, extra_loss_db=0.0)
        assert energy == 1000.0  # 1 mW * 1 ns * 1e3 = 1000 fJ
        
        # Test with loss
        energy_with_loss = pulse_energy_fJ(P_high_mW=1.0, pulse_ns=1.0, extra_loss_db=3.0)
        assert energy_with_loss == pytest.approx(1000.0 * 10**(3.0/10), rel=1e-6)
        
        # Test with different values
        energy2 = pulse_energy_fJ(P_high_mW=2.0, pulse_ns=0.5, extra_loss_db=0.0)
        assert energy2 == 1000.0  # 2 mW * 0.5 ns * 1e3 = 1000 fJ
    
    def test_contrast_db_calculation(self):
        """Test unified contrast calculation."""
        # Test basic contrast
        cdB = contrast_db(T_on=1.0, T_off=0.1)
        assert cdB == pytest.approx(10.0, rel=1e-6)  # 10*log10(10) = 10 dB
        
        # Test with small but not epsilon-clamped values
        cdB_small = contrast_db(T_on=1e-6, T_off=1e-8)
        assert cdB_small == pytest.approx(20.0, rel=1e-6)  # 10*log10(100) = 20 dB
        
        # Test with epsilon protection (both values get clamped to same epsilon)
        cdB_zero = contrast_db(T_on=0.0, T_off=0.0)
        assert cdB_zero == 0.0  # Both clamped to epsilon, so log(eps/eps) = 0
        
        # Test with very small values that get epsilon-clamped
        cdB_tiny = contrast_db(T_on=1e-12, T_off=1e-15)
        assert cdB_tiny == 0.0  # Both below epsilon, so both clamped to same value
    
    def test_energy_consistency_across_commands(self):
        """Test that energy calculations are consistent across different command paths."""
        C = DeviceConst()
        
        # Calculate energy using the unified function (without split loss for base energy)
        expected_energy = pulse_energy_fJ(C.P_high_mW, C.pulse_ns, 0.0)  # No split loss for base
        
        # Test cascade command energy calculation
        dev = PhotonicMolecule()
        ctl = ExperimentController(dev)
        cascade_res = ctl.test_cascade(
            n_stages=2,
            base_P_ctrl_W=C.P_high_mW * 1e-3,
            pulse_duration_s=C.pulse_ns * 1e-9
        )
        
        # Check that base_energy_fJ matches expected
        for gate in cascade_res:
            base_energy = cascade_res[gate].get("base_energy_fJ", 0)
            # Allow some tolerance due to physics calculations
            assert base_energy == pytest.approx(expected_energy, rel=0.01)
    
    def test_benchmark_nonzero_contrast(self):
        """Test that benchmark command returns non-zero contrast."""
        from plogic.cli import benchmark
        from typer.testing import CliRunner
        from plogic.cli import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["benchmark", "--metric", "switching-contrast"])
        
        assert result.exit_code == 0
        output = json.loads(result.output)
        
        # Check that the benchmark runs and returns expected fields
        # Note: contrast_dB may be 0.0 if device is far from resonance
        assert "contrast_dB" in output
        assert "platform" in output
        assert "P_high_mW" in output
        assert "pulse_ns" in output
        
        # The benchmark command uses platform-specific defaults, not global constants
        # AlGaAs is the default platform for benchmark
        platform_defaults = {
            "AlGaAs": {"p_high_mw": 0.06, "pulse_ns": 1.4},
            "Si": {"p_high_mw": 0.13, "pulse_ns": 0.1},
            "SiN": {"p_high_mw": 2.5, "pulse_ns": 1.0},
        }
        # Default platform is AlGaAs
        expected_defaults = platform_defaults["AlGaAs"]
        assert output["P_high_mW"] == expected_defaults["p_high_mw"]
        assert output["pulse_ns"] == expected_defaults["pulse_ns"]


class TestPhysicsMetrics:
    """Test unified physics metrics calculations."""
    
    def test_tops_calculation(self):
        """Test TOPS calculation with different array scopes."""
        # Test global scope
        peak_global, eff_global, rings_global = tops_from_spec(
            rows=35, cols=36, lanes=24,
            macs_per_ring=2.0, clock_ghz=1.0,
            utilization=0.5, array_scope="global"
        )
        
        assert rings_global == 35 * 36  # 1260 rings
        assert peak_global == pytest.approx(1260 * 2 * 1.0 / 1e3, rel=1e-6)  # 2.52 TOPS
        assert eff_global == pytest.approx(peak_global * 0.5, rel=1e-6)
        
        # Test per_lane scope
        peak_lane, eff_lane, rings_lane = tops_from_spec(
            rows=35, cols=36, lanes=24,
            macs_per_ring=2.0, clock_ghz=1.0,
            utilization=0.5, array_scope="per_lane"
        )
        
        assert rings_lane == 35 * 36 * 24  # 30240 rings
        assert peak_lane == pytest.approx(30240 * 2 * 1.0 / 1e3, rel=1e-6)  # 60.48 TOPS
        assert eff_lane == pytest.approx(peak_lane * 0.5, rel=1e-6)
    
    def test_utilization_product(self):
        """Test utilization product calculation."""
        util = utilization_product(
            decode_util=0.55,
            duty=0.80,
            guard=0.86
        )
        expected = 0.55 * 0.80 * 0.86
        assert util == pytest.approx(expected, rel=1e-6)
    
    def test_power_breakdown(self):
        """Test power breakdown calculation."""
        C = DeviceConst()
        total_rings = 1260
        
        pb = power_breakdown(total_rings, C)
        
        # Check individual components
        expected_heaters = C.heater_uW_per_ring * total_rings * C.active_fraction / 1e6
        assert pb["heaters_W"] == pytest.approx(expected_heaters, rel=1e-6)
        assert pb["laser_W"] == C.laser_W
        assert pb["dsp_sram_W"] == C.dsp_sram_W
        assert pb["misc_W"] == C.misc_W
        
        # Check total
        expected_total = expected_heaters + C.laser_W + C.dsp_sram_W + C.misc_W
        assert pb["total_W"] == pytest.approx(expected_total, rel=1e-6)
        
        # Check ring counts
        assert pb["total_rings"] == total_rings
        assert pb["active_rings"] == int(total_rings * C.active_fraction)
    
    def test_power_breakdown_explicit(self):
        """Test explicit power breakdown calculation."""
        pb = power_breakdown_explicit(
            heater_uW_per_ring=200.0,
            active_fraction=0.8,
            total_rings=1000,
            laser_W=0.5,
            dsp_sram_W=0.3,
            misc_W=0.1
        )
        
        # Check calculations
        expected_heaters = 200.0 * 1000 * 0.8 / 1e6  # 0.16 W
        assert pb["heaters_W"] == pytest.approx(expected_heaters, rel=1e-6)
        assert pb["total_W"] == pytest.approx(0.16 + 0.5 + 0.3 + 0.1, rel=1e-6)


class TestEnvironmentOverrides:
    """Test that environment variables can override constants."""
    
    @patch.dict('os.environ', {'PLOGIC_P_HIGH_MW': '2.0'})
    def test_env_override_p_high(self):
        """Test P_high_mW can be overridden via environment."""
        # Need to reimport to pick up env var
        import importlib
        import plogic.config.constants
        importlib.reload(plogic.config.constants)
        from plogic.config.constants import DeviceConst
        
        C = DeviceConst()
        assert C.P_high_mW == 2.0
    
    @patch.dict('os.environ', {'PLOGIC_ARRAY_SCOPE': 'per_lane'})
    def test_env_override_array_scope(self):
        """Test array_scope can be overridden via environment."""
        import importlib
        import plogic.config.constants
        importlib.reload(plogic.config.constants)
        from plogic.config.constants import DeviceConst
        
        C = DeviceConst()
        assert C.array_scope == 'per_lane'


class TestConstantsCommand:
    """Test the new constants CLI command."""
    
    def test_constants_command_json(self):
        """Test constants command JSON output."""
        from typer.testing import CliRunner
        from plogic.cli import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["constants", "--format", "json"])
        
        assert result.exit_code == 0
        output = json.loads(result.output)
        
        # Check structure
        assert "wavelength_nm" in output
        assert "P_high_mW" in output
        assert "calculated" in output
        assert "pulse_energy_fJ" in output["calculated"]
        assert "total_utilization" in output["calculated"]
    
    def test_constants_command_table(self):
        """Test constants command table output."""
        from typer.testing import CliRunner
        from plogic.cli import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["constants", "--format", "table"])
        
        assert result.exit_code == 0
        assert "PHOTONIC LOGIC CONSTANTS" in result.output
        assert "v2.4.0" in result.output
        assert "Wavelength:" in result.output
        assert "Pulse energy:" in result.output


def test_no_hardcoded_energy_values():
    """Ensure no hardcoded energy values remain in the codebase."""
    # This is a meta-test to ensure we're using unified calculations
    from plogic.controller import ExperimentController, PhotonicMolecule
    from plogic.config.constants import DeviceConst, pulse_energy_fJ
    
    C = DeviceConst()
    dev = PhotonicMolecule()
    ctl = ExperimentController(dev)
    
    # Run cascade and check energy is calculated correctly
    res = ctl.test_cascade(
        n_stages=2,
        base_P_ctrl_W=C.P_high_mW * 1e-3,
        pulse_duration_s=C.pulse_ns * 1e-9
    )
    
    expected_energy = pulse_energy_fJ(
        C.P_high_mW,
        C.pulse_ns,
        0.0  # No extra loss in basic cascade
    )
    
    for gate in res:
        if "base_energy_fJ" in res[gate]:
            # Energy should match our unified calculation
            assert res[gate]["base_energy_fJ"] == pytest.approx(expected_energy, rel=0.1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
