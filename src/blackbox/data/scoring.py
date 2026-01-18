"""Scoring calculations for economic events.

This module provides functions for calculating various scores
related to economic events, such as the surprise score.
"""


def calculate_surprise(
    actual: float | None,
    forecast: float | None,
    direction: int,
) -> float | None:
    """Calculate the normalized surprise score.

    The surprise score measures how much the actual result deviated
    from market expectations (forecast), normalized by the forecast value.

    Formula: direction * (actual - forecast) / |forecast|

    Args:
        actual: The actual reported value (None if not yet released).
        forecast: The forecasted value (None if no forecast available).
        direction: Impact direction (+1 = higher is bullish, -1 = higher is bearish).

    Returns:
        Normalized surprise score, or None if:
        - actual is None
        - forecast is None
        - forecast is 0 (division impossible)

    Examples:
        >>> calculate_surprise(300000, 200000, +1)
        0.5
        >>> calculate_surprise(0.04, 0.035, -1)
        -0.14285714285714285
        >>> calculate_surprise(0.002, 0.003, +1)
        -0.3333333333333333
        >>> calculate_surprise(None, 0.003, +1)
        None
        >>> calculate_surprise(0.002, None, +1)
        None
        >>> calculate_surprise(0.002, 0, +1)
        None
    """
    if actual is None or forecast is None:
        return None

    if forecast == 0:
        return None

    return direction * (actual - forecast) / abs(forecast)
