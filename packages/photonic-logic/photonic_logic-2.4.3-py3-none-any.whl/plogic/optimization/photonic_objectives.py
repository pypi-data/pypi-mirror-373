"""
Photonic Logic Objective Functions for DANTE Optimization

This module implements DANTE-compatible objective functions for optimizing photonic logic circuits.
Supports single and multi-objective optimization across energy, cascade depth, thermal safety, and fabrication feasibility.
"""

import sys
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import numpy as np
import subprocess
import json

# Add DANTE to path for imports (with fallback for CI environments)
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'DANTE'))
    from dante.obj_functions import ObjectiveFunction
    from dante.utils import Tracker
    DANTE_AVAILABLE = True
except ImportError:
    # Fallback for environments without DANTE
    DANTE_AVAILABLE = False
    
    # Create minimal fallback classes
    class ObjectiveFunction(ABC):
        """Fallback ObjectiveFunction for when DANTE is not available."""
        def __init__(self):
            self.dims = 8
            self.turn = 0.01
            self.name = "fallback"
            self.lb = None
            self.ub = None
        
        def _preprocess(self, x):
            return np.array(x)
        
        @abstractmethod
        def __call__(self, x, apply_scaling=True, track=True):
            pass
    
    class Tracker:
        """Fallback Tracker for when DANTE is not available."""
        def __init__(self, name):
            self.name = name
            self.data = []
        
        def track(self, value, x):
            self.data.append({"value": value, "x": x})
        
        def track_metadata(self, metadata):
            pass

# Import photonic logic components
from ..controller import ExperimentController, PhotonicMolecule
from ..materials.platforms import PlatformDB


@dataclass
class PhotonicObjectiveBase(ObjectiveFunction):
    """Base class for photonic logic objective functions."""
    
    def _run_photonic_simulation(self, x: np.ndarray) -> Dict[str, Any]:
        """
        Run photonic logic simulation with parameters from DANTE.
        
        Args:
            x: Parameter vector from DANTE
            
        Returns:
            Simulation results dictionary
        """
        try:
            # Extract parameters with strict bounds enforcement
            platform_idx = int(np.clip(x[0], 0, 2))
            platforms = ["AlGaAs", "Si", "SiN"]
            platform = platforms[platform_idx]
            
            # Enforce minimum valid values to prevent invalid configurations
            p_high_mw = max(0.05, float(x[1]))  # Minimum 0.05 mW
            pulse_ns = max(0.05, float(x[2]))   # Minimum 0.05 ns
            coupling_eta = np.clip(float(x[3]), 0.7, 0.99)  # Realistic coupling range
            link_length_um = max(20.0, float(x[4]))  # Minimum 20 μm
            fanout = max(1, int(np.clip(x[5], 1, 8)))  # Force integer, minimum 1
            split_loss_db = max(0.2, float(x[6]))  # Minimum 0.2 dB
            # Extract stages with correct bounds [8, 24] and ensure integer
            stages = max(8, min(24, int(np.round(x[7]))))  # Force integer in [8, 24]
            
            # Load platform configuration
            db = PlatformDB()
            platform_obj = db.get(platform)
            
            # Create device with platform-specific parameters
            dev = PhotonicMolecule(
                n2=platform_obj.nonlinear.n2_m2_per_W,
                xpm_mode="physics" if platform == "AlGaAs" else "linear"
            )
            
            # Run cascade simulation
            ctl = ExperimentController(dev)
            base_P_ctrl_W = p_high_mw * 1e-3
            pulse_duration_s = pulse_ns * 1e-9
            
            result = ctl.test_cascade(
                n_stages=stages,
                base_P_ctrl_W=base_P_ctrl_W,
                pulse_duration_s=pulse_duration_s
            )
            
            # Add configuration metadata
            for gate_type in result:
                result[gate_type]["platform"] = platform
                result[gate_type]["fanout"] = fanout
                result[gate_type]["split_loss_db"] = split_loss_db
                result[gate_type]["coupling_eta"] = coupling_eta
                result[gate_type]["link_length_um"] = link_length_um
                
                # Calculate fanout-adjusted metrics
                if fanout > 1:
                    effective_depth = max(1, int(stages / np.sqrt(fanout)))
                    split_efficiency = 10 ** (-split_loss_db / 10)
                    base_energy = result[gate_type].get("base_energy_fJ", base_P_ctrl_W * pulse_duration_s * 1e15)
                    result[gate_type]["effective_cascade_depth"] = effective_depth
                    result[gate_type]["split_efficiency"] = split_efficiency
                    result[gate_type]["fanout_adjusted_energy_fJ"] = base_energy * fanout
                else:
                    result[gate_type]["effective_cascade_depth"] = stages
                    result[gate_type]["fanout_adjusted_energy_fJ"] = result[gate_type].get("base_energy_fJ", base_P_ctrl_W * pulse_duration_s * 1e15)
            
            return result
            
        except Exception as e:
            # Return invalid result for failed simulations
            return {
                "XOR": {
                    "fanout_adjusted_energy_fJ": 1e6,  # Very high energy penalty
                    "effective_cascade_depth": 0,
                    "effective_P_ctrl_mW": 1e6,
                    "min_contrast_dB": 0,
                    "platform": "invalid"
                }
            }


@dataclass
class PhotonicEnergyOptimizer(PhotonicObjectiveBase):
    """Single-objective energy minimization for photonic logic circuits."""
    
    dims: int = 8
    turn: float = 0.01
    name: str = "photonic_energy"
    
    def __post_init__(self):
        # Parameter bounds: [platform_idx, P_high_mW, pulse_ns, coupling_eta, 
        #                   link_length_um, fanout, split_loss_db, stages]
        # Fixed bounds to prevent invalid configurations (no zeros)
        self.lb = np.array([0, 0.05, 0.05, 0.7, 20,  1, 0.2, 1])  # No zero pulse/stages
        self.ub = np.array([2, 5.0,  5.0,  0.99, 200, 8, 2.0, 20])
        self.tracker = Tracker(self.name + str(self.dims))
    
    def scaled(self, y: float) -> float:
        """Scale energy for DANTE (DANTE maximizes, so return 1/energy)."""
        return 10000 / (abs(y) + 1)
    
    def __call__(self, x: np.ndarray, apply_scaling: bool = True, track: bool = True) -> float:
        x = self._preprocess(x)
        result = self._run_photonic_simulation(x)
        
        # Extract energy from XOR gate (representative)
        energy_fJ = result["XOR"]["fanout_adjusted_energy_fJ"]
        
        # Apply penalties for impractical configurations
        power_mW = result["XOR"]["effective_P_ctrl_mW"]
        if power_mW > 100:  # >100mW impractical
            energy_fJ *= 100  # Heavy penalty
        
        if track:
            self.tracker.track(energy_fJ, x)
        
        # Return negative energy (DANTE maximizes, we want to minimize energy)
        return -energy_fJ if not apply_scaling else self.scaled(-energy_fJ)


@dataclass
class PhotonicCascadeOptimizer(PhotonicObjectiveBase):
    """Single-objective cascade depth maximization."""
    
    dims: int = 8
    turn: float = 0.01
    name: str = "photonic_cascade"
    
    def __post_init__(self):
        self.lb = np.array([0, 0.01, 0.05, 0.7, 5,   1, 0.1, 1])
        self.ub = np.array([2, 5.0,  2.0,  0.99, 200, 8, 2.0, 50])
        self.tracker = Tracker(self.name + str(self.dims))
    
    def scaled(self, y: float) -> float:
        """Scale cascade depth for DANTE."""
        return max(0, y) * 10  # Amplify for better optimization
    
    def __call__(self, x: np.ndarray, apply_scaling: bool = True, track: bool = True) -> float:
        x = self._preprocess(x)
        result = self._run_photonic_simulation(x)
        
        # Extract effective cascade depth
        cascade_depth = result["XOR"]["effective_cascade_depth"]
        
        # Apply penalties for poor performance
        contrast_dB = result["XOR"]["min_contrast_dB"]
        if contrast_dB < 10:  # Poor extinction ratio
            cascade_depth *= 0.1  # Heavy penalty
        
        if track:
            self.tracker.track(cascade_depth, x)
        
        return cascade_depth if not apply_scaling else self.scaled(cascade_depth)


@dataclass
class PhotonicThermalOptimizer(PhotonicObjectiveBase):
    """Single-objective thermal safety optimization."""
    
    dims: int = 8
    turn: float = 0.01
    name: str = "photonic_thermal"
    
    def __post_init__(self):
        self.lb = np.array([0, 0.01, 0.05, 0.7, 5,   1, 0.1, 1])
        self.ub = np.array([2, 5.0,  2.0,  0.99, 200, 8, 2.0, 20])
        self.tracker = Tracker(self.name + str(self.dims))
    
    def scaled(self, y: float) -> float:
        """Scale thermal safety score for DANTE."""
        return max(0, y)
    
    def __call__(self, x: np.ndarray, apply_scaling: bool = True, track: bool = True) -> float:
        x = self._preprocess(x)
        result = self._run_photonic_simulation(x)
        
        # Compute thermal safety score
        power_mW = result["XOR"]["effective_P_ctrl_mW"]
        platform = result["XOR"]["platform"]
        
        # Platform-specific thermal limits (mW)
        thermal_limits = {"AlGaAs": 1.0, "Si": 10.0, "SiN": 500.0}
        limit = thermal_limits.get(platform, 1.0)
        
        # Thermal safety score (0-100)
        if power_mW <= limit * 0.1:  # Well below limit
            thermal_score = 100
        elif power_mW >= limit:      # At or above limit
            thermal_score = 0
        else:
            thermal_score = 100 * (1 - (power_mW - limit*0.1) / (limit*0.9))
        
        if track:
            self.tracker.track(thermal_score, x)
        
        return thermal_score if not apply_scaling else self.scaled(thermal_score)


@dataclass
class PhotonicMultiObjective(PhotonicObjectiveBase):
    """Multi-objective optimization for photonic logic circuits."""
    
    dims: int = 12
    turn: float = 0.01
    name: str = "photonic_multi"
    
    # Objective weights
    energy_weight: float = 0.4
    cascade_weight: float = 0.3
    thermal_weight: float = 0.2
    fabrication_weight: float = 0.1
    
    # Cascade penalty parameters (configurable via CLI)
    cascade_min_stages: int = 8
    cascade_target_stages: int = 12
    cascade_hard_penalty: float = 3.0
    cascade_band_penalty: float = 0.5
    
    # Verbose logging flag
    _verbose: bool = False
    
    def __post_init__(self):
        # Extended parameter space: [platform_idx, P_high_mW, pulse_ns, coupling_eta, 
        #                           link_length_um, fanout, split_loss_db, stages,
        #                           hybrid_flag, routing_fraction, include_2pa, auto_timing]
        self.lb = np.array([0, 0.01, 0.05, 0.7, 5,   1, 0.1, 8,  0, 0.1, 0, 0])  # stages: 8 not 1
        self.ub = np.array([2, 5.0,  2.0,  0.99, 200, 8, 2.0, 24, 1, 0.9, 1, 1])  # stages: 24 not 50
        self.tracker = Tracker(self.name + str(self.dims))
    
    def scaled(self, y: float) -> float:
        """Scale composite score for DANTE."""
        return max(0, y)
    
    def _compute_energy_score(self, result: Dict[str, Any]) -> float:
        """Compute energy efficiency score (0-100) with robust normalization."""
        energy_fJ = result["XOR"]["fanout_adjusted_energy_fJ"]
        
        # Robust logarithmic scoring with epsilon guards
        energy_fJ = max(energy_fJ, 1e-3)  # Prevent log(0)
        
        # Use robust bounds instead of fixed thresholds
        log_energy = np.log10(energy_fJ)
        
        # Robust scoring: lower energy is better
        if energy_fJ <= 10:
            score = 100.0
        elif energy_fJ >= 10000:  # Expanded upper bound for robustness
            score = 0.0
        else:
            # Smooth transition with epsilon guard
            log_range = np.log10(10000/10)  # log10(1000)
            normalized = (log_energy - np.log10(10)) / max(log_range, 1e-9)
            score = max(0.0, min(100.0, 100.0 * (1.0 - normalized)))
        
        return score
    
    def _extract_stages(self, result: Dict[str, Any]) -> float:
        """
        Robustly extract cascade depth from multiple possible locations.
        """
        # Try direct keys first
        for key in ("stages", "Stages", "cascade_depth", "depth"):
            if key in result and isinstance(result[key], (int, float)):
                return float(result[key])
        
        # Try nested XOR structure (most common)
        xor = result.get("XOR", {})
        for key in ("effective_cascade_depth", "cascade_depth", "stages"):
            value = xor.get(key, None)
            if isinstance(value, (int, float)):
                return float(value)
        
        # Try other gate types as fallback
        for gate_type in ["AND", "OR", "NAND", "NOR", "XNOR"]:
            gate_data = result.get(gate_type, {})
            for key in ("effective_cascade_depth", "cascade_depth", "stages"):
                value = gate_data.get(key, None)
                if isinstance(value, (int, float)):
                    return float(value)
        
        # Ultimate fallback
        return 1.0
    
    def _compute_cascade_score(self, result: Dict[str, Any]) -> float:
        """
        Compute cascade penalty (lower is better).
        Imposes hard squared-hinge penalty for shallow cascades and soft bowl around target.
        Uses configurable parameters from CLI with verbose logging.
        """
        # Extract cascade depth robustly
        stages = self._extract_stages(result)
        
        # Use configurable cascade penalty parameters
        min_stages = self.cascade_min_stages
        target_stages = self.cascade_target_stages
        hard_scale = self.cascade_hard_penalty
        band_scale = self.cascade_band_penalty
        
        # Hard squared penalty for shallow designs (< min_stages)
        pen_shallow = max(0.0, (min_stages - stages)) ** 2
        
        # Soft quadratic penalty around target band
        dev = (stages - target_stages) / max(1.0, target_stages)
        pen_band = dev * dev
        
        # Final cascade penalty (lower is better)
        cascade_penalty = hard_scale * pen_shallow + band_scale * pen_band
        
        # Verbose logging for debugging
        if hasattr(self, '_verbose') and self._verbose:
            print(f"Cascade penalty: stages={stages:.3f}, min={min_stages}, target={target_stages}, "
                  f"hard={hard_scale:.3f}, band={band_scale:.3f} -> pen={cascade_penalty:.3f} "
                  f"(shallow={pen_shallow:.3f}, band={pen_band:.3f})")
        
        return cascade_penalty
    
    def _compute_thermal_score(self, result: Dict[str, Any]) -> float:
        """Compute thermal safety score (0-100) with robust normalization."""
        power_mW = result["XOR"].get("effective_P_ctrl_mW", 0.1)
        platform = result["XOR"].get("platform", "Si")
        
        # Platform-specific thermal limits with robust bounds
        thermal_limits = {"AlGaAs": 1.0, "Si": 10.0, "SiN": 500.0}
        limit = thermal_limits.get(platform, 10.0)
        
        # Robust thermal scoring with epsilon guards
        power_mW = max(power_mW, 1e-6)  # Prevent division issues
        
        # Smooth thermal scoring with guaranteed non-zero range
        safe_zone = limit * 0.1  # 10% of limit is safe
        danger_zone = limit * 1.5  # 150% of limit is dangerous
        
        if power_mW <= safe_zone:
            score = 100.0
        elif power_mW >= danger_zone:
            score = 5.0  # Minimum score, not zero
        else:
            # Smooth transition with robust normalization
            span = max(danger_zone - safe_zone, 1e-6)
            normalized = (power_mW - safe_zone) / span
            score = max(5.0, 100.0 * (1.0 - normalized))
        
        return score
    
    def _compute_fabrication_score(self, result: Dict[str, Any]) -> float:
        """Compute fabrication feasibility score (0-100) with robust normalization."""
        platform = result["XOR"].get("platform", "Si")
        coupling_eta = result["XOR"].get("coupling_eta", 0.9)
        contrast_dB = result["XOR"].get("min_contrast_dB", 10.0)
        
        # Platform maturity scores (CMOS compatibility) with robust bounds
        platform_scores = {"AlGaAs": 60, "Si": 100, "SiN": 90}
        base_score = platform_scores.get(platform, 75)  # Better default
        
        # Robust coupling efficiency bonus with epsilon guards
        coupling_eta = np.clip(coupling_eta, 0.1, 0.99)  # Prevent extreme values
        coupling_bonus = (1 - coupling_eta) * 15  # Reduced impact
        
        # Robust contrast scoring with minimum floor
        contrast_dB = max(contrast_dB, 0.1)  # Prevent negative/zero
        if contrast_dB >= 15:
            contrast_bonus = 20
        elif contrast_dB >= 5:
            contrast_bonus = 10 * (contrast_dB - 5) / 10  # Smooth transition
        else:
            contrast_bonus = -20  # Penalty for poor contrast
        
        # Robust final score with guaranteed minimum
        final_score = base_score + coupling_bonus + contrast_bonus
        return max(10.0, min(100.0, final_score))  # Floor at 10, not 0
    
    def _run_photonic_simulation(self, x: np.ndarray) -> Dict[str, Any]:
        """Extended simulation with hybrid platform support."""
        try:
            # Extract parameters
            platform_idx = int(np.clip(x[0], 0, 2))
            platforms = ["AlGaAs", "Si", "SiN"]
            platform = platforms[platform_idx]
            
            p_high_mw = float(x[1])
            pulse_ns = float(x[2])
            coupling_eta = float(x[3])
            link_length_um = float(x[4])
            fanout = int(np.clip(x[5], 1, 8))
            split_loss_db = float(x[6])
            # Extract stages with correct bounds [8, 24] and ensure integer
            stages = max(8, min(24, int(np.round(x[7]))))  # Force integer in [8, 24]
            
            # Extended parameters for multi-objective
            if len(x) >= 12:
                hybrid_flag = bool(x[8] > 0.5)
                routing_fraction = float(x[9])
                include_2pa = bool(x[10] > 0.5)
                auto_timing = bool(x[11] > 0.5)
            else:
                hybrid_flag = False
                routing_fraction = 0.5
                include_2pa = False
                auto_timing = False
            
            # Load platform configuration
            db = PlatformDB()
            platform_obj = db.get(platform)
            
            # Handle hybrid platform
            if hybrid_flag:
                from ..materials.hybrid import HybridPlatform
                hybrid_platform = HybridPlatform(
                    logic_material=platform,
                    routing_material="SiN",
                    routing_fraction=routing_fraction
                )
                eff_params = hybrid_platform.get_effective_parameters()
                effective_n2 = eff_params["effective_n2"]
                platform_name = f"Hybrid-{platform}/SiN"
            else:
                effective_n2 = platform_obj.nonlinear.n2_m2_per_W
                platform_name = platform
            
            # Create device
            dev = PhotonicMolecule(
                n2=effective_n2,
                xpm_mode="physics" if platform == "AlGaAs" else "linear"
            )
            
            # Run simulation
            ctl = ExperimentController(dev)
            base_P_ctrl_W = p_high_mw * 1e-3
            pulse_duration_s = pulse_ns * 1e-9
            
            result = ctl.test_cascade(
                n_stages=stages,
                base_P_ctrl_W=base_P_ctrl_W,
                pulse_duration_s=pulse_duration_s
            )
            
            # Add metadata
            for gate_type in result:
                result[gate_type]["platform"] = platform_name
                result[gate_type]["fanout"] = fanout
                result[gate_type]["split_loss_db"] = split_loss_db
                result[gate_type]["coupling_eta"] = coupling_eta
                result[gate_type]["link_length_um"] = link_length_um
                result[gate_type]["hybrid"] = hybrid_flag
                
                # Calculate fanout-adjusted metrics
                if fanout > 1:
                    effective_depth = max(1, int(stages / np.sqrt(fanout)))
                    split_efficiency = 10 ** (-split_loss_db / 10)
                    base_energy = result[gate_type].get("base_energy_fJ", base_P_ctrl_W * pulse_duration_s * 1e15)
                    result[gate_type]["effective_cascade_depth"] = effective_depth
                    result[gate_type]["split_efficiency"] = split_efficiency
                    result[gate_type]["fanout_adjusted_energy_fJ"] = base_energy * fanout
                else:
                    result[gate_type]["effective_cascade_depth"] = stages
                    result[gate_type]["fanout_adjusted_energy_fJ"] = result[gate_type].get("base_energy_fJ", base_P_ctrl_W * pulse_duration_s * 1e15)
            
            return result
            
        except Exception as e:
            # Return penalty result for failed simulations
            return {
                "XOR": {
                    "fanout_adjusted_energy_fJ": 1e6,
                    "effective_cascade_depth": 0,
                    "effective_P_ctrl_mW": 1e6,
                    "min_contrast_dB": 0,
                    "platform": "invalid",
                    "coupling_eta": 0.5,
                    "hybrid": False
                }
            }
    
    def __call__(self, x: np.ndarray, apply_scaling: bool = True, track: bool = True) -> float:
        x = self._preprocess(x)
        result = self._run_photonic_simulation(x)
        
        # Compute individual objective scores
        energy_score = self._compute_energy_score(result)
        cascade_penalty = self._compute_cascade_score(result)  # Returns penalty (lower is better)
        thermal_score = self._compute_thermal_score(result)
        fabrication_score = self._compute_fabrication_score(result)
        
        # Convert scores to consistent direction (lower is better)
        # Energy score is 0-100 (higher is better), so invert it
        energy_penalty = 100 - energy_score
        # Thermal and fabrication scores are 0-100 (higher is better), so invert them
        thermal_penalty = 100 - thermal_score
        fabrication_penalty = 100 - fabrication_score
        
        # Weighted composite penalty (lower is better)
        composite_penalty = (
            self.energy_weight * energy_penalty +
            self.cascade_weight * cascade_penalty +  # Already a penalty
            self.thermal_weight * thermal_penalty +
            self.fabrication_weight * fabrication_penalty
        )
        
        # Verbose score breakdown logging
        if hasattr(self, '_verbose') and self._verbose:
            print(f"Score terms: E={energy_penalty:.4f} (w={self.energy_weight:.2f}), "
                  f"Cpen={cascade_penalty:.4f} (w={self.cascade_weight:.2f}), "
                  f"T={thermal_penalty:.4f} (w={self.thermal_weight:.2f}), "
                  f"F={fabrication_penalty:.4f} (w={self.fabrication_weight:.2f}) -> total={composite_penalty:.4f}")
        
        # Safety guards to prevent runaway values
        composite_penalty = float(np.clip(composite_penalty, 1e-6, 1e6))
        if not np.isfinite(composite_penalty):
            raise ValueError(f"Non-finite composite penalty: {composite_penalty}")
        
        # Convert to maximization score for DANTE (higher is better)
        composite_score = 1000.0 / (composite_penalty + 1.0)
        
        # Final safety check
        if not np.isfinite(composite_score):
            raise ValueError(f"Non-finite composite score: {composite_score}")
        
        if track:
            self.tracker.track(composite_score, x)
            # Also track individual scores for analysis (if tracker supports metadata)
            try:
                self.tracker.track_metadata({
                    "energy_score": energy_score,
                    "cascade_penalty": cascade_penalty,
                    "thermal_score": thermal_score,
                    "fabrication_score": fabrication_score,
                    "composite_penalty": composite_penalty,
                    "energy_fJ": result["XOR"]["fanout_adjusted_energy_fJ"],
                    "cascade_depth": result["XOR"]["effective_cascade_depth"],
                    "power_mW": result["XOR"]["effective_P_ctrl_mW"],
                    "platform": result["XOR"]["platform"]
                })
            except AttributeError:
                # Tracker doesn't support metadata, skip
                pass
        
        return composite_score if not apply_scaling else self.scaled(composite_score)




def create_photonic_optimizer(
    objective_type: str = "multi",
    energy_weight: float = 0.4,
    cascade_weight: float = 0.3,
    thermal_weight: float = 0.2,
    fabrication_weight: float = 0.1,
    dims: int = 12,
    cascade_min_stages: int = 8,
    cascade_target_stages: int = 12,
    cascade_hard_penalty: float = 3.0,
    cascade_band_penalty: float = 0.5,
    **kwargs
) -> PhotonicObjectiveBase:
    """
    Factory function to create photonic optimizers.
    
    Args:
        objective_type: Type of optimizer ("energy", "cascade", "thermal", "multi")
        energy_weight: Weight for energy objective (multi-objective only)
        cascade_weight: Weight for cascade objective (multi-objective only)
        thermal_weight: Weight for thermal objective (multi-objective only)
        fabrication_weight: Weight for fabrication objective (multi-objective only)
        dims: Number of optimization dimensions
        cascade_min_stages: Minimum cascade stages (hard penalty below this)
        cascade_target_stages: Target cascade stages (soft penalty around this)
        cascade_hard_penalty: Strength of shallow cascade penalty
        cascade_band_penalty: Strength of target band penalty
        
    Returns:
        Configured photonic optimizer
    """
    if objective_type == "energy":
        return PhotonicEnergyOptimizer(dims=min(dims, 8))
    elif objective_type == "cascade":
        return PhotonicCascadeOptimizer(dims=min(dims, 8))
    elif objective_type == "thermal":
        return PhotonicThermalOptimizer(dims=min(dims, 8))
    elif objective_type == "multi":
        optimizer = PhotonicMultiObjective(
            dims=dims,
            energy_weight=energy_weight,
            cascade_weight=cascade_weight,
            thermal_weight=thermal_weight,
            fabrication_weight=fabrication_weight,
            cascade_min_stages=cascade_min_stages,
            cascade_target_stages=cascade_target_stages,
            cascade_hard_penalty=cascade_hard_penalty,
            cascade_band_penalty=cascade_band_penalty
        )
        # Set verbose flag if provided
        optimizer._verbose = kwargs.get('verbose', False)
        return optimizer
    else:
        raise ValueError(f"Unknown objective type: {objective_type}")


def run_photonic_optimization(
    objective_type: str = "multi",
    num_initial_samples: int = 16,  # Increased for better surrogate stability
    num_acquisitions: int = 8,     # Balanced for good results
    samples_per_acquisition: int = 4,  # Increased for better exploration
    timeout_seconds: int = 30,     # Add timeout protection
    **kwargs
) -> Dict[str, Any]:
    """
    Run DANTE optimization for photonic logic circuits with explicit budget tracking and stop reasons.
    
    Args:
        objective_type: Type of optimization ("energy", "cascade", "thermal", "multi")
        num_initial_samples: Number of initial random samples
        num_acquisitions: Number of DANTE acquisition iterations
        samples_per_acquisition: Number of samples per acquisition
        timeout_seconds: Maximum time to spend on optimization
        **kwargs: Additional arguments for optimizer configuration
        
    Returns:
        Optimization results including best configurations and stop reason
    """
    import time
    start_time = time.time()
    
    # Calculate and log budget
    max_evals = num_initial_samples + (num_acquisitions * samples_per_acquisition)
    print(f"Budget: max_evals={max_evals} (initial={num_initial_samples} + acquisitions={num_acquisitions} * samples_per_acquisition={samples_per_acquisition})")
    
    stop_reason = None
    
    try:
        # Import DANTE components with fallback
        try:
            from dante.neural_surrogate import AckleySurrogateModel
            from dante.tree_exploration import TreeExploration
            from dante.utils import generate_initial_samples
            dante_available = True
        except ImportError:
            dante_available = False
        
        # Create objective function
        obj_function = create_photonic_optimizer(objective_type, **kwargs)
        
        # Fallback to simple optimization if DANTE not available
        if not dante_available:
            result = _run_simple_optimization(
                obj_function, num_initial_samples, num_acquisitions, 
                samples_per_acquisition, timeout_seconds
            )
            result["stop_reason"] = "DANTE not available, used fallback"
            return result
        
        # Generate initial samples with timeout check
        input_x, input_y = generate_initial_samples(
            obj_function, num_init_samples=num_initial_samples, apply_scaling=True
        )
        
        total_evals = len(input_y)
        
        if time.time() - start_time > timeout_seconds:
            result = _create_timeout_result(input_x, input_y, objective_type, "Initial sampling")
            result["stop_reason"] = f"Timeout during initial sampling ({total_evals}/{max_evals} evals)"
            return result
        
        # Track best solutions
        best_solutions = []
        no_improve_count = 0
        best_score_so_far = float('-inf')
        
        # Create robust surrogate model based on dataset size with enhanced safety
        from ..utils.optimize_utils import build_robust_surrogate, add_exploration_noise, safe_convergence_check, last_n
        from ..optimization.surrogates import SklearnSurrogateWrapper
        from ..opt_utils.array_safety import ensure_1d, ensure_2d_row
        
        # Use enhanced surrogate wrapper for bulletproof array handling
        surrogate = build_robust_surrogate(len(input_y), obj_function.dims)
        
        # Add exploration noise to prevent constant targets and ensure arrays
        input_y = ensure_1d(add_exploration_noise(ensure_1d(input_y)))
        input_x = ensure_2d_row(input_x) if np.asarray(input_x).ndim == 1 else np.asarray(input_x)
        
        # Integer neighbor exploration constants
        STAGE_IDX, STAGES_MIN, STAGES_MAX = 7, 8, 24
        
        def _write_stage_in_scale(vec, stages, lb, ub):
            """Write stage value back in the scale used by the optimizer."""
            v = list(vec)
            # Support normalized or absolute internal representation
            if 0.0 - 1e-9 <= v[STAGE_IDX] <= 1.0 + 1e-9 and (ub[STAGE_IDX] - lb[STAGE_IDX]) > 1.0:
                v[STAGE_IDX] = (stages - lb[STAGE_IDX]) / (ub[STAGE_IDX] - lb[STAGE_IDX])
            else:
                v[STAGE_IDX] = float(stages)
            return v
        
        def augment_stage_neighbors(cands, incumbent_stage, lb, ub, k_local=4, k_global=2):
            """Add integer neighbors around incumbent stage for better discrete exploration."""
            aug = []
            # Local neighbors ±{1,2,3}
            for delta in (-3, -2, -1, 1, 2, 3):
                s = int(np.clip(incumbent_stage + delta, STAGES_MIN, STAGES_MAX))
                aug.append(_write_stage_in_scale(cands[0], s, lb, ub))
                if len(aug) >= k_local:
                    break
            # Global diversity
            for _ in range(k_global):
                s = int(np.random.randint(STAGES_MIN, STAGES_MAX + 1))
                aug.append(_write_stage_in_scale(cands[0], s, lb, ub))
            return cands + aug
        
        # Track best configuration for neighbor exploration
        best_config = {}
        
        # Main optimization loop with explicit budget tracking
        for i in range(num_acquisitions):
            # Check stopping conditions with explicit reasons
            if total_evals >= max_evals:
                stop_reason = f"Reached evaluation budget ({total_evals}/{max_evals})"
                break
                
            if time.time() - start_time > timeout_seconds:
                stop_reason = f"Timeout reached after {i} iterations ({total_evals}/{max_evals} evals)"
                break
            
            # Train surrogate model with timeout resilience
            surrogate_ok = True
            try:
                trained_surrogate = surrogate(input_x, input_y)
                
                if time.time() - start_time > timeout_seconds:
                    stop_reason = f"Timeout during surrogate training ({total_evals}/{max_evals} evals)"
                    break
                    
            except Exception as e:
                error_msg = str(e).lower()
                if "timeout" in error_msg or "timed out" in error_msg:
                    print(f"Warning: Surrogate training timed out at iteration {i+1}, using Sobol-only sampling")
                    surrogate_ok = False
                else:
                    stop_reason = f"Surrogate training error: {e} ({total_evals}/{max_evals} evals)"
                    break
            
            # Determine sampling strategy based on surrogate success
            remaining_budget = max_evals - total_evals
            actual_samples = min(samples_per_acquisition, remaining_budget)
            
            if actual_samples <= 0:
                stop_reason = f"No budget remaining ({total_evals}/{max_evals} evals)"
                break
            
            # Generate new samples based on surrogate availability
            if not surrogate_ok:
                # Use Sobol sampling when surrogate failed
                print(f"Using Sobol-only sampling for iteration {i+1}")
                from scipy.stats import qmc
                sobol = qmc.Sobol(d=obj_function.dims, scramble=True)
                sobol_samples = sobol.random(actual_samples)
                new_x = obj_function.lb + sobol_samples * (obj_function.ub - obj_function.lb)
            else:
                # Use tree exploration when surrogate is available
                try:
                    # Create tree explorer
                    tree_explorer = TreeExploration(
                        func=obj_function, 
                        model=trained_surrogate, 
                        num_samples_per_acquisition=samples_per_acquisition
                    )
                    
                    # Try tree exploration with timeout fallback to Sobol sampling
                    try:
                        new_x = tree_explorer.rollout(input_x, input_y, iteration=i)
                        
                        if time.time() - start_time > timeout_seconds:
                            stop_reason = f"Timeout during tree exploration ({total_evals}/{max_evals} evals)"
                            break
                            
                    except Exception as e:
                        error_msg = str(e).lower()
                        if "timeout" in error_msg or "timed out" in error_msg:
                            print(f"Warning: Tree exploration timed out at iteration {i+1}, using Sobol fallback")
                            # Generate Sobol samples as fallback
                            from scipy.stats import qmc
                            sobol = qmc.Sobol(d=obj_function.dims, scramble=True)
                            sobol_samples = sobol.random(actual_samples)
                            # Scale to bounds
                            new_x = obj_function.lb + sobol_samples * (obj_function.ub - obj_function.lb)
                        else:
                            # Re-raise non-timeout errors
                            raise e
                            
                except Exception as e:
                    stop_reason = f"Tree exploration error: {e} ({total_evals}/{max_evals} evals)"
                    break
            
            # Add integer neighbor exploration for stages
            if i > 0 and len(new_x) > 0:  # Skip first iteration, need incumbent
                inc_stage = int(best_config.get("stages", STAGES_MIN))
                new_x = augment_stage_neighbors(new_x.tolist(), inc_stage, obj_function.lb, obj_function.ub)
                new_x = np.array(new_x)
                
                # Optional: Show stage diversity in verbose mode
                if kwargs.get('verbose', False):
                    stages_seen = []
                    for v in new_x:
                        val = v[STAGE_IDX]
                        if 0.0 <= val <= 1.0 and (obj_function.ub[STAGE_IDX] - obj_function.lb[STAGE_IDX]) > 1.0:
                            val = obj_function.lb[STAGE_IDX] + val * (obj_function.ub[STAGE_IDX] - obj_function.lb[STAGE_IDX])
                        stages_seen.append(int(np.round(np.clip(val, STAGES_MIN, STAGES_MAX))))
                    hist = {s: stages_seen.count(s) for s in sorted(set(stages_seen))}
                    print(f"Proposal stages histogram: {hist}")
            
            # Limit evaluations to remaining budget
            if len(new_x) > actual_samples:
                new_x = new_x[:actual_samples]
            
            new_y = np.array([obj_function(x, apply_scaling=True) for x in new_x])
            total_evals += len(new_y)
            
            # Update dataset
            input_x = np.concatenate((input_x, new_x), axis=0)
            input_y = np.concatenate((input_y, new_y))
            
            # Track progress and improvement
            current_best = np.max(input_y)
            if current_best > best_score_so_far + 1e-6:  # Meaningful improvement
                best_score_so_far = current_best
                no_improve_count = 0
            else:
                no_improve_count += 1
            
            best_idx = np.argmax(input_y)
            
            # Update best configuration for neighbor exploration
            best_params = input_x[best_idx]
            if len(best_params) >= 8:
                best_config = {
                    "stages": max(8, min(24, int(np.round(best_params[7]))))
                }
            
            best_solutions.append({
                "iteration": i,
                "best_score": input_y[best_idx],
                "best_params": input_x[best_idx].tolist(),
                "num_evaluations": total_evals
            })
            
            print(f"Iteration {i+1}/{num_acquisitions}: Best score = {input_y[best_idx]:.4f}, Evaluations = {total_evals}/{max_evals}")
            
            # Early stopping for convergence
            if i > 3 and safe_convergence_check(input_y, window=5, tolerance=1e-3):
                stop_reason = f"Converged after {i+1} iterations ({total_evals}/{max_evals} evals)"
                break
            
            # Plateau detection
            if no_improve_count >= 5:
                stop_reason = f"No improvement for 5 iterations ({total_evals}/{max_evals} evals)"
                break
        
        # Set default stop reason if loop completed normally
        if stop_reason is None:
            stop_reason = f"Completed all {num_acquisitions} iterations ({total_evals}/{max_evals} evals)"
        
        print(f"Optimization completed! Reason: {stop_reason}")
        
        # Return optimization results with explicit stop reason
        best_idx = np.argmax(input_y)
        return {
            "best_score": input_y[best_idx],
            "best_parameters": input_x[best_idx],
            "optimization_history": best_solutions,
            "all_evaluations": {"x": input_x, "y": input_y},
            "objective_type": objective_type,
            "total_evaluations": total_evals,
            "max_evaluations": max_evals,
            "runtime_seconds": time.time() - start_time,
            "stop_reason": stop_reason
        }
        
    except Exception as e:
        # Fallback to simple optimization on any error
        print(f"DANTE optimization failed: {e}")
        result = _run_simple_optimization(
            create_photonic_optimizer(objective_type, **kwargs),
            num_initial_samples, num_acquisitions, samples_per_acquisition, timeout_seconds
        )
        result["stop_reason"] = f"DANTE failed ({e}), used fallback"
        return result


def _run_simple_optimization(
    obj_function, num_initial_samples: int, num_acquisitions: int,
    samples_per_acquisition: int, timeout_seconds: int
) -> Dict[str, Any]:
    """Fallback simple optimization when DANTE is not available or fails."""
    import time
    start_time = time.time()
    
    print("Using fallback simple optimization...")
    
    # Generate random samples within bounds
    input_x = []
    input_y = []
    
    total_samples = num_initial_samples + (num_acquisitions * samples_per_acquisition)
    
    for i in range(total_samples):
        if time.time() - start_time > timeout_seconds:
            print(f"Timeout reached after {i} samples")
            break
        
        # Generate random sample within bounds
        x = np.random.uniform(obj_function.lb, obj_function.ub)
        y = obj_function(x, apply_scaling=True)
        
        input_x.append(x)
        input_y.append(y)
        
        if i % 5 == 0:  # Progress every 5 samples
            best_idx = np.argmax(input_y)
            print(f"Sample {i+1}/{total_samples}: Best score = {input_y[best_idx]:.4f}")
    
    input_x = np.array(input_x)
    input_y = np.array(input_y)
    
    best_idx = np.argmax(input_y)
    return {
        "best_score": input_y[best_idx],
        "best_parameters": input_x[best_idx],
        "optimization_history": [{"iteration": 0, "best_score": input_y[best_idx], 
                                "best_params": input_x[best_idx].tolist(), 
                                "num_evaluations": len(input_y)}],
        "all_evaluations": {"x": input_x, "y": input_y},
        "objective_type": "simple_fallback",
        "total_evaluations": len(input_y),
        "runtime_seconds": time.time() - start_time
    }


def _create_timeout_result(input_x, input_y, objective_type: str, stage: str) -> Dict[str, Any]:
    """Create result when timeout occurs."""
    best_idx = np.argmax(input_y) if len(input_y) > 0 else 0
    return {
        "best_score": input_y[best_idx] if len(input_y) > 0 else 0.0,
        "best_parameters": input_x[best_idx] if len(input_x) > 0 else np.zeros(8),
        "optimization_history": [],
        "all_evaluations": {"x": input_x, "y": input_y},
        "objective_type": objective_type,
        "total_evaluations": len(input_y),
        "timeout_stage": stage,
        "runtime_seconds": 30.0
    }
