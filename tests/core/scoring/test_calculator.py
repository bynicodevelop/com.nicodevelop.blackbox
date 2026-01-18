"""Unit tests for the scoring calculator functions."""

from datetime import date, datetime, time, timedelta

import pytest

from blackbox.core.scoring.calculator import (
    calculate_currency_score,
    calculate_decay,
    calculate_event_force,
    calculate_pair_bias,
    event_to_datetime,
    get_bias_signal,
)
from blackbox.core.scoring.config import ScoringConfig
from blackbox.data.models import EconomicEvent, Impact


class TestCalculateDecay:
    """Tests for calculate_decay function."""

    @pytest.mark.parametrize(
        "hours_elapsed,half_life,expected_decay",
        [
            (0, 48, 1.0),
            (48, 48, 0.5),
            (96, 48, 0.25),
            (144, 48, 0.125),
            (24, 48, 0.707),
            (2, 48, 0.971),
        ],
    )
    def test_decay_calculation(
        self, hours_elapsed: float, half_life: float, expected_decay: float
    ) -> None:
        """Test decay follows exponential formula 0.5^(hours/half_life)."""
        reference = datetime(2026, 1, 15, 12, 0, 0)
        event_time = reference - timedelta(hours=hours_elapsed)

        result = calculate_decay(event_time, reference, half_life)

        assert result == pytest.approx(expected_decay, rel=0.01)

    def test_future_event_no_decay(self) -> None:
        """Future events should have decay of 1.0."""
        reference = datetime(2026, 1, 15, 12, 0, 0)
        future_event = datetime(2026, 1, 16, 12, 0, 0)

        result = calculate_decay(future_event, reference, 48)

        assert result == 1.0

    def test_invalid_half_life_raises_error(self) -> None:
        """Zero or negative half_life should raise ValueError."""
        reference = datetime(2026, 1, 15, 12, 0, 0)
        event_time = datetime(2026, 1, 15, 10, 0, 0)

        with pytest.raises(ValueError, match="half_life_hours must be positive"):
            calculate_decay(event_time, reference, 0)

        with pytest.raises(ValueError, match="half_life_hours must be positive"):
            calculate_decay(event_time, reference, -10)


class TestCalculateEventForce:
    """Tests for calculate_event_force function."""

    def test_positive_force(self) -> None:
        """Positive surprise with weight and decay produces positive force."""
        result = calculate_event_force(surprise=2.0, weight=5, decay=0.5)
        assert result == 5.0

    def test_negative_force(self) -> None:
        """Negative surprise produces negative force."""
        result = calculate_event_force(surprise=-3.0, weight=4, decay=1.0)
        assert result == -12.0

    def test_zero_surprise(self) -> None:
        """Zero surprise results in zero force."""
        result = calculate_event_force(surprise=0.0, weight=10, decay=1.0)
        assert result == 0.0

    def test_full_decay_zero_force(self) -> None:
        """Decay of zero means zero contribution."""
        result = calculate_event_force(surprise=5.0, weight=10, decay=0.0)
        assert result == 0.0


class TestEventToDatetime:
    """Tests for event_to_datetime function."""

    def test_with_time(self) -> None:
        """Event with time uses the specified time."""
        event = EconomicEvent(
            date=date(2026, 1, 15),
            time=time(8, 30),
            currency="USD",
            impact=Impact.HIGH,
            event_name="NFP",
        )
        reference = datetime(2026, 1, 15, 12, 0, 0)

        result = event_to_datetime(event, reference)

        assert result == datetime(2026, 1, 15, 8, 30, 0)

    def test_without_time(self) -> None:
        """Event without time defaults to 00:00:00."""
        event = EconomicEvent(
            date=date(2026, 1, 15),
            time=None,
            currency="USD",
            impact=Impact.HOLIDAY,
            event_name="Bank Holiday",
        )
        reference = datetime(2026, 1, 15, 12, 0, 0)

        result = event_to_datetime(event, reference)

        assert result == datetime(2026, 1, 15, 0, 0, 0)


class TestCalculateCurrencyScore:
    """Tests for calculate_currency_score function."""

    @pytest.fixture
    def config(self) -> ScoringConfig:
        """Default scoring configuration."""
        return ScoringConfig(
            half_life_hours=48.0, lookback_days=7, min_bias_threshold=1.0
        )

    def test_single_event_score(self, config: ScoringConfig) -> None:
        """Single event with surprise contributes to score."""
        events = [
            EconomicEvent(
                date=date(2026, 1, 15),
                time=time(8, 0),
                currency="USD",
                impact=Impact.HIGH,
                event_name="NFP",
                actual=1.0,
                forecast=0.5,
                direction=1,
                weight=5,
            ),
        ]
        reference = datetime(2026, 1, 15, 8, 0, 0)

        result = calculate_currency_score(events, "USD", reference, config)

        # surprise = (1.0 - 0.5) / |0.5| * 1 = 1.0
        # decay = 1.0 (same time)
        # force = 1.0 * 5 * 1.0 = 5.0
        assert result == pytest.approx(5.0, rel=0.01)

    def test_filters_by_currency(self, config: ScoringConfig) -> None:
        """Only events for the specified currency are included."""
        events = [
            EconomicEvent(
                date=date(2026, 1, 15),
                time=time(8, 0),
                currency="USD",
                impact=Impact.HIGH,
                event_name="NFP",
                actual=1.0,
                forecast=0.5,
                direction=1,
                weight=5,
            ),
            EconomicEvent(
                date=date(2026, 1, 15),
                time=time(9, 0),
                currency="EUR",
                impact=Impact.HIGH,
                event_name="ECB",
                actual=2.0,
                forecast=1.0,
                direction=1,
                weight=8,
            ),
        ]
        reference = datetime(2026, 1, 15, 10, 0, 0)

        usd_score = calculate_currency_score(events, "USD", reference, config)
        eur_score = calculate_currency_score(events, "EUR", reference, config)

        assert usd_score != eur_score
        assert usd_score > 0
        assert eur_score > 0

    def test_skips_events_without_surprise(self, config: ScoringConfig) -> None:
        """Events with None surprise are ignored."""
        events = [
            EconomicEvent(
                date=date(2026, 1, 15),
                time=time(8, 0),
                currency="USD",
                impact=Impact.HIGH,
                event_name="Pending Event",
                actual=None,
                forecast=1.0,
                previous=0.8,
                weight=5,
            ),
        ]
        reference = datetime(2026, 1, 15, 10, 0, 0)

        result = calculate_currency_score(events, "USD", reference, config)

        assert result == 0.0

    def test_empty_events_returns_zero(self, config: ScoringConfig) -> None:
        """Empty event list returns zero score."""
        result = calculate_currency_score([], "USD", datetime.now(), config)
        assert result == 0.0

    def test_no_matching_currency_returns_zero(self, config: ScoringConfig) -> None:
        """No events for currency returns zero score."""
        events = [
            EconomicEvent(
                date=date(2026, 1, 15),
                time=time(8, 0),
                currency="EUR",
                impact=Impact.HIGH,
                event_name="ECB",
                actual=1.0,
                forecast=0.5,
                weight=5,
            ),
        ]
        reference = datetime(2026, 1, 15, 10, 0, 0)

        result = calculate_currency_score(events, "USD", reference, config)

        assert result == 0.0

    def test_case_insensitive_currency(self, config: ScoringConfig) -> None:
        """Currency matching is case-insensitive."""
        events = [
            EconomicEvent(
                date=date(2026, 1, 15),
                time=time(8, 0),
                currency="USD",
                impact=Impact.HIGH,
                event_name="NFP",
                actual=1.0,
                forecast=0.5,
                weight=5,
            ),
        ]
        reference = datetime(2026, 1, 15, 8, 0, 0)

        upper_result = calculate_currency_score(events, "USD", reference, config)
        lower_result = calculate_currency_score(events, "usd", reference, config)

        assert upper_result == lower_result


class TestCalculatePairBias:
    """Tests for calculate_pair_bias function."""

    @pytest.mark.parametrize(
        "base_score,quote_score,expected_bias",
        [
            (5.0, 1.0, 4.0),
            (2.0, 6.0, -4.0),
            (3.0, 3.0, 0.0),
            (3.0, 3.5, -0.5),
            (10.0, 0.0, 10.0),
            (0.0, 10.0, -10.0),
        ],
    )
    def test_bias_calculation(
        self, base_score: float, quote_score: float, expected_bias: float
    ) -> None:
        """Bias is base_score - quote_score."""
        result = calculate_pair_bias(base_score, quote_score)
        assert result == expected_bias


class TestGetBiasSignal:
    """Tests for get_bias_signal function."""

    @pytest.mark.parametrize(
        "bias,threshold,expected_signal",
        [
            (4.0, 1.0, "BULLISH"),
            (-4.0, 1.0, "BEARISH"),
            (0.5, 1.0, "NEUTRAL"),
            (-0.5, 1.0, "NEUTRAL"),
            (1.0, 1.0, "NEUTRAL"),  # Equal to threshold is neutral
            (-1.0, 1.0, "NEUTRAL"),  # Equal to -threshold is neutral
            (1.01, 1.0, "BULLISH"),
            (-1.01, 1.0, "BEARISH"),
        ],
    )
    def test_signal_generation(
        self, bias: float, threshold: float, expected_signal: str
    ) -> None:
        """Signal is BULLISH/BEARISH/NEUTRAL based on threshold."""
        result = get_bias_signal(bias, threshold)
        assert result == expected_signal


class TestScoringConfig:
    """Tests for ScoringConfig validation."""

    def test_valid_config(self) -> None:
        """Valid configuration creates successfully."""
        config = ScoringConfig(
            half_life_hours=24.0, lookback_days=14, min_bias_threshold=0.5
        )
        assert config.half_life_hours == 24.0
        assert config.lookback_days == 14
        assert config.min_bias_threshold == 0.5

    def test_default_values(self) -> None:
        """Default configuration values are applied."""
        config = ScoringConfig()
        assert config.half_life_hours == 48.0
        assert config.lookback_days == 7
        assert config.min_bias_threshold == 1.0

    def test_invalid_half_life_raises_error(self) -> None:
        """Zero or negative half_life raises ValueError."""
        with pytest.raises(ValueError, match="half_life_hours must be positive"):
            ScoringConfig(half_life_hours=0)

        with pytest.raises(ValueError, match="half_life_hours must be positive"):
            ScoringConfig(half_life_hours=-10)

    def test_invalid_lookback_days_raises_error(self) -> None:
        """Zero or negative lookback_days raises ValueError."""
        with pytest.raises(ValueError, match="lookback_days must be positive"):
            ScoringConfig(lookback_days=0)

    def test_invalid_threshold_raises_error(self) -> None:
        """Negative threshold raises ValueError."""
        with pytest.raises(ValueError, match="min_bias_threshold must be non-negative"):
            ScoringConfig(min_bias_threshold=-1.0)
