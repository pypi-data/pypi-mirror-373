"""
Console encoding utilities for Windows compatibility.
Provides UTF-8 enforcement and ASCII-safe character mapping.
"""

import os
import sys


def force_utf8():
    """Force UTF-8 encoding for console output on Windows."""
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    os.environ.setdefault("PYTHONUTF8", "1")
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            try:
                s.reconfigure(encoding="utf-8")
            except Exception:
                pass


# ASCII-safe character mapping for Windows console compatibility
ASCII_SAFE_MAP = {
    "×": "x",      # multiplication sign
    "µ": "u",      # micro sign
    "μ": "u",      # Greek mu
    "—": "-",      # em dash
    "–": "-",      # en dash
    " ": " ",      # non-breaking space -> regular space
    "°": "deg",    # degree symbol
    "±": "+/-",    # plus-minus
    "≈": "~",      # approximately equal
    "≤": "<=",     # less than or equal
    "≥": ">=",     # greater than or equal
}


def ascii_safe(s: str) -> str:
    """
    Convert Unicode characters to ASCII-safe equivalents.
    
    Args:
        s: Input string that may contain Unicode characters
        
    Returns:
        String with Unicode characters replaced by ASCII equivalents
    """
    for unicode_char, ascii_char in ASCII_SAFE_MAP.items():
        s = s.replace(unicode_char, ascii_char)
    return s


def safe_print(text: str, **kwargs):
    """
    Print text with ASCII-safe character conversion.
    
    Args:
        text: Text to print
        **kwargs: Additional arguments passed to print()
    """
    print(ascii_safe(str(text)), **kwargs)


def format_dimensions(rows: int, cols: int) -> str:
    """Format array dimensions in ASCII-safe way."""
    return f"{rows}x{cols}"


def format_power_unit(value_or_unit, unit: str = "uW") -> str:
    """Format power values with ASCII-safe units."""
    # Handle case where only unit is passed (backward compatibility)
    if isinstance(value_or_unit, str):
        return value_or_unit  # Just return the unit string
    
    # Normal case with value and unit
    value = float(value_or_unit)
    return f"{value:.1f} {unit}"


def format_length_unit(value_or_unit, unit: str = "um") -> str:
    """Format length values with ASCII-safe units."""
    # Handle case where only unit is passed (backward compatibility)
    if isinstance(value_or_unit, str):
        return value_or_unit  # Just return the unit string
    
    # Normal case with value and unit
    value = float(value_or_unit)
    return f"{value:.1f} {unit}"
