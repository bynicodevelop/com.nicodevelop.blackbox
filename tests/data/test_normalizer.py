"""Tests for the economic value normalizer."""

from blackbox.data.normalizer import format_normalized_value, normalize_value


class TestNormalizeValue:
    """Tests for normalize_value function."""

    def test_normalize_none(self):
        """Test that None input returns None."""
        assert normalize_value(None) is None

    def test_normalize_empty_string(self):
        """Test that empty string returns None."""
        assert normalize_value("") is None
        assert normalize_value("   ") is None

    def test_normalize_simple_number(self):
        """Test normalization of simple numbers without units."""
        assert normalize_value("123") == 123.0
        assert normalize_value("1.5") == 1.5
        assert normalize_value("0.25") == 0.25

    def test_normalize_thousands(self):
        """Test normalization of K (thousands) suffix."""
        assert normalize_value("223K") == 223000.0
        assert normalize_value("223k") == 223000.0
        assert normalize_value("1.5K") == 1500.0
        assert normalize_value("0.5k") == 500.0

    def test_normalize_millions(self):
        """Test normalization of M (millions) suffix."""
        assert normalize_value("1M") == 1000000.0
        assert normalize_value("1m") == 1000000.0
        assert normalize_value("1.5M") == 1500000.0
        assert normalize_value("2.75m") == 2750000.0

    def test_normalize_billions(self):
        """Test normalization of B (billions) suffix."""
        assert normalize_value("1B") == 1000000000.0
        assert normalize_value("1b") == 1000000000.0
        assert normalize_value("2.5B") == 2500000000.0
        assert normalize_value("-50B") == -50000000000.0

    def test_normalize_trillions(self):
        """Test normalization of T (trillions) suffix."""
        assert normalize_value("1T") == 1000000000000.0
        assert normalize_value("1t") == 1000000000000.0
        assert normalize_value("2.5T") == 2500000000000.0

    def test_normalize_percentages(self):
        """Test normalization of percentage values."""
        assert normalize_value("2.5%") == 0.025
        assert normalize_value("100%") == 1.0
        assert normalize_value("0.1%") == 0.001
        assert normalize_value("-1.5%") == -0.015

    def test_normalize_negative_values(self):
        """Test normalization of negative values."""
        assert normalize_value("-223K") == -223000.0
        assert normalize_value("-1.5M") == -1500000.0
        assert normalize_value("-2.5%") == -0.025
        assert normalize_value("-100") == -100.0

    def test_normalize_with_thousand_separators(self):
        """Test normalization of values with thousand separators."""
        assert normalize_value("1,234") == 1234.0
        assert normalize_value("1,234,567") == 1234567.0
        assert normalize_value("1,234.56") == 1234.56

    def test_normalize_with_whitespace(self):
        """Test normalization handles whitespace correctly."""
        assert normalize_value("  223K  ") == 223000.0
        assert normalize_value("2.5 %") == 0.025
        assert normalize_value(" -1.5M ") == -1500000.0

    def test_normalize_with_comparison_operators(self):
        """Test that comparison operators are stripped."""
        assert normalize_value("<0.1%") == 0.001
        assert normalize_value(">100K") == 100000.0
        assert normalize_value("≤50M") == 50000000.0
        assert normalize_value("≥2.5%") == 0.025

    def test_normalize_invalid_values(self):
        """Test that invalid values return None."""
        assert normalize_value("abc") is None
        assert normalize_value("N/A") is None
        assert normalize_value("--") is None
        assert normalize_value("TBD") is None

    def test_normalize_real_world_examples(self):
        """Test with real-world economic calendar values."""
        # Non-Farm Payrolls style
        assert normalize_value("223K") == 223000.0
        assert normalize_value("215K") == 215000.0

        # GDP style
        assert normalize_value("2.1%") == 0.021
        assert normalize_value("-0.3%") == -0.003

        # Trade Balance style
        assert normalize_value("-68.3B") == -68300000000.0

        # Interest Rate style
        assert normalize_value("5.25%") == 0.0525

        # CPI style
        assert normalize_value("0.2%") == 0.002


class TestFormatNormalizedValue:
    """Tests for format_normalized_value function."""

    def test_format_none(self):
        """Test that None returns empty string."""
        assert format_normalized_value(None) == ""

    def test_format_thousands(self):
        """Test formatting of thousands."""
        assert format_normalized_value(223000) == "223.00K"
        assert format_normalized_value(1500) == "1.50K"

    def test_format_millions(self):
        """Test formatting of millions."""
        assert format_normalized_value(1500000) == "1.50M"
        assert format_normalized_value(2750000) == "2.75M"

    def test_format_billions(self):
        """Test formatting of billions."""
        assert format_normalized_value(1000000000) == "1.00B"
        assert format_normalized_value(-50000000000) == "-50.00B"

    def test_format_trillions(self):
        """Test formatting of trillions."""
        assert format_normalized_value(1000000000000) == "1.00T"
        assert format_normalized_value(2500000000000) == "2.50T"

    def test_format_small_values(self):
        """Test formatting of small values (no suffix)."""
        assert format_normalized_value(123) == "123.00"
        assert format_normalized_value(0.025) == "0.03"
        assert format_normalized_value(0.001) == "0.00"

    def test_format_precision(self):
        """Test formatting with different precision levels."""
        assert format_normalized_value(223456, precision=0) == "223K"
        assert format_normalized_value(223456, precision=1) == "223.5K"
        assert format_normalized_value(223456, precision=3) == "223.456K"

    def test_format_without_suffix(self):
        """Test formatting without suffix."""
        assert format_normalized_value(223000, use_suffix=False) == "223000.00"
        assert format_normalized_value(1500000, use_suffix=False) == "1500000.00"

    def test_format_negative_values(self):
        """Test formatting of negative values."""
        assert format_normalized_value(-223000) == "-223.00K"
        assert format_normalized_value(-1500000) == "-1.50M"
        assert format_normalized_value(-0.025) == "-0.03"
