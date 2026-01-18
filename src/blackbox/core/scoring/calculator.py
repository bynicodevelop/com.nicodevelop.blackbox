"""Pure calculation functions for fundamental scoring.

This module contains stateless functions for calculating scores,
decay factors, and directional biases based on economic events.
"""

from datetime import datetime
from datetime import time as dt_time

from blackbox.core.scoring.config import ScoringConfig
from blackbox.data.models import EconomicEvent


def calculate_decay(
    event_time: datetime,
    reference_time: datetime,
    half_life_hours: float,
) -> float:
    """Calculate temporal decay factor for an event.

    Uses exponential decay formula: 0.5^(hours_elapsed / half_life).
    Future events (negative elapsed time) return decay of 1.0.

    Args:
        event_time: When the event occurred (timezone-aware or naive).
        reference_time: Reference point for decay calculation.
        half_life_hours: Number of hours for decay to reach 50%.

    Returns:
        Decay factor between 0 and 1. Returns 1.0 for future events.

    Raises:
        ValueError: If half_life_hours is not positive.
    """
    if half_life_hours <= 0:
        raise ValueError("half_life_hours must be positive")

    # Calculate hours elapsed
    elapsed = reference_time - event_time
    hours_elapsed = elapsed.total_seconds() / 3600

    # Future events have no decay
    if hours_elapsed < 0:
        return 1.0

    # Exponential decay: 0.5^(hours/half_life)
    return 0.5 ** (hours_elapsed / half_life_hours)


def calculate_event_force(
    surprise: float,
    weight: int,
    decay: float,
) -> float:
    """Calculate the force contribution of a single event.

    Force = surprise × weight × decay

    Args:
        surprise: Surprise score of the event (can be positive or negative).
        weight: Importance weight of the event (1-10).
        decay: Temporal decay factor (0-1).

    Returns:
        Force contribution of the event.
    """
    return surprise * weight * decay


def event_to_datetime(
    event: EconomicEvent,
    reference: datetime,
) -> datetime:
    """Convert an event's date and time to a datetime object.

    If the event has no time, uses 00:00:00 (start of day).
    The resulting datetime uses the same timezone as the reference.

    Args:
        event: Economic event with date and optional time.
        reference: Reference datetime for timezone info.

    Returns:
        Datetime representing when the event occurred.
    """
    event_time = event.time if event.time is not None else dt_time(0, 0, 0)

    # Combine date and time
    event_dt = datetime.combine(event.date, event_time)

    # Apply timezone if reference has one
    if reference.tzinfo is not None:
        event_dt = event_dt.replace(tzinfo=reference.tzinfo)

    return event_dt


def calculate_currency_score(
    events: list[EconomicEvent],
    currency: str,
    reference_time: datetime,
    config: ScoringConfig,
) -> float:
    """Calculate aggregate score for a currency from its events.

    Filters events by currency, calculates force for each valid event
    (with non-None surprise), and sums them with temporal decay.

    Args:
        events: List of economic events to process.
        currency: Currency code to filter by (e.g., "USD", "EUR").
        reference_time: Reference point for decay calculation.
        config: Scoring configuration with decay parameters.

    Returns:
        Aggregate score for the currency. Returns 0.0 if no valid events.
    """
    currency_upper = currency.upper()
    total_score = 0.0

    for event in events:
        # Filter by currency
        if event.currency.upper() != currency_upper:
            continue

        # Skip events without surprise score
        if event.surprise is None:
            continue

        # Calculate decay based on event time
        event_dt = event_to_datetime(event, reference_time)
        decay = calculate_decay(event_dt, reference_time, config.half_life_hours)

        # Calculate and accumulate force
        force = calculate_event_force(event.surprise, event.weight, decay)
        total_score += force

    return total_score


def calculate_pair_bias(base_score: float, quote_score: float) -> float:
    """Calculate directional bias for a currency pair.

    Bias = base_currency_score - quote_currency_score

    A positive bias indicates bullish sentiment for the pair (base > quote).
    A negative bias indicates bearish sentiment for the pair (base < quote).

    Args:
        base_score: Aggregate score for the base currency.
        quote_score: Aggregate score for the quote currency.

    Returns:
        Bias value (positive = bullish, negative = bearish).
    """
    return base_score - quote_score


def get_bias_signal(bias: float, threshold: float) -> str:
    """Convert a bias value to a directional signal.

    Args:
        bias: Pair bias value.
        threshold: Minimum absolute bias for directional signal.

    Returns:
        "BULLISH" if bias > threshold,
        "BEARISH" if bias < -threshold,
        "NEUTRAL" otherwise.
    """
    if bias > threshold:
        return "BULLISH"
    elif bias < -threshold:
        return "BEARISH"
    else:
        return "NEUTRAL"
