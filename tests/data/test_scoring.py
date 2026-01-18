"""Tests for scoring module."""

import pytest

from blackbox.data.scoring import calculate_surprise


class TestCalculateSurprise:
    """Tests for calculate_surprise function."""

    @pytest.mark.parametrize(
        "actual,forecast,direction,expected",
        [
            # Standard positive surprise (actual > forecast, direction +1)
            (300000, 200000, +1, 0.5),
            # Negative surprise with negative direction
            (0.04, 0.035, -1, pytest.approx(-0.1428571, rel=1e-5)),
            # Negative surprise (actual < forecast, direction +1)
            (0.002, 0.003, +1, pytest.approx(-0.3333333, rel=1e-5)),
            # Actual equals forecast -> no surprise
            (100, 100, +1, 0.0),
            (100, 100, -1, 0.0),
            # Large positive surprise
            (500, 100, +1, 4.0),
            # Negative forecast (still valid): (-50 - (-100)) / 100 = 0.5
            (-50, -100, +1, 0.5),
            # Direction reversal
            (150, 100, -1, -0.5),
            (50, 100, -1, 0.5),
        ],
    )
    def test_calculate_surprise_valid_inputs(
        self, actual: float, forecast: float, direction: int, expected: float
    ):
        """Test surprise calculation with valid inputs."""
        result = calculate_surprise(actual, forecast, direction)
        if isinstance(expected, float):
            assert result == pytest.approx(expected, rel=1e-5)
        else:
            assert result == expected

    def test_calculate_surprise_none_actual(self):
        """Test that None actual returns None."""
        assert calculate_surprise(None, 0.003, +1) is None

    def test_calculate_surprise_none_forecast(self):
        """Test that None forecast returns None."""
        assert calculate_surprise(0.002, None, +1) is None

    def test_calculate_surprise_both_none(self):
        """Test that both None returns None."""
        assert calculate_surprise(None, None, +1) is None

    def test_calculate_surprise_zero_forecast(self):
        """Test that zero forecast returns None (division by zero)."""
        assert calculate_surprise(0.002, 0, +1) is None
        assert calculate_surprise(100, 0, -1) is None
        assert calculate_surprise(0, 0, +1) is None

    def test_calculate_surprise_zero_actual(self):
        """Test surprise with zero actual but non-zero forecast."""
        # actual=0, forecast=100, direction=+1 -> -1.0
        result = calculate_surprise(0, 100, +1)
        assert result == pytest.approx(-1.0)

        # actual=0, forecast=100, direction=-1 -> +1.0
        result = calculate_surprise(0, 100, -1)
        assert result == pytest.approx(1.0)


class TestCalculateSurpriseEdgeCases:
    """Edge case tests for calculate_surprise."""

    def test_very_small_forecast(self):
        """Test with very small forecast values."""
        result = calculate_surprise(0.0001, 0.00001, +1)
        assert result == pytest.approx(9.0, rel=1e-5)

    def test_very_large_values(self):
        """Test with very large values."""
        result = calculate_surprise(1e12, 1e11, +1)
        assert result == pytest.approx(9.0, rel=1e-5)

    def test_mixed_sign_values(self):
        """Test with mixed positive/negative values."""
        # Actual positive, forecast negative: (50 - (-100)) / 100 = 1.5
        result = calculate_surprise(50, -100, +1)
        assert result == pytest.approx(1.5, rel=1e-5)

        # Actual negative, forecast positive: (-50 - 100) / 100 = -1.5
        result = calculate_surprise(-50, 100, +1)
        assert result == pytest.approx(-1.5, rel=1e-5)

    def test_direction_zero(self):
        """Test with direction=0 (edge case, should return 0)."""
        result = calculate_surprise(200, 100, 0)
        assert result == 0.0


class TestCalculateSurpriseFromTicketExamples:
    """Test cases from the ticket specification."""

    @pytest.mark.parametrize(
        "actual,forecast,direction,expected",
        [
            (300000, 200000, +1, 0.5),
            (0.04, 0.035, -1, pytest.approx(-0.143, rel=1e-2)),
            (0.002, 0.003, +1, pytest.approx(-0.333, rel=1e-2)),
            (None, 0.003, +1, None),
            (0.002, None, +1, None),
            (0.002, 0, +1, None),
        ],
    )
    def test_ticket_examples(
        self, actual: float | None, forecast: float | None, direction: int, expected
    ):
        """Test the exact examples from the ticket."""
        result = calculate_surprise(actual, forecast, direction)
        if expected is None:
            assert result is None
        else:
            assert result == expected
