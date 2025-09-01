"""
ASCII-safe formatting utilities for cross-platform compatibility.

This module provides functions to format physical units and symbols using only
ASCII characters, ensuring compatibility with all console encodings including
Windows cp1252.
"""

import os
from typing import Optional, Union


def is_utf8_capable() -> bool:
    """
    Check if the current environment supports UTF-8 encoding.
    
    Returns:
        bool: True if UTF-8 is supported, False otherwise.
    """
    # Check environment variables
    if os.environ.get('PYTHONUTF8') == '1':
        return True
    
    # Check Python IO encoding
    io_encoding = os.environ.get('PYTHONIOENCODING', '').lower()
    if 'utf-8' in io_encoding or 'utf8' in io_encoding:
        return True
    
    # Default to ASCII-safe
    return False


def format_micro(value: Union[int, float], unit: str = "W", use_unicode: Optional[bool] = None) -> str:
    """
    Format a value with micro prefix.
    
    Args:
        value: The numeric value
        unit: The unit (e.g., "W", "m", "s")
        use_unicode: Force Unicode (True) or ASCII (False). If None, auto-detect.
    
    Returns:
        str: Formatted string with micro prefix (µ or u)
    
    Examples:
        >>> format_micro(100, "W")
        '100 uW'
        >>> format_micro(50.5, "m")
        '50.5 um'
    """
    if use_unicode is None:
        use_unicode = is_utf8_capable()
    
    prefix = 'µ' if use_unicode else 'u'
    return f"{value} {prefix}{unit}"


def format_squared(value: Union[int, float], unit: str = "m") -> str:
    """
    Format a value with squared unit.
    
    Args:
        value: The numeric value
        unit: The base unit
    
    Returns:
        str: Formatted string with squared unit
    
    Examples:
        >>> format_squared(10, "m")
        '10 m^2'
    """
    return f"{value} {unit}^2"


def format_cubed(value: Union[int, float], unit: str = "m") -> str:
    """
    Format a value with cubed unit.
    
    Args:
        value: The numeric value
        unit: The base unit
    
    Returns:
        str: Formatted string with cubed unit
    """
    return f"{value} {unit}^3"


def format_greek(letter: str, use_unicode: Optional[bool] = None) -> str:
    """
    Format a Greek letter.
    
    Args:
        letter: The Greek letter name (e.g., "eta", "lambda", "tau")
        use_unicode: Force Unicode (True) or ASCII (False). If None, auto-detect.
    
    Returns:
        str: The Greek letter or its ASCII name
    """
    if use_unicode is None:
        use_unicode = is_utf8_capable()
    
    if not use_unicode:
        return letter
    
    greek_map = {
        'alpha': 'α',
        'beta': 'β',
        'gamma': 'γ',
        'delta': 'δ',
        'epsilon': 'ε',
        'zeta': 'ζ',
        'eta': 'η',
        'theta': 'θ',
        'iota': 'ι',
        'kappa': 'κ',
        'lambda': 'λ',
        'mu': 'μ',
        'nu': 'ν',
        'xi': 'ξ',
        'omicron': 'ο',
        'pi': 'π',
        'rho': 'ρ',
        'sigma': 'σ',
        'tau': 'τ',
        'upsilon': 'υ',
        'phi': 'φ',
        'chi': 'χ',
        'psi': 'ψ',
        'omega': 'ω',
        'Delta': 'Δ',
        'Sigma': 'Σ',
        'Omega': 'Ω',
    }
    
    return greek_map.get(letter, letter)


def format_comparison(operator: str) -> str:
    """
    Format comparison operators in ASCII.
    
    Args:
        operator: The operator type ("gte", "lte", "approx", etc.)
    
    Returns:
        str: ASCII representation of the operator
    """
    operators = {
        'gte': '>=',
        'lte': '<=',
        'approx': '~',
        'neq': '!=',
        'plusminus': '+/-',
        'times': 'x',
        'divide': '/',
        'infinity': 'inf',
    }
    
    return operators.get(operator, operator)


def format_degree(value: Union[int, float], use_unicode: Optional[bool] = None) -> str:
    """
    Format a value in degrees.
    
    Args:
        value: The numeric value
        use_unicode: Force Unicode (True) or ASCII (False). If None, auto-detect.
    
    Returns:
        str: Formatted string with degree symbol
    """
    if use_unicode is None:
        use_unicode = is_utf8_capable()
    
    symbol = '°' if use_unicode else ' deg'
    return f"{value}{symbol}"


def format_ohm(value: Union[int, float], use_unicode: Optional[bool] = None) -> str:
    """
    Format a resistance value in ohms.
    
    Args:
        value: The numeric value
        use_unicode: Force Unicode (True) or ASCII (False). If None, auto-detect.
    
    Returns:
        str: Formatted string with ohm symbol
    """
    if use_unicode is None:
        use_unicode = is_utf8_capable()
    
    symbol = 'Ω' if use_unicode else 'Ohm'
    return f"{value} {symbol}"


def sanitize_for_ascii(text: str) -> str:
    """
    Replace all non-ASCII characters with ASCII equivalents.
    
    Args:
        text: Input text that may contain Unicode
    
    Returns:
        str: ASCII-safe version of the text
    """
    replacements = {
        # Greek letters
        'α': 'alpha', 'β': 'beta', 'γ': 'gamma', 'δ': 'delta',
        'ε': 'epsilon', 'ζ': 'zeta', 'η': 'eta', 'θ': 'theta',
        'ι': 'iota', 'κ': 'kappa', 'λ': 'lambda', 'μ': 'mu',
        'ν': 'nu', 'ξ': 'xi', 'ο': 'omicron', 'π': 'pi',
        'ρ': 'rho', 'σ': 'sigma', 'τ': 'tau', 'υ': 'upsilon',
        'φ': 'phi', 'χ': 'chi', 'ψ': 'psi', 'ω': 'omega',
        'Δ': 'Delta', 'Σ': 'Sigma', 'Ω': 'Omega',
        
        # Units and symbols
        'µ': 'u',  # micro
        '°': 'deg',  # degree
        '²': '^2',  # squared
        '³': '^3',  # cubed
        '×': 'x',  # multiplication
        '÷': '/',  # division
        '±': '+/-',  # plus-minus
        '≈': '~',  # approximately
        '≤': '<=',  # less than or equal
        '≥': '>=',  # greater than or equal
        '≠': '!=',  # not equal
        '∞': 'inf',  # infinity
        
        # Arrows
        '→': '->',  # right arrow
        '←': '<-',  # left arrow
        '↑': '^',  # up arrow
        '↓': 'v',  # down arrow
        '↔': '<->',  # bidirectional arrow
        
        # Quotes and dashes
        ''': "'",  # left single quote
        ''': "'",  # right single quote
        '"': '"',  # left double quote
        '"': '"',  # right double quote
        '–': '-',  # en dash
        '—': '--',  # em dash
        '…': '...',  # ellipsis
        
        # Checkmarks and symbols
        '✓': '[OK]',
        '✗': '[X]',
        '✅': '[PASS]',
        '❌': '[FAIL]',
        '⚠': '[WARNING]',
        '⚡': '[!]',
        '🎉': '[SUCCESS]',
        '🚀': '[LAUNCH]',
        '💡': '[IDEA]',
        '🔧': '[FIX]',
        '📝': '[NOTE]',
        '📊': '[CHART]',
        '🎯': '[TARGET]',
    }
    
    result = text
    for unicode_char, ascii_replacement in replacements.items():
        result = result.replace(unicode_char, ascii_replacement)
    
    # Final check: replace any remaining non-ASCII with '?'
    try:
        result.encode('ascii')
    except UnicodeEncodeError:
        # If there are still non-ASCII characters, replace them
        result = ''.join(char if ord(char) < 128 else '?' for char in result)
    
    return result


# Standard unit abbreviations (always ASCII)
UNITS = {
    'wavelength': 'nm',
    'power': 'mW',
    'energy': 'fJ',
    'time': 'ns',
    'frequency': 'GHz',
    'length': 'um',
    'area': 'um^2',
    'loss': 'dB/cm',
    'temperature': 'K',
    'thermal_conductivity': 'W/(m*K)',
    'nonlinearity': 'm^2/W',
    'absorption': 'cm^-1',
    'efficiency': '%',
    'voltage': 'V',
    'current': 'mA',
    'resistance': 'Ohm',
    'capacitance': 'fF',
    'inductance': 'nH',
}


def format_value_with_unit(value: Union[int, float], unit_type: str, precision: int = 2) -> str:
    """
    Format a value with its appropriate unit.
    
    Args:
        value: The numeric value
        unit_type: The type of unit from UNITS dict
        precision: Number of decimal places
    
    Returns:
        str: Formatted string with value and unit
    
    Examples:
        >>> format_value_with_unit(1550, 'wavelength')
        '1550 nm'
        >>> format_value_with_unit(0.06, 'power', precision=3)
        '0.060 mW'
    """
    unit = UNITS.get(unit_type, '')
    if unit:
        return f"{value:.{precision}f} {unit}"
    return f"{value:.{precision}f}"


if __name__ == "__main__":
    # Test the formatting functions
    print("ASCII-safe formatting examples:")
    print(f"Micro: {format_micro(100, 'W')}")
    print(f"Squared: {format_squared(10, 'm')}")
    print(f"Greek eta: {format_greek('eta')}")
    print(f"Comparison: {format_comparison('gte')}")
    print(f"Degree: {format_degree(25)}")
    
    # Test sanitization
    test_text = "η = 0.98, P = 100 µW, T = 25°C, λ = 1550 nm, ≥ 30 stages ✅"
    print(f"\nOriginal: {test_text}")
    print(f"ASCII-safe: {sanitize_for_ascii(test_text)}")
