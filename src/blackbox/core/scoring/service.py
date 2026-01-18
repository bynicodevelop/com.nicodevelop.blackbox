"""Service layer for fundamental scoring operations.

This module provides a high-level interface for calculating currency
scores and pair biases, integrating with the event repository.
"""

from datetime import datetime, timedelta

from blackbox.core.scoring.calculator import (
    calculate_currency_score,
    calculate_pair_bias,
    get_bias_signal,
)
from blackbox.core.scoring.config import ScoringConfig
from blackbox.data.storage.repository import EventRepository


class ScoringService:
    """Service for calculating fundamental scores and biases.

    Integrates with EventRepository to fetch events and calculate
    scores with temporal decay.
    """

    def __init__(
        self,
        config: ScoringConfig,
        event_repository: EventRepository,
    ) -> None:
        """Initialize the scoring service.

        Args:
            config: Scoring configuration with decay and threshold parameters.
            event_repository: Repository for fetching economic events.
        """
        self.config = config
        self.repository = event_repository

    def get_currency_score(
        self,
        currency: str,
        at_time: datetime | None = None,
    ) -> float:
        """Calculate the aggregate score for a currency.

        Fetches events from the lookback window and calculates
        a weighted, decayed score based on surprises.

        Args:
            currency: Currency code (e.g., "USD", "EUR").
            at_time: Reference time for calculations. Defaults to now.

        Returns:
            Aggregate score for the currency.
        """
        reference_time = at_time if at_time is not None else datetime.now()

        # Calculate date range for lookback
        end_date = reference_time.date()
        start_date = end_date - timedelta(days=self.config.lookback_days)

        # Fetch events for the currency in the lookback window
        events = self.repository.get_events(
            start_date=start_date,
            end_date=end_date,
            currencies=[currency],
        )

        return calculate_currency_score(events, currency, reference_time, self.config)

    def get_pair_bias(
        self,
        base: str,
        quote: str,
        at_time: datetime | None = None,
    ) -> float:
        """Calculate the directional bias for a currency pair.

        Bias = base_currency_score - quote_currency_score

        Args:
            base: Base currency code (e.g., "EUR" in EURUSD).
            quote: Quote currency code (e.g., "USD" in EURUSD).
            at_time: Reference time for calculations. Defaults to now.

        Returns:
            Bias value. Positive = bullish, negative = bearish.
        """
        reference_time = at_time if at_time is not None else datetime.now()

        base_score = self.get_currency_score(base, reference_time)
        quote_score = self.get_currency_score(quote, reference_time)

        return calculate_pair_bias(base_score, quote_score)

    def get_bias_signal(
        self,
        base: str,
        quote: str,
        at_time: datetime | None = None,
    ) -> str:
        """Get a directional signal for a currency pair.

        Args:
            base: Base currency code.
            quote: Quote currency code.
            at_time: Reference time for calculations. Defaults to now.

        Returns:
            "BULLISH" if bias > threshold,
            "BEARISH" if bias < -threshold,
            "NEUTRAL" otherwise.
        """
        bias = self.get_pair_bias(base, quote, at_time)
        return get_bias_signal(bias, self.config.min_bias_threshold)
