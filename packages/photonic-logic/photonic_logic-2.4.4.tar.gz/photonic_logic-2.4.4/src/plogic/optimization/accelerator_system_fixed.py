"""
Level 4 System-Level Photonic AI Accelerator Optimization (FIXED VERSION)

This module implements production-ready optimization for the mobile photonic AI accelerator,
with comprehensive fixes for score tracking, TOPS calculation, and power transparency.
"""

import sys
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple, Union
import numpy as np
import json
import warnings
from pathlib import Path
from datetime import datetime

# Add DANTE to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'DANTE'))
from dante.obj_functions import ObjectiveFunction
from dante.utils import Tracker

# Import photonic logic components
from ..controller import ExperimentController, PhotonicMolecule
from ..materials.platforms import PlatformDB

# Import our fixes
from .optimizer_fixes_v2 import (
    BestState, 
    safe_mape, 
    create_unique_run_dir,
    print_architecture_totals,
    run_optimization_with_fixes
)
from .physics_validation import tops_from_spec, power_from_spec


@dataclass
class AcceleratorConfig:
    """Configuration for the photonic AI accelerator system."""
    
    # System architecture - FIXED: Correct ring count
    num_rings: int = 1260  # 35×36 array per the spec
    array_config: Tuple[int, int] = (35, 36)  # Actual array size
    num_lanes: int = 24  # 24 lanes per spec
    num_tiles: int = 4   # 4x4 tile configuration
    
    # Array scope configuration
    array_scope: str = "global"  # "global" or "per_lane"
    
    # Power constraints (mobile)
    total_power_budget_W: float = 2.0  # Hard mobile limit
    laser_power_budget_W: float = 0.53  # 4x QDFB lasers
    ring_tuning_budget_W: float = 0.20  # rings × 50µW
    sram_power_budget_W: float = 0.35   # 3D-stacked SRAM
    
    # Performance targets - FIXED: Realistic targets
    target_sustained_tops: float = 2.06  # Correct calculation
    target_token_rate: float = 50.0  # tok/s for 7B model
    target_latency_ms: float = 10.0  # Maximum inference latency
    
    # Manufacturing constraints
    target_yield: float = 0.8  # 80% functional rings
    cd_variation_nm: float = 5.0  # ±5nm critical dimension
    wavelength_drift_pm: float = 5.0  # <5pm drift over 1 hour
    
    # Thermal constraints
    max_die_temp_C: float = 85.0  # Mobile operating temperature
    thermal_gradient_limit: float = 10.0  # °C across die
    heater_power_limit_uW: float = 50.0  # Per ring
    
    # Fabrication process
    platform: str = "AlGaAs"  # AlGaAsOI platform
    process_node: str = "150nm"  # Initial prototyping
    wafer_size_mm: int = 150  # 150mm → 200mm scaling
    
    # Integration specs
    sram_capacity_MB: int = 512  # 3D-stacked SRAM
    sram_bandwidth_TBps: float = 2.0  # Cu-Cu bonding bandwidth
    package_type: str = "InFO_oS"  # TSMC InFO on Substrate


@dataclass
class ManufacturingModel:
    """Manufacturing and yield modeling for the accelerator."""
    
    # Process parameters
    cd_mean_nm: float = 220.0  # Target critical dimension
    cd_std_nm: float = 2.0     # Process variation (3σ = ±6nm)
    sidewall_roughness_nm: float = 1.5  # RMS sidewall roughness
    
    # Yield parameters
    ring_yield_probability: float = 0.85  # Individual ring yield
    cluster_defect_rate: float = 0.02     # Clustered defects per cm²
    die_area_cm2: float = 0.25            # 5mm × 5mm die
    
    # Cost model
    wafer_cost_USD: int = 8000            # 150mm AlGaAsOI wafer
    dies_per_wafer: int = 50              # Conservative estimate
    packaging_cost_USD: int = 15          # InFO_oS packaging
    test_time_minutes: float = 2.0        # Calibration time per die
    
    def compute_die_yield(self) -> float:
        """Compute overall die yield including clustered defects."""
        # Individual ring yield
        ring_yield = self.ring_yield_probability
        
        # Clustered defect yield (Poisson model)
        cluster_yield = np.exp(-self.cluster_defect_rate * self.die_area_cm2)
        
        # Combined yield for minimum functional rings
        min_functional = 1000  # Need at least 1000 of 1260 rings
        total_rings = 1260
        
        # Binomial probability of having at least min_functional rings
        from scipy.stats import binom
        functional_yield = 1 - binom.cdf(min_functional - 1, total_rings, ring_yield)
        
        return functional_yield * cluster_yield
    
    def compute_unit_cost(self, volume: int = 1000) -> float:
        """Compute unit cost including yield and volume effects."""
        die_yield = self.compute_die_yield()
        
        # Die cost
        die_cost = self.wafer_cost_USD / (self.dies_per_wafer * die_yield)
        
        # Volume pricing (learning curve effect)
        volume_factor = max(0.5, 1000 / volume) ** 0.2  # 20% learning curve
        
        # Total unit cost
        total_cost = (die_cost + self.packaging_cost_USD) * volume_factor
        
        return total_cost


@dataclass
class ThermalModel:
    """Thermal modeling for the accelerator system."""
    
    # Die thermal properties
    die_size_mm: float = 5.0
    die_thickness_um: float = 200.0
    thermal_conductivity: float = 55.0  # AlGaAs W/m·K
    
    # Heat sources
    laser_power_W: float = 0.53
    ring_power_W: float = 0.20
    sram_power_W: float = 0.35
    
    # Thermal constraints
    max_temp_C: float = 85.0
    ambient_temp_C: float = 35.0  # Mobile ambient
    max_gradient_C: float = 10.0
    
    def __post_init__(self):
        """Initialize thermal resistance network."""
        # Simplified thermal resistance model
        # In production, this would import COMSOL data
        self.thermal_resistance = self._compute_thermal_resistance()
    
    def _compute_thermal_resistance(self) -> float:
        """Compute thermal resistance from die to ambient."""
        # Simplified model: R_th = thickness / (k * area)
        area_m2 = (self.die_size_mm * 1e-3) ** 2
        thickness_m = self.die_thickness_um * 1e-6
        
        return thickness_m / (self.thermal_conductivity * area_m2)
    
    def compute_die_temperature(self, total_power_W: float) -> float:
        """Compute peak die temperature."""
        return self.ambient_temp_C + total_power_W * self.thermal_resistance
    
    def compute_thermal_gradient(self, power_map: np.ndarray) -> float:
        """Compute thermal gradient across die (simplified)."""
        # In production, this would use detailed FEM analysis
        power_std = np.std(power_map)
        return power_std * self.thermal_resistance * 10  # Empirical factor
    
    def is_thermally_feasible(self, total_power_W: float, power_map: np.ndarray) -> bool:
        """Check if configuration meets thermal constraints."""
        peak_temp = self.compute_die_temperature(total_power_W)
        gradient = self.compute_thermal_gradient(power_map)
        
        return (peak_temp <= self.max_temp_C and 
                gradient <= self.max_gradient_C)


@dataclass
class SystemPerformanceModel:
    """Performance modeling for the full accelerator system (FIXED)."""
    
    # Architecture parameters - FIXED values
    rows: int = 35
    cols: int = 36
    lanes: int = 24
    macs_per_ring: int = 2
    clock_freq_GHz: float = 1.0
    array_scope: str = "global"  # "global" or "per_lane"
    
    # Memory system
    sram_bandwidth_TBps: float = 2.0
    sram_latency_ns: float = 5.0
    
    # Optical parameters
    modulation_bandwidth_GHz: float = 10.0
    optical_loss_budget_dB: float = 15.0
    
    def compute_peak_tops(self) -> float:
        """Compute peak TOPS performance using correct formula."""
        # Use the validated physics calculation
        tops, total_rings = tops_from_spec(
            rows=self.rows,
            cols=self.cols,
            lanes=self.lanes,
            macs_per_ring=self.macs_per_ring,
            clock_ghz=self.clock_freq_GHz,
            utilization=1.0,
            array_scope=self.array_scope
        )
        return tops
    
    def compute_sustained_tops(self, power_budget_W: float, thermal_model: ThermalModel) -> float:
        """Compute sustained TOPS under thermal constraints."""
        peak_tops = self.compute_peak_tops()
        
        # Thermal throttling factor
        if thermal_model.compute_die_temperature(power_budget_W) > thermal_model.max_temp_C:
            # Linear throttling model
            throttle_factor = thermal_model.max_temp_C / thermal_model.compute_die_temperature(power_budget_W)
        else:
            throttle_factor = 1.0
        
        return peak_tops * throttle_factor
    
    def compute_token_rate(self, model_size_B: int = 7, sustained_tops: float = None) -> float:
        """Compute token generation rate for LLM inference."""
        if sustained_tops is None:
            sustained_tops = self.compute_peak_tops()
        
        # Empirical model: tok/s ≈ TOPS / (model_size_B * complexity_factor)
        complexity_factor = 0.1  # Empirical for transformer models
        
        return sustained_tops / (model_size_B * complexity_factor)


@dataclass
class PhotonicAcceleratorOptimizer(ObjectiveFunction):
    """Level 4 system-level optimization for photonic AI accelerator (FIXED)."""
    
    dims: int = 25
    turn: float = 0.01
    name: str = "photonic_accelerator_l4_fixed"
    
    # System models
    config: AcceleratorConfig = field(default_factory=AcceleratorConfig)
    manufacturing: ManufacturingModel = field(default_factory=ManufacturingModel)
    thermal: ThermalModel = field(default_factory=ThermalModel)
    performance: SystemPerformanceModel = field(default_factory=SystemPerformanceModel)
    
    # Best state tracking
    best_state: BestState = field(default_factory=BestState)
    
    def __post_init__(self):
        """Initialize system-level optimization parameters."""
        # Extended parameter space for full accelerator system:
        # [0-2]: Ring array geometry (rows, cols, spacing_um)
        # [3-5]: Optical parameters (wavelength_nm, power_per_lane_mW, loss_budget_dB)
        # [6-8]: Thermal parameters (heater_power_uW, thermal_time_constant, gradient_limit)
        # [9-11]: Manufacturing (cd_target_nm, yield_target, process_corner)
        # [12-14]: System architecture (num_lanes, clock_freq_GHz, sram_config)
        # [15-17]: Power distribution (laser_power_W, ring_power_W, sram_power_W)
        # [18-20]: Performance targets (sustained_tops, token_rate, latency_ms)
        # [21-24]: Integration (package_type, test_time_min, calibration_points, compiler_config)
        
        self.lb = np.array([
            # Ring geometry (realistic bounds)
            32, 32, 8.0,
            # Optical (FIXED: proper telecom wavelengths and realistic power)
            1530, 15, 12,
            # Thermal (FIXED: realistic heater power and timing in microseconds)
            30, 5.0, 8.0,
            # Manufacturing (FIXED: realistic CD and yield)
            200, 0.6, 0,
            # Architecture (FIXED: realistic lanes and clock in GHz, not MHz)
            12, 0.5, 256,
            # Power (mobile constraints)
            0.4, 0.15, 0.25,
            # Performance (FIXED: realistic targets)
            1.0, 20, 8.0,
            # Integration (realistic test and calibration)
            0, 1.0, 8, 0
        ])
        
        self.ub = np.array([
            # Ring geometry
            64, 64, 15.0,
            # Optical (FIXED: telecom C-band only)
            1570, 35, 20,
            # Thermal (FIXED: microseconds, not scientific notation)
            80, 50.0, 15.0,
            # Manufacturing (FIXED: standard silicon photonics CD range)
            250, 0.85, 2,
            # Architecture (FIXED: realistic clock frequencies)
            25, 2.0, 768,
            # Power (strict mobile limits)
            0.7, 0.25, 0.45,
            # Performance (FIXED: achievable targets)
            5.0, 60, 15.0,
            # Integration
            2, 3.0, 32, 2
        ])
        
        self.tracker = Tracker(self.name + str(self.dims))
        
        # Parameter names for debugging
        self.param_names = [
            "array_rows", "array_cols", "ring_spacing_um",
            "wavelength_nm", "power_per_lane_mW", "loss_budget_dB",
            "heater_power_uW", "thermal_tau_us", "gradient_limit_C",
            "cd_target_nm", "yield_target", "process_corner",
            "num_lanes", "clock_freq_GHz", "sram_config",
            "laser_power_W", "ring_power_W", "sram_power_W",
            "target_sustained_tops", "target_token_rate", "target_latency_ms",
            "package_type", "test_time_min", "calibration_points", "compiler_config"
        ]
    
    def scaled(self, y: float) -> float:
        """Scale composite score for DANTE optimization."""
        return max(0, y)
    
    def _extract_parameters(self, x: np.ndarray) -> Dict[str, Any]:
        """Extract and validate parameters from optimization vector."""
        params = {}
        
        # Ring array geometry - FIXED to actual spec
        params["array_rows"] = 35  # Fixed per spec
        params["array_cols"] = 36  # Fixed per spec
        params["ring_spacing_um"] = float(x[2])
        
        # Optical parameters
        params["wavelength_nm"] = float(x[3])
        params["power_per_lane_mW"] = float(x[4])
        params["loss_budget_dB"] = float(x[5])
        
        # Thermal parameters
        params["heater_power_uW"] = float(x[6])
        params["thermal_tau_us"] = float(x[7])
        params["gradient_limit_C"] = float(x[8])
        
        # Manufacturing parameters
        params["cd_target_nm"] = float(x[9])
        params["yield_target"] = float(x[10])
        params["process_corner"] = int(np.clip(x[11], 0, 2))  # SS/TT/FF
        
        # System architecture - FIXED lanes to 24
        params["num_lanes"] = 24  # Fixed per spec
        params["clock_freq_GHz"] = float(x[13])
        params["sram_config"] = int(np.clip(x[14], 256, 1024))
        
        # Power distribution
        params["laser_power_W"] = float(x[15])
        params["ring_power_W"] = float(x[16])
        params["sram_power_W"] = float(x[17])
        
        # Performance targets
        params["target_sustained_tops"] = float(x[18])
        params["target_token_rate"] = float(x[19])
        params["target_latency_ms"] = float(x[20])
        
        # Integration parameters
        params["package_type"] = int(np.clip(x[21], 0, 2))
        params["test_time_min"] = float(x[22])
        params["calibration_points"] = int(np.clip(x[23], 8, 32))
        params["compiler_config"] = int(np.clip(x[24], 0, 2))
        
        return params
    
    def _compute_system_power(self, params: Dict[str, Any]) -> Dict[str, float]:
        """Compute total system power consumption with breakdown."""
        # Use validated physics calculation
        power_breakdown = power_from_spec(
            heater_power_W=params["ring_power_W"],
            laser_power_W=params["laser_power_W"],
            dsp_sram_power_W=params["sram_power_W"],
            misc_power_W=0.8  # ADC/DAC + control
        )
        
        return power_breakdown
    
    def _compute_manufacturing_yield(self, params: Dict[str, Any]) -> float:
        """Compute manufacturing yield with process variations."""
        # More realistic yield model for production optimization
        base_yield = params["yield_target"]
        
        # CD variation impact (less pessimistic)
        cd_variation = params["cd_target_nm"] * 0.015  # 1.5% variation (more realistic)
        wavelength_shift = cd_variation * 1.5  # Reduced sensitivity
        
        # Yield degradation from wavelength shift (less severe)
        if wavelength_shift > 15.0:  # Increased tolerance
            yield_penalty = 0.7  # Less severe penalty
        else:
            yield_penalty = 1.0 - wavelength_shift / 30.0  # Reduced penalty
        
        # Process corner effects (less pessimistic)
        corner_factors = [0.9, 1.0, 0.95]  # SS, TT, FF (improved)
        corner_factor = corner_factors[params["process_corner"]]
        
        # Final yield calculation
        final_yield = base_yield * yield_penalty * corner_factor
        
        # Ensure minimum realistic yield for optimization
        return max(0.3, final_yield)  # Floor at 30% for optimization purposes
    
    def _compute_thermal_performance(self, params: Dict[str, Any]) -> Tuple[float, bool]:
        """Compute thermal performance and feasibility."""
        power_breakdown = self._compute_system_power(params)
        total_power = power_breakdown["total_W"]
        
        # Thermal model
        thermal_model = ThermalModel()
        peak_temp = thermal_model.compute_die_temperature(total_power)
        
        # Power distribution map (simplified)
        num_rings = 1260  # Fixed
        power_per_ring = params["ring_power_W"] / num_rings
        power_map = np.full((35, 36), power_per_ring)
        
        # Add laser hot spots
        power_map[0:4, 0:4] += params["laser_power_W"] / 16  # Laser region
        
        gradient = thermal_model.compute_thermal_gradient(power_map)
        thermal_feasible = thermal_model.is_thermally_feasible(total_power, power_map)
        
        return peak_temp, thermal_feasible
    
    def _compute_sustained_performance(self, params: Dict[str, Any]) -> float:
        """Compute sustained performance under realistic constraints."""
        # Update performance model with correct values
        self.performance.rows = 35
        self.performance.cols = 36
        self.performance.lanes = 24
        self.performance.clock_freq_GHz = params["clock_freq_GHz"]
        self.performance.array_scope = self.config.array_scope
        
        peak_tops = self.performance.compute_peak_tops()
        
        # Thermal throttling
        power_breakdown = self._compute_system_power(params)
        total_power = power_breakdown["total_W"]
        thermal_model = ThermalModel()
        sustained_tops = self.performance.compute_sustained_tops(total_power, thermal_model)
        
        # Yield impact on performance
        yield_factor = self._compute_manufacturing_yield(params)
        effective_tops = sustained_tops * yield_factor
        
        return effective_tops
    
    def _compute_cost_performance_ratio(self, params: Dict[str, Any]) -> float:
        """Compute cost-performance ratio ($/TOPS)."""
        sustained_tops = self._compute_sustained_performance(params)
        unit_cost = self.manufacturing.compute_unit_cost(volume=10000)  # 10K volume
        
        if sustained_tops <= 0:
            return 1e6  # Very high cost for invalid configs
        
        return unit_cost / sustained_tops
    
    def _compute_mobile_suitability_score(self, params: Dict[str, Any]) -> float:
        """Compute mobile suitability score (0-100)."""
        power_breakdown = self._compute_system_power(params)
        total_power = power_breakdown["total_W"]
        peak_temp, thermal_feasible = self._compute_thermal_performance(params)
        sustained_tops = self._compute_sustained_performance(params)
        
        # Power score (0-100)
        if total_power <= 1.5:
            power_score = 100
        elif total_power >= 2.5:
            power_score = 0
        else:
            power_score = 100 * (2.5 - total_power) / 1.0
        
        # Thermal score (0-100)
        if thermal_feasible and peak_temp <= 75:
            thermal_score = 100
        elif not thermal_feasible:
            thermal_score = 0
        else:
            thermal_score = 100 * (85 - peak_temp) / 10
        
        # Performance score (0-100)
        if sustained_tops >= 2.0:  # Adjusted for realistic target
            perf_score = 100
        elif sustained_tops <= 1.0:
            perf_score = 0
        else:
            perf_score = 100 * (sustained_tops - 1.0) / 1.0
        
        # Weighted mobile score
        mobile_score = 0.4 * power_score + 0.3 * thermal_score + 0.3 * perf_score
        
        return mobile_score
    
    def _compute_manufacturing_feasibility_score(self, params: Dict[str, Any]) -> float:
        """Compute manufacturing feasibility score (0-100)."""
        yield_factor = self._compute_manufacturing_yield(params)
        unit_cost = self.manufacturing.compute_unit_cost(volume=10000)
        
        # Yield score
        yield_score = yield_factor * 100
        
        # Cost score (target <$50)
        if unit_cost <= 30:
            cost_score = 100
        elif unit_cost >= 100:
            cost_score = 0
        else:
            cost_score = 100 * (100 - unit_cost) / 70
        
        # Test time score (target <2 minutes)
        test_time = params["test_time_min"]
        if test_time <= 1.0:
            test_score = 100
        elif test_time >= 5.0:
            test_score = 0
        else:
            test_score = 100 * (5.0 - test_time) / 4.0
        
        # Weighted manufacturing score
        mfg_score = 0.5 * yield_score + 0.3 * cost_score + 0.2 * test_score
        
        return mfg_score
    
    def _run_system_simulation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run full system simulation with all constraints."""
        try:
            # System power analysis with breakdown
            power_breakdown = self._compute_system_power(params)
            total_power = power_breakdown["total_W"]
            
            # Thermal analysis
            peak_temp, thermal_feasible = self._compute_thermal_performance(params)
            
            # Performance analysis with correct TOPS
            sustained_tops = self._compute_sustained_performance(params)
            token_rate = self.performance.compute_token_rate(sustained_tops=sustained_tops)
            
            # Manufacturing analysis
            yield_factor = self._compute_manufacturing_yield(params)
            unit_cost = self.manufacturing.compute_unit_cost(volume=10000)
            
            # Mobile suitability
            mobile_score = self._compute_mobile_suitability_score(params)
            mfg_score = self._compute_manufacturing_feasibility_score(params)
            
            return {
                "total_power_W": total_power,
                "power_breakdown": power_breakdown,  # Added breakdown
                "peak_temp_C": peak_temp,
                "thermal_feasible": thermal_feasible,
                "sustained_tops": sustained_tops,
                "token_rate_per_s": token_rate,
                "yield_factor": yield_factor,
                "unit_cost_USD": unit_cost,
                "mobile_score": mobile_score,
                "manufacturing_score": mfg_score,
                "cost_per_tops": unit_cost / max(sustained_tops, 0.1),
                "power_efficiency_tops_per_w": sustained_tops / max(total_power, 0.1),
                "valid_config": (
                    total_power <= self.config.total_power_budget_W and
                    thermal_feasible and
                    sustained_tops >= 1.0 and
                    yield_factor >= 0.5
                )
            }
            
        except Exception as e:
            # Return penalty result for failed simulations
            return {
                "total_power_W": 10.0,
                "power_breakdown": {"heaters_W": 0, "lasers_W": 0, "dsp_sram_W": 0, "misc_W": 0, "total_W": 10.0},
                "peak_temp_C": 150.0,
                "thermal_feasible": False,
                "sustained_tops": 0.0,
                "token_rate_per_s": 0.0,
                "yield_factor": 0.0,
                "unit_cost_USD": 1000.0,
                "mobile_score": 0.0,
                "manufacturing_score": 0.0,
                "cost_per_tops": 1e6,
                "power_efficiency_tops_per_w": 0.0,
                "valid_config": False
            }
    
    def __call__(self, x: np.ndarray, apply_scaling: bool = True, track: bool = True) -> float:
        """System-level optimization objective function with best tracking."""
        x = self._preprocess(x)
        params = self._extract_parameters(x)
        result = self._run_system_simulation(params)
        
        # New: soft penalties with correct sign, then invert to a maximization score.
        def relu(x: float) -> float:
            return x if x > 0 else 0.0

        # Primary objective: minimize total power (or energy if you have it)
        primary_term = float(result.get("energy_J", result["total_power_W"]))

        # Targets / caps
        cap_power = float(self.config.total_power_budget_W)   # e.g., 2.0 W
        cap_temp  = 85.0                                      # °C limit
        min_tops  = 1.5  # Adjusted to realistic target
        min_yield = 0.5

        # Metrics
        total_power = float(result["total_power_W"])
        peak_temp   = float(result["peak_temp_C"])
        sustained_tops = float(result["sustained_tops"])
        yield_factor   = float(result["yield_factor"])

        # Correct penalty directions:
        #  - For ≤ constraints: relu(measured - target)
        #  - For ≥ constraints: relu(target   - measured)
        p_power = relu(total_power   - cap_power)  # ≤ constraint
        p_temp  = relu(peak_temp      - cap_temp)  # ≤ constraint
        p_tops  = relu(min_tops       - sustained_tops)  # ≥ constraint
        p_yield = relu(min_yield      - yield_factor)    # ≥ constraint

        # Weights — crank power/temp hard so violations dominate.
        W_POWER, W_TEMP, W_TOPS, W_YIELD = 1_000.0, 500.0, 200.0, 100.0

        total_penalty = (
            primary_term
            + W_POWER * p_power
            + W_TEMP  * p_temp
            + W_TOPS  * p_tops
            + W_YIELD * p_yield
        )

        # Turn "smaller is better" into a score to maximize.
        composite_score = 10_000.0 / (total_penalty + 1.0)
        
        # Track best state
        if composite_score < self.best_state.score:
            self.best_state.score = composite_score
            self.best_state.x = x.copy()
            self.best_state.power_W = total_power
            self.best_state.tops = sustained_tops
            
            # Print progress with power breakdown
            print(f"\n🎯 New best score: {composite_score:.2f}")
            print_architecture_totals(
                rows=35, cols=36, lanes=24,
                array_scope=self.config.array_scope,
                power_breakdown=result["power_breakdown"]
            )

        if track:
            self.tracker.track(composite_score, x)
            try:
                self.tracker.track_metadata({
                    "total_power_W": total_power,
                    "power_breakdown": result["power_breakdown"],
                    "peak_temp_C": peak_temp,
                    "sustained_tops": sustained_tops,
                    "yield_factor": yield_factor,
                    "primary_term": primary_term,
                    "p_power": p_power, "p_temp": p_temp, "p_tops": p_tops, "p_yield": p_yield,
                    "total_penalty": total_penalty
                })
            except AttributeError:
                pass

        return composite_score if not apply_scaling else self.scaled(composite_score)


def optimize_photonic_accelerator_fixed(
    iterations: int = 500,
    initial_samples: int = 100,
    samples_per_acquisition: int = 20,
    target_power_W: float = 2.0,
    target_performance_tops: float = 2.06,  # Realistic target
    output_dir: Optional[str] = None,
    run_id: Optional[str] = None,
    array_scope: str = "global",
    use_fallback: bool = False
) -> Dict[str, Any]:
    """
    Run Level 4 system optimization for the photonic AI accelerator (FIXED VERSION).
    
    Args:
        iterations: Number of optimization iterations
        initial_samples: Number of initial random samples
        samples_per_acquisition: Samples per iteration
        target_power_W: Target power budget (mobile constraint)
        target_performance_tops: Target sustained performance
        output_dir: Optional output directory for results
        run_id: Optional run ID for unique directory naming
        array_scope: "global" or "per_lane" for ring array calculation
        use_fallback: Force use of fallback optimizer instead of DANTE
        
    Returns:
        Optimization results with fab-ready accelerator configuration
    """
    # Create unique run directory
    if output_dir:
        output_dir = create_unique_run_dir(base_dir=output_dir, run_id=run_id)
        print(f"📁 Output directory: {output_dir}")
    
    # Create system-level objective function
    obj_function = PhotonicAcceleratorOptimizer()
    obj_function.config.total_power_budget_W = target_power_W
    obj_function.config.target_sustained_tops = target_performance_tops
    obj_function.config.array_scope = array_scope
    
    # Update performance model with array scope
    obj_function.performance.array_scope = array_scope
    
    print(f"🚀 Starting Level 4 Photonic AI Accelerator Optimization (FIXED)")
    print(f"Target: {target_performance_tops} TOPS at {target_power_W}W")
    print(f"Array scope: {array_scope}")
    print(f"Optimizing {obj_function.dims} system parameters...")
    
    # Print initial architecture totals
    print("\n📊 Architecture Configuration:")
    print_architecture_totals(
        rows=35, cols=36, lanes=24,
        array_scope=array_scope,
        power_breakdown=None
    )
    
    # Run optimization with fixes
    best_x, best_score, history = run_optimization_with_fixes(
        objective_func=obj_function,
        bounds=(obj_function.lb, obj_function.ub),
        n_iterations=iterations,
        initial_samples=initial_samples,
        use_fallback=use_fallback
    )
    
    # Extract best parameters and results
    best_params = obj_function._extract_parameters(best_x)
    best_result = obj_function._run_system_simulation(best_params)
    
    print(f"\n✅ Level 4 Optimization Complete!")
    print(f"Best Configuration:")
    print(f"  Score: {best_score:.2f}")
    print(f"  Power: {best_result['total_power_W']:.2f}W (target: {target_power_W}W)")
    print(f"  Performance: {best_result['sustained_tops']:.2f} TOPS (target: {target_performance_tops})")
    print(f"  Efficiency: {best_result['power_efficiency_tops_per_w']:.2f} TOPS/W")
    print(f"  Token Rate: {best_result['token_rate_per_s']:.1f} tok/s")
    print(f"  Unit Cost: ${best_result['unit_cost_USD']:.0f}")
    print(f"  Yield: {best_result['yield_factor']:.1%}")
    
    # Print final power breakdown
    print("\n📊 Final Power Breakdown:")
    print_architecture_totals(
        rows=35, cols=36, lanes=24,
        array_scope=array_scope,
        power_breakdown=best_result['power_breakdown']
    )
    
    # Save results
    results = {
        "best_score": best_score,
        "best_parameters": best_params,
        "best_metrics": best_result,
        "optimization_history": history,
        "total_evaluations": len(history),
        "target_specs": {
            "power_budget_W": target_power_W,
            "performance_target_tops": target_performance_tops,
            "array_scope": array_scope
        },
        "architecture": {
            "rows": 35,
            "cols": 36,
            "lanes": 24,
            "total_rings": 1260 if array_scope == "global" else 1260 * 24
        }
    }
    
    if output_dir:
        output_file = Path(output_dir) / "optimization_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n💾 Results saved to {output_file}")
    
    return results
