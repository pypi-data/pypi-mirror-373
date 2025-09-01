"""
Physics validation and metrics calculation for photonic accelerator.
Provides ground-truth calculations independent of optimization.
"""

import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PhysicsMetrics:
    """Container for validated physics metrics."""
    total_rings: int
    power_W: float
    tops: float
    tops_per_W: float
    token_rate: float
    power_breakdown: Dict[str, float]
    array_scope: str
    

def tops_from_spec(
    rows: int, 
    cols: int, 
    lanes: int, 
    macs_per_ring: int = 2,
    clock_ghz: float = 1.0, 
    utilization: float = 1.0,
    array_scope: str = "global"
) -> Tuple[float, int]:
    """
    Calculate TOPS from ring array specification.
    
    Args:
        rows: Number of rows in ring array
        cols: Number of columns in ring array
        lanes: Number of computational lanes
        macs_per_ring: MAC operations per ring (typically 2)
        clock_ghz: Clock frequency in GHz
        utilization: Utilization factor (0-1)
        array_scope: "global" (rows×cols total) or "per_lane" (rows×cols per lane)
    
    Returns:
        Tuple of (TOPS, total_rings)
    """
    base_rings = rows * cols
    
    if array_scope == "per_lane":
        total_rings = base_rings * lanes
    else:
        total_rings = base_rings
    
    # ops/sec = total_rings * macs_per_ring * clock_ghz * 1e9
    # TOPS = ops/sec / 1e12 = total_rings * macs_per_ring * clock_ghz / 1e3
    tops = (total_rings * macs_per_ring * clock_ghz / 1e3) * utilization
    
    return tops, total_rings


def power_breakdown(
    heater_uW_per_ring: float,
    active_fraction: float,
    total_rings: int,
    laser_W: float,
    dsp_sram_W: float,
    misc_W: float = 0.0
) -> Dict[str, float]:
    """
    Calculate detailed power breakdown.
    
    Args:
        heater_uW_per_ring: Heater power per ring in microWatts
        active_fraction: Fraction of rings that are active (0-1)
        total_rings: Total number of rings
        laser_W: Laser power in Watts
        dsp_sram_W: DSP and SRAM power in Watts
        misc_W: Miscellaneous power (3R, control, etc.) in Watts
    
    Returns:
        Dictionary with power breakdown
    """
    active_rings = int(total_rings * active_fraction)
    heaters_W = heater_uW_per_ring * active_rings / 1e6
    total_W = heaters_W + laser_W + dsp_sram_W + misc_W
    
    return {
        "heaters_W": float(heaters_W),
        "active_rings": active_rings,
        "laser_W": float(laser_W),
        "dsp_sram_W": float(dsp_sram_W),
        "misc_W": float(misc_W),
        "total_W": float(total_W)
    }


def power_from_spec(
    heater_power_W: float,
    laser_power_W: float,
    dsp_sram_power_W: float,
    misc_power_W: float = 0.0
) -> Dict[str, float]:
    """
    Calculate power breakdown from direct power specifications.
    
    Args:
        heater_power_W: Total heater power in Watts
        laser_power_W: Total laser power in Watts
        dsp_sram_power_W: DSP and SRAM power in Watts
        misc_power_W: Miscellaneous power (3R, control, etc.) in Watts
    
    Returns:
        Dictionary with power breakdown
    """
    total_W = heater_power_W + laser_power_W + dsp_sram_power_W + misc_power_W
    
    return {
        "heaters_W": float(heater_power_W),
        "lasers_W": float(laser_power_W),
        "dsp_sram_W": float(dsp_sram_power_W),
        "misc_W": float(misc_power_W),
        "total_W": float(total_W)
    }


def tokens_per_second(
    tops: float,
    ops_per_token: float,
    utilization: float = 1.0
) -> float:
    """
    Calculate token generation rate from TOPS.
    
    Args:
        tops: Performance in TOPS
        ops_per_token: Operations per token (model-dependent)
        utilization: Decode utilization factor
    
    Returns:
        Tokens per second
    """
    # tokens/s = (TOPS * 1e12 * utilization) / ops_per_token
    return (tops * 1e12 * utilization) / float(ops_per_token)


def validate_configuration(
    rows: int,
    cols: int,
    lanes: int,
    clock_ghz: float,
    heater_uW: float,
    laser_W: float,
    dsp_W: float,
    array_scope: str = "global",
    active_fraction: float = 0.8,
    utilization: float = 0.7,
    ops_per_token_7B: float = 1.4e11,  # 140B ops/token for 7B model
    verbose: bool = True
) -> PhysicsMetrics:
    """
    Validate a complete accelerator configuration.
    
    Args:
        rows: Ring array rows
        cols: Ring array columns
        lanes: Number of computational lanes
        clock_ghz: Clock frequency in GHz
        heater_uW: Heater power per ring in microWatts
        laser_W: Total laser power in Watts
        dsp_W: DSP/SRAM power in Watts
        array_scope: "global" or "per_lane"
        active_fraction: Fraction of active rings
        utilization: System utilization
        ops_per_token_7B: Operations per token for 7B model
        verbose: Print detailed breakdown
    
    Returns:
        PhysicsMetrics with validated results
    """
    # Calculate TOPS
    tops, total_rings = tops_from_spec(
        rows=rows,
        cols=cols,
        lanes=lanes,
        macs_per_ring=2,
        clock_ghz=clock_ghz,
        utilization=utilization,
        array_scope=array_scope
    )
    
    # Calculate power
    pb = power_breakdown(
        heater_uW_per_ring=heater_uW,
        active_fraction=active_fraction,
        total_rings=total_rings,
        laser_W=laser_W,
        dsp_sram_W=dsp_W,
        misc_W=0.1  # Control overhead
    )
    
    # Calculate token rate
    tok_rate = tokens_per_second(
        tops=tops,
        ops_per_token=ops_per_token_7B,
        utilization=utilization
    )
    
    # Calculate efficiency
    tops_per_W = tops / pb["total_W"] if pb["total_W"] > 0 else 0
    
    if verbose:
        print("\n" + "="*60)
        print("PHYSICS VALIDATION - Ground Truth Calculation")
        print("="*60)
        print(f"\n📐 Architecture Configuration:")
        print(f"  Array: {rows}×{cols} = {rows*cols} rings")
        print(f"  Scope: {array_scope}")
        print(f"  Lanes: {lanes}")
        print(f"  Total rings: {total_rings:,}")
        print(f"  Active rings: {pb['active_rings']:,} ({active_fraction:.0%})")
        print(f"  Clock: {clock_ghz} GHz")
        print(f"  Utilization: {utilization:.0%}")
        
        print(f"\n⚡ Power Breakdown:")
        print(f"  Heaters:  {pb['heaters_W']:.3f} W ({pb['active_rings']:,} × {heater_uW:.1f} µW)")
        print(f"  Lasers:   {pb['laser_W']:.3f} W")
        print(f"  DSP/SRAM: {pb['dsp_sram_W']:.3f} W")
        print(f"  Misc:     {pb['misc_W']:.3f} W")
        print(f"  ─────────────────────")
        print(f"  TOTAL:    {pb['total_W']:.3f} W")
        
        print(f"\n🚀 Performance Metrics:")
        print(f"  TOPS: {tops:.2f}")
        print(f"  TOPS/W: {tops_per_W:.2f}")
        print(f"  Token rate: {tok_rate:.1f} tok/s (7B model)")
        
        print(f"\n📊 Calculation Details:")
        print(f"  ops/sec = {total_rings} rings × 2 MAC × {clock_ghz} GHz × 1e9")
        print(f"  ops/sec = {total_rings * 2 * clock_ghz * 1e9:.2e}")
        print(f"  TOPS = {total_rings * 2 * clock_ghz * 1e9:.2e} / 1e12 × {utilization:.2f}")
        print(f"  TOPS = {tops:.2f}")
        print("="*60 + "\n")
    
    return PhysicsMetrics(
        total_rings=total_rings,
        power_W=pb["total_W"],
        tops=tops,
        tops_per_W=tops_per_W,
        token_rate=tok_rate,
        power_breakdown=pb,
        array_scope=array_scope
    )


def cross_check_optimization_result(
    optimization_params: Dict,
    verbose: bool = True
) -> Dict[str, any]:
    """
    Cross-check optimization results with physics calculations.
    
    Args:
        optimization_params: Parameters from optimization
        verbose: Print comparison
    
    Returns:
        Dictionary with comparison results
    """
    # Extract parameters
    rows = optimization_params.get("array_rows", 35)
    cols = optimization_params.get("array_cols", 36)
    lanes = optimization_params.get("num_lanes", 24)
    clock_ghz = optimization_params.get("clock_freq_GHz", 1.17)
    heater_uW = optimization_params.get("heater_power_uW", 60.4)
    laser_W = optimization_params.get("laser_power_W", 0.5)
    dsp_W = optimization_params.get("sram_power_W", 0.3)
    
    # Try both array scopes to see which matches
    results = {}
    
    for scope in ["global", "per_lane"]:
        metrics = validate_configuration(
            rows=rows,
            cols=cols,
            lanes=lanes,
            clock_ghz=clock_ghz,
            heater_uW=heater_uW,
            laser_W=laser_W,
            dsp_W=dsp_W,
            array_scope=scope,
            verbose=False
        )
        results[scope] = metrics
    
    if verbose:
        print("\n🔍 Cross-Check Results:")
        print(f"Optimization claimed: 7.48 TOPS at 1.68W")
        print(f"\nPhysics validation:")
        for scope, metrics in results.items():
            print(f"  {scope:10s}: {metrics.tops:.2f} TOPS at {metrics.power_W:.2f}W")
        
        # Find which is closer
        target_tops = 7.48
        global_diff = abs(results["global"].tops - target_tops)
        per_lane_diff = abs(results["per_lane"].tops - target_tops)
        
        if global_diff < per_lane_diff:
            print(f"\n✓ Likely using array_scope='global' (error: {global_diff:.2f} TOPS)")
        else:
            print(f"\n✓ Likely using array_scope='per_lane' (error: {per_lane_diff:.2f} TOPS)")
    
    return results


# Quick test function
if __name__ == "__main__":
    print("Testing physics validation...")
    
    # Test with values from the optimization run
    test_params = {
        "array_rows": 35,
        "array_cols": 36,
        "num_lanes": 24,
        "clock_freq_GHz": 1.17,
        "heater_power_uW": 60.4,
        "laser_power_W": 0.5,
        "sram_power_W": 0.3
    }
    
    results = cross_check_optimization_result(test_params)
