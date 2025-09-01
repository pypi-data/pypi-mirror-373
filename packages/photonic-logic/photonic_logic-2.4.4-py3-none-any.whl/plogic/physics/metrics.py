"""
Shared physics metrics calculations used across all commands.
This ensures consistent TOPS, power, and energy calculations everywhere.
"""

from typing import Dict, Tuple
from ..config.constants import DeviceConst


def tops_from_spec(
    rows: int,
    cols: int,
    lanes: int,
    macs_per_ring: float,
    clock_ghz: float,
    utilization: float,
    array_scope: str
) -> Tuple[float, float, int]:
    """
    Calculate TOPS from ring array specification.
    
    Args:
        rows: Number of rows in ring array
        cols: Number of columns in ring array
        lanes: Number of computational lanes
        macs_per_ring: MAC operations per ring
        clock_ghz: Clock frequency in GHz
        utilization: Total utilization factor (0-1)
        array_scope: "global" (rows×cols total) or "per_lane" (rows×cols per lane)
    
    Returns:
        Tuple of (peak_tops, effective_tops, total_rings)
    """
    base = rows * cols
    total_rings = base * (lanes if array_scope == "per_lane" else 1)
    peak_tops = (total_rings * macs_per_ring * clock_ghz) / 1e3
    eff_tops = peak_tops * utilization
    return float(peak_tops), float(eff_tops), int(total_rings)


def utilization_product(decode_util: float, duty: float, guard: float) -> float:
    """
    Calculate total utilization from individual factors.
    
    Args:
        decode_util: Decode utilization factor
        duty: Duty cycle factor
        guard: Guard efficiency factor
    
    Returns:
        Product of all utilization factors
    """
    return float(decode_util * duty * guard)


def power_breakdown(total_rings: int, C: DeviceConst) -> Dict[str, float]:
    """
    Calculate detailed power breakdown using unified constants.
    
    Args:
        total_rings: Total number of rings in the system
        C: DeviceConst instance with system parameters
    
    Returns:
        Dictionary with power breakdown in Watts
    """
    heaters_W = C.heater_uW_per_ring * total_rings * C.active_fraction / 1e6
    total_W = heaters_W + C.laser_W + C.dsp_sram_W + C.misc_W
    
    return {
        "heaters_W": float(heaters_W),
        "laser_W": float(C.laser_W),
        "dsp_sram_W": float(C.dsp_sram_W),
        "misc_W": float(C.misc_W),
        "total_W": float(total_W),
        "active_rings": int(total_rings * C.active_fraction),
        "total_rings": int(total_rings)
    }


def power_breakdown_explicit(
    heater_uW_per_ring: float,
    active_fraction: float,
    total_rings: int,
    laser_W: float,
    dsp_sram_W: float,
    misc_W: float = 0.0
) -> Dict[str, float]:
    """
    Calculate power breakdown with explicit parameters (for optimization).
    
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
        "total_W": float(total_W),
        "total_rings": int(total_rings)
    }


def format_throughput_summary(
    peak_tops: float,
    effective_tops: float,
    clock_ghz: float,
    decode_util: float,
    duty_cycle: float,
    guard_efficiency: float,
    array_scope: str,
    total_rings: int
) -> Dict:
    """
    Format throughput metrics for consistent output.
    
    Args:
        peak_tops: Peak TOPS performance
        effective_tops: Effective TOPS after utilization
        clock_ghz: Clock frequency in GHz
        decode_util: Decode utilization factor
        duty_cycle: Duty cycle factor
        guard_efficiency: Guard efficiency factor
        array_scope: Array scope ("global" or "per_lane")
        total_rings: Total number of rings
    
    Returns:
        Dictionary with formatted throughput summary
    """
    return {
        "array": {
            "scope": array_scope,
            "total_rings": total_rings
        },
        "throughput": {
            "peak_tops": round(peak_tops, 3),
            "effective_tops": round(effective_tops, 3),
            "clock_ghz": round(clock_ghz, 2),
            "factors": {
                "decode_util": round(decode_util, 3),
                "duty_cycle": round(duty_cycle, 3),
                "guard_efficiency": round(guard_efficiency, 3),
                "total_utilization": round(decode_util * duty_cycle * guard_efficiency, 3)
            }
        }
    }


def print_throughput_summary(
    peak_tops: float,
    effective_tops: float,
    clock_ghz: float,
    decode_util: float,
    duty_cycle: float,
    guard_efficiency: float,
    verbose: bool = True
) -> None:
    """
    Print formatted throughput summary to console.
    
    Args:
        peak_tops: Peak TOPS performance
        effective_tops: Effective TOPS after utilization
        clock_ghz: Clock frequency in GHz
        decode_util: Decode utilization factor
        duty_cycle: Duty cycle factor
        guard_efficiency: Guard efficiency factor
        verbose: Whether to print detailed breakdown
    """
    if not verbose:
        return
    
    print(f"Throughput (peak):      {peak_tops:.2f} TOPS @ {clock_ghz:.2f} GHz")
    print(f"Throughput (effective): {effective_tops:.2f} TOPS "
          f"[decode={decode_util:.2f} × duty={duty_cycle:.2f} × guard={guard_efficiency:.2f}]")


def print_power_breakdown(power_dict: Dict[str, float], verbose: bool = True) -> None:
    """
    Print formatted power breakdown to console.
    
    Args:
        power_dict: Power breakdown dictionary from power_breakdown()
        verbose: Whether to print
    """
    if not verbose:
        return
    
    print("\nPower Breakdown:")
    print(f"  Heaters:   {power_dict['heaters_W']:.3f} W")
    print(f"  Lasers:    {power_dict['laser_W']:.3f} W")
    print(f"  DSP/SRAM:  {power_dict['dsp_sram_W']:.3f} W")
    print(f"  Misc:      {power_dict['misc_W']:.3f} W")
    print(f"  ────────────────")
    print(f"  Total:     {power_dict['total_W']:.3f} W")
    
    if 'active_rings' in power_dict:
        print(f"\n  Active rings: {power_dict['active_rings']:,} / {power_dict.get('total_rings', 0):,}")
