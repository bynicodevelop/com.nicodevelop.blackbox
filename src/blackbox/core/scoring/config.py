"""Configuration for the scoring module.

This module defines configuration dataclasses for the scoring system.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoringConfig:
    """Configuration for fundamental scoring calculations.

    Attributes:
        half_life_hours: Half-life for decay calculation in hours.
            Events decay to 50% weight after this many hours.
        lookback_days: Number of days to look back for events.
        min_bias_threshold: Minimum absolute bias value to generate
            a directional signal (BULLISH/BEARISH). Below this threshold,
            the signal is NEUTRAL.
    """

    half_life_hours: float = 48.0
    lookback_days: int = 7
    min_bias_threshold: float = 1.0

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.half_life_hours <= 0:
            raise ValueError("half_life_hours must be positive")
        if self.lookback_days <= 0:
            raise ValueError("lookback_days must be positive")
        if self.min_bias_threshold < 0:
            raise ValueError("min_bias_threshold must be non-negative")
