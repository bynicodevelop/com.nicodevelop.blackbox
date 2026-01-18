"""Normalizer for economic calendar values.

This module provides functions to parse and normalize economic values
such as "223K" → 223000, "2.5%" → 0.025, etc.
"""

import re

# Multipliers for unit suffixes (case-insensitive)
UNIT_MULTIPLIERS = {
    "k": 1_000,
    "m": 1_000_000,
    "b": 1_000_000_000,
    "t": 1_000_000_000_000,
}

# Regex pattern to parse economic values
# Matches: optional sign, number (with optional decimals), optional unit suffix or %
VALUE_PATTERN = re.compile(
    r"^\s*"  # Leading whitespace
    r"([<>≤≥]?)"  # Optional comparison operator
    r"([+-]?)"  # Optional sign
    r"([\d,]+\.?\d*)"  # Number with optional decimals and thousand separators
    r"\s*"  # Optional whitespace
    r"([kmbt%]?)"  # Optional unit suffix or percent
    r"\s*$",  # Trailing whitespace
    re.IGNORECASE,
)


def normalize_value(raw_value: str | None) -> float | None:
    """Normalize an economic value string to a float.

    Handles various formats commonly found in economic calendars:
    - Unit suffixes: "223K" → 223000, "1.5M" → 1500000, "2B" → 2000000000
    - Percentages: "2.5%" → 0.025
    - Negative values: "-50B" → -50000000000
    - Thousand separators: "1,234" → 1234
    - Comparison operators are stripped: "<0.1%" → 0.001

    Args:
        raw_value: The raw string value to normalize (e.g., "223K", "2.5%").

    Returns:
        The normalized float value, or None if the input is None, empty,
        or cannot be parsed.

    Examples:
        >>> normalize_value("223K")
        223000.0
        >>> normalize_value("2.5%")
        0.025
        >>> normalize_value("-1.5M")
        -1500000.0
        >>> normalize_value(None)
        None
    """
    if raw_value is None:
        return None

    # Strip and handle empty strings
    cleaned = raw_value.strip()
    if not cleaned:
        return None

    # Try to match the pattern
    match = VALUE_PATTERN.match(cleaned)
    if not match:
        return None

    _, sign, number_str, unit = match.groups()

    # Remove thousand separators
    number_str = number_str.replace(",", "")

    try:
        value = float(number_str)
    except ValueError:
        return None

    # Apply sign
    if sign == "-":
        value = -value

    # Apply unit multiplier or percentage conversion
    unit_lower = unit.lower()
    if unit_lower == "%":
        value = value / 100
    elif unit_lower in UNIT_MULTIPLIERS:
        value = value * UNIT_MULTIPLIERS[unit_lower]

    return value


def format_normalized_value(
    value: float | None, precision: int = 2, use_suffix: bool = True
) -> str:
    """Format a normalized value back to a human-readable string.

    Args:
        value: The normalized float value.
        precision: Number of decimal places for display.
        use_suffix: Whether to use K/M/B suffixes for large numbers.

    Returns:
        Formatted string representation of the value.

    Examples:
        >>> format_normalized_value(223000)
        "223K"
        >>> format_normalized_value(1500000)
        "1.5M"
        >>> format_normalized_value(0.025)
        "0.03"
    """
    if value is None:
        return ""

    if not use_suffix:
        return f"{value:.{precision}f}"

    abs_value = abs(value)
    sign = "-" if value < 0 else ""

    if abs_value >= 1_000_000_000_000:
        return f"{sign}{abs_value / 1_000_000_000_000:.{precision}f}T"
    elif abs_value >= 1_000_000_000:
        return f"{sign}{abs_value / 1_000_000_000:.{precision}f}B"
    elif abs_value >= 1_000_000:
        return f"{sign}{abs_value / 1_000_000:.{precision}f}M"
    elif abs_value >= 1_000:
        return f"{sign}{abs_value / 1_000:.{precision}f}K"
    else:
        return f"{sign}{abs_value:.{precision}f}"
