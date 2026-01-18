"""Core module for trading logic.

This module contains the business logic for the trading robot,
including strategies, signals, and portfolio management.
"""

from blackbox.core.logging import get_logger, setup_logging
from blackbox.core.scoring import (
    ScoringConfig,
    ScoringService,
    calculate_currency_score,
    calculate_decay,
    calculate_event_force,
    calculate_pair_bias,
    event_to_datetime,
    get_bias_signal,
)

__all__ = [
    # Logging
    "get_logger",
    "setup_logging",
    # Scoring
    "ScoringConfig",
    "ScoringService",
    "calculate_decay",
    "calculate_event_force",
    "calculate_currency_score",
    "calculate_pair_bias",
    "event_to_datetime",
    "get_bias_signal",
]
