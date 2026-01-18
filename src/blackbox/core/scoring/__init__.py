"""Fundamental scoring module for currency analysis.

This module provides functionality for calculating fundamental scores
based on economic events, with temporal decay and directional biases.
"""

from blackbox.core.scoring.calculator import (
    calculate_currency_score,
    calculate_decay,
    calculate_event_force,
    calculate_pair_bias,
    event_to_datetime,
    get_bias_signal,
)
from blackbox.core.scoring.config import ScoringConfig
from blackbox.core.scoring.service import ScoringService

__all__ = [
    # Config
    "ScoringConfig",
    # Service
    "ScoringService",
    # Calculator functions
    "calculate_decay",
    "calculate_event_force",
    "calculate_currency_score",
    "calculate_pair_bias",
    "event_to_datetime",
    "get_bias_signal",
]
