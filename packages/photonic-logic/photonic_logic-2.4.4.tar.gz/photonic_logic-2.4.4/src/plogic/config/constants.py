"""
Single source of truth for all physics constants and device parameters.
All commands and modules should import from here to ensure consistency.
"""

from dataclasses import dataclass, asdict
import os
import math
from typing import Optional


def _env_float(name: str, default: float) -> float:
    """Get float value from environment variable with fallback to default."""
    try:
        return float(os.getenv(name, default))
    except Exception:
        return default


@dataclass(frozen=True)
class DeviceConst:
    """Unified device constants used across all commands."""
    
    # Optical/device parameters
    wavelength_nm: float = _env_float("PLOGIC_WAVELENGTH_NM", 1550.0)
    Q_factor: float = _env_float("PLOGIC_Q_FACTOR", 5e5)
    kappa_Hz: float = _env_float("PLOGIC_KAPPA_HZ", 3.9e8)
    g_xpm_Hz_per_W: float = _env_float("PLOGIC_GXPM_HZ_PER_W", 2.5e12)
    
    # System/power parameters
    heater_uW_per_ring: float = _env_float("PLOGIC_HEATER_UW_PER_RING", 218.0)  # aligns with ~0.22 W @ 80% of 1260
    active_fraction: float = _env_float("PLOGIC_ACTIVE_FRACTION", 0.80)
    laser_W: float = _env_float("PLOGIC_LASER_W", 0.53)
    dsp_sram_W: float = _env_float("PLOGIC_DSP_SRAM_W", 0.35)
    misc_W: float = _env_float("PLOGIC_MISC_W", 0.80)
    
    # Logic pulse defaults
    P_high_mW: float = _env_float("PLOGIC_P_HIGH_MW", 1.0)
    pulse_ns: float = _env_float("PLOGIC_PULSE_NS", 1.0)
    split_loss_db: float = _env_float("PLOGIC_SPLIT_LOSS_DB", 0.5)
    fanout: int = int(_env_float("PLOGIC_FANOUT", 1))
    
    # Compute defaults
    macs_per_ring: float = _env_float("PLOGIC_MACS_PER_RING", 2.0)
    decode_util: float = _env_float("PLOGIC_DECODE_UTIL", 0.55)
    duty_cycle: float = _env_float("PLOGIC_DECODE_DUTY", 0.80)
    guard_efficiency: float = _env_float("PLOGIC_GUARD_EFF", 0.86)
    
    # Array configuration defaults
    array_scope: str = os.getenv("PLOGIC_ARRAY_SCOPE", "global")  # "global" or "per_lane"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


def pulse_energy_fJ(P_high_mW: float, pulse_ns: float, extra_loss_db: float = 0.0) -> float:
    """
    Calculate pulse energy in femtojoules.
    
    E_fJ = P[mW] * t[ns] * 1e3 * 10^(loss_dB/10)
    
    Args:
        P_high_mW: High control power in milliwatts
        pulse_ns: Pulse duration in nanoseconds
        extra_loss_db: Additional loss in dB (e.g., from splitting)
    
    Returns:
        Energy in femtojoules
    """
    return float(P_high_mW * pulse_ns * 1e3 * (10.0 ** (extra_loss_db / 10.0)))


def contrast_db(T_on: float, T_off: float, eps: float = 1e-9) -> float:
    """
    Calculate contrast in dB between on and off transmissions.
    
    Args:
        T_on: Transmission in ON state
        T_off: Transmission in OFF state
        eps: Small epsilon to avoid log(0) and improve numerical stability
    
    Returns:
        Contrast in dB (raw calculation, may be negative)
    """
    T_on_safe = max(T_on, eps)
    T_off_safe = max(T_off, eps)
    contrast_raw = 10.0 * math.log10(T_on_safe / T_off_safe)
    
    # Return raw contrast (can be negative if T_off > T_on)
    # This preserves the physical meaning of the measurement
    return float(contrast_raw)


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
