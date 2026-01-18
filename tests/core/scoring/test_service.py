"""Integration tests for the ScoringService."""

from datetime import date, datetime, time

import pytest

from blackbox.core.scoring.config import ScoringConfig
from blackbox.core.scoring.service import ScoringService
from blackbox.data.models import EconomicEvent, Impact
from blackbox.data.storage.repository import EventRepository


class TestScoringServiceIntegration:
    """Integration tests for ScoringService with real database."""

    def test_get_currency_score_with_events(
        self,
        event_repository: EventRepository,
        scoring_config: ScoringConfig,
        sample_events: list[EconomicEvent],
    ) -> None:
        """Currency score calculation with events in database."""
        # Insert events
        event_repository.upsert_events(sample_events)
        event_repository.session.commit()

        service = ScoringService(scoring_config, event_repository)
        reference = datetime(2026, 1, 15, 12, 0, 0)

        usd_score = service.get_currency_score("USD", reference)
        eur_score = service.get_currency_score("EUR", reference)

        # Both should have non-zero scores
        assert usd_score != 0.0
        assert eur_score != 0.0

    def test_get_currency_score_no_events(
        self,
        event_repository: EventRepository,
        scoring_config: ScoringConfig,
    ) -> None:
        """Currency score with no events returns zero."""
        service = ScoringService(scoring_config, event_repository)
        reference = datetime(2026, 1, 15, 12, 0, 0)

        score = service.get_currency_score("USD", reference)

        assert score == 0.0

    def test_get_currency_score_case_insensitive(
        self,
        event_repository: EventRepository,
        scoring_config: ScoringConfig,
        sample_events: list[EconomicEvent],
    ) -> None:
        """Currency matching is case-insensitive."""
        event_repository.upsert_events(sample_events)
        event_repository.session.commit()

        service = ScoringService(scoring_config, event_repository)
        reference = datetime(2026, 1, 15, 12, 0, 0)

        upper_score = service.get_currency_score("USD", reference)
        lower_score = service.get_currency_score("usd", reference)

        assert upper_score == lower_score

    def test_get_pair_bias_positive(
        self,
        event_repository: EventRepository,
        scoring_config: ScoringConfig,
        sample_events_bullish_eur: list[EconomicEvent],
    ) -> None:
        """Pair bias is positive when base currency is stronger."""
        event_repository.upsert_events(sample_events_bullish_eur)
        event_repository.session.commit()

        service = ScoringService(scoring_config, event_repository)
        reference = datetime(2026, 1, 15, 12, 0, 0)

        bias = service.get_pair_bias("EUR", "USD", reference)

        # EUR should be stronger, so EURUSD bias is positive
        assert bias > 0

    def test_get_pair_bias_negative(
        self,
        event_repository: EventRepository,
        scoring_config: ScoringConfig,
        sample_events_bearish_eur: list[EconomicEvent],
    ) -> None:
        """Pair bias is negative when quote currency is stronger."""
        event_repository.upsert_events(sample_events_bearish_eur)
        event_repository.session.commit()

        service = ScoringService(scoring_config, event_repository)
        reference = datetime(2026, 1, 15, 12, 0, 0)

        bias = service.get_pair_bias("EUR", "USD", reference)

        # USD should be stronger, so EURUSD bias is negative
        assert bias < 0

    def test_get_bias_signal_bullish(
        self,
        event_repository: EventRepository,
        scoring_config: ScoringConfig,
        sample_events_bullish_eur: list[EconomicEvent],
    ) -> None:
        """Signal is BULLISH when bias exceeds threshold."""
        event_repository.upsert_events(sample_events_bullish_eur)
        event_repository.session.commit()

        service = ScoringService(scoring_config, event_repository)
        reference = datetime(2026, 1, 15, 12, 0, 0)

        signal = service.get_bias_signal("EUR", "USD", reference)

        assert signal == "BULLISH"

    def test_get_bias_signal_bearish(
        self,
        event_repository: EventRepository,
        scoring_config: ScoringConfig,
        sample_events_bearish_eur: list[EconomicEvent],
    ) -> None:
        """Signal is BEARISH when bias is below negative threshold."""
        event_repository.upsert_events(sample_events_bearish_eur)
        event_repository.session.commit()

        service = ScoringService(scoring_config, event_repository)
        reference = datetime(2026, 1, 15, 12, 0, 0)

        signal = service.get_bias_signal("EUR", "USD", reference)

        assert signal == "BEARISH"

    def test_get_bias_signal_neutral(
        self,
        event_repository: EventRepository,
    ) -> None:
        """Signal is NEUTRAL when bias is within threshold."""
        # Use high threshold so any small bias is neutral
        config = ScoringConfig(
            half_life_hours=48.0,
            lookback_days=7,
            min_bias_threshold=100.0,  # Very high threshold
        )

        # Create events with small differences
        events = [
            EconomicEvent(
                date=date(2026, 1, 15),
                time=time(9, 0),
                currency="EUR",
                impact=Impact.HIGH,
                event_name="ECB",
                actual=4.5,
                forecast=4.5,  # No surprise
                previous=4.0,
                weight=10,
            ),
            EconomicEvent(
                date=date(2026, 1, 15),
                time=time(8, 30),
                currency="USD",
                impact=Impact.HIGH,
                event_name="NFP",
                actual=200.0,
                forecast=200.0,  # No surprise
                previous=180.0,
                weight=8,
            ),
        ]

        event_repository.upsert_events(events)
        event_repository.session.commit()

        service = ScoringService(config, event_repository)
        reference = datetime(2026, 1, 15, 12, 0, 0)

        signal = service.get_bias_signal("EUR", "USD", reference)

        assert signal == "NEUTRAL"

    def test_lookback_window_filters_events(
        self,
        event_repository: EventRepository,
    ) -> None:
        """Events outside lookback window are not included."""
        config = ScoringConfig(
            half_life_hours=48.0,
            lookback_days=3,  # Only 3 days lookback
            min_bias_threshold=1.0,
        )

        # Event within window
        recent_event = EconomicEvent(
            date=date(2026, 1, 15),
            time=time(9, 0),
            currency="USD",
            impact=Impact.HIGH,
            event_name="Recent Event",
            actual=300.0,
            forecast=200.0,
            weight=10,
        )

        # Event outside window (10 days ago)
        old_event = EconomicEvent(
            date=date(2026, 1, 5),
            time=time(9, 0),
            currency="USD",
            impact=Impact.HIGH,
            event_name="Old Event",
            actual=300.0,
            forecast=200.0,
            weight=10,
        )

        event_repository.upsert_events([recent_event, old_event])
        event_repository.session.commit()

        service = ScoringService(config, event_repository)

        # Reference at Jan 15
        reference = datetime(2026, 1, 15, 12, 0, 0)
        score = service.get_currency_score("USD", reference)

        # Only recent event should be included
        # The old event from Jan 5 is outside the 3-day window
        assert score > 0

        # Now reference at Jan 4 (old event from Jan 5 is in the future, not included)
        reference_old = datetime(2026, 1, 4, 12, 0, 0)
        score_old = service.get_currency_score("USD", reference_old)

        # Old event from Jan 5 is in the future relative to Jan 4, so not included
        # (window is Jan 1-4, event is Jan 5)
        assert score_old == 0.0

    def test_decay_reduces_old_event_impact(
        self,
        event_repository: EventRepository,
    ) -> None:
        """Older events have reduced impact due to decay."""
        config = ScoringConfig(
            half_life_hours=24.0,  # 24-hour half-life
            lookback_days=7,
            min_bias_threshold=1.0,
        )

        event = EconomicEvent(
            date=date(2026, 1, 15),
            time=time(12, 0),
            currency="USD",
            impact=Impact.HIGH,
            event_name="Test Event",
            actual=300.0,
            forecast=200.0,
            weight=10,
        )

        event_repository.upsert_events([event])
        event_repository.session.commit()

        service = ScoringService(config, event_repository)

        # Score at event time (no decay)
        score_no_decay = service.get_currency_score(
            "USD", datetime(2026, 1, 15, 12, 0, 0)
        )

        # Score 24 hours later (50% decay)
        score_half_decay = service.get_currency_score(
            "USD", datetime(2026, 1, 16, 12, 0, 0)
        )

        # Score 48 hours later (25% decay)
        score_quarter_decay = service.get_currency_score(
            "USD", datetime(2026, 1, 17, 12, 0, 0)
        )

        assert score_no_decay > score_half_decay
        assert score_half_decay > score_quarter_decay
        assert score_half_decay == pytest.approx(score_no_decay * 0.5, rel=0.01)
        assert score_quarter_decay == pytest.approx(score_no_decay * 0.25, rel=0.01)

    def test_default_reference_time(
        self,
        event_repository: EventRepository,
        scoring_config: ScoringConfig,
    ) -> None:
        """Methods use current time when at_time is not provided."""
        service = ScoringService(scoring_config, event_repository)

        # Should not raise, even with no events
        score = service.get_currency_score("USD")
        bias = service.get_pair_bias("EUR", "USD")
        signal = service.get_bias_signal("EUR", "USD")

        assert score == 0.0
        assert bias == 0.0
        assert signal == "NEUTRAL"
