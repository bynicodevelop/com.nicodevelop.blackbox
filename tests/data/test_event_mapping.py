"""Tests for event mapping module."""

import pytest

from blackbox.data.event_mapping import (
    EVENT_MAPPING,
    EventMetadata,
    get_event_metadata,
)
from blackbox.data.models import EventType


class TestEventMetadata:
    """Tests for EventMetadata dataclass."""

    def test_event_metadata_creation(self):
        """Test creating EventMetadata with valid values."""
        metadata = EventMetadata(EventType.EMPLOYMENT, +1, 10)
        assert metadata.event_type == EventType.EMPLOYMENT
        assert metadata.direction == 1
        assert metadata.weight == 10

    def test_event_metadata_frozen(self):
        """Test that EventMetadata is immutable."""
        metadata = EventMetadata(EventType.EMPLOYMENT, +1, 10)
        with pytest.raises(AttributeError):
            metadata.weight = 5


class TestEventMapping:
    """Tests for EVENT_MAPPING dictionary."""

    def test_mapping_not_empty(self):
        """Test that mapping contains events."""
        assert len(EVENT_MAPPING) > 0

    def test_mapping_keys_lowercase(self):
        """Test that all mapping keys are lowercase."""
        for key in EVENT_MAPPING:
            assert key == key.lower(), f"Key '{key}' is not lowercase"

    def test_mapping_keys_trimmed(self):
        """Test that all mapping keys are trimmed."""
        for key in EVENT_MAPPING:
            assert key == key.strip(), f"Key '{key}' has leading/trailing whitespace"

    def test_mapping_values_valid(self):
        """Test that all mapping values have valid metadata."""
        for key, metadata in EVENT_MAPPING.items():
            assert isinstance(metadata, EventMetadata), f"Invalid metadata for '{key}'"
            assert isinstance(metadata.event_type, EventType), f"Invalid event_type for '{key}'"
            assert metadata.direction in (-1, +1), f"Invalid direction for '{key}'"
            assert 1 <= metadata.weight <= 10, f"Invalid weight for '{key}'"

    def test_high_impact_events_present(self):
        """Test that major high-impact events are in the mapping."""
        high_impact_events = [
            "non-farm employment change",
            "unemployment rate",
            "cpi m/m",
            "cpi y/y",
            "gdp q/q",
            "federal funds rate",
        ]
        for event in high_impact_events:
            assert event in EVENT_MAPPING, f"High-impact event '{event}' missing from mapping"


class TestGetEventMetadata:
    """Tests for get_event_metadata function."""

    def test_known_event_exact_match(self):
        """Test metadata retrieval for known event with exact match."""
        metadata = get_event_metadata("Non-Farm Employment Change")
        assert metadata.event_type == EventType.EMPLOYMENT
        assert metadata.direction == +1
        assert metadata.weight == 10

    def test_known_event_lowercase(self):
        """Test metadata retrieval with lowercase input."""
        metadata = get_event_metadata("non-farm employment change")
        assert metadata.event_type == EventType.EMPLOYMENT
        assert metadata.direction == +1
        assert metadata.weight == 10

    def test_known_event_uppercase(self):
        """Test metadata retrieval with uppercase input."""
        metadata = get_event_metadata("NON-FARM EMPLOYMENT CHANGE")
        assert metadata.event_type == EventType.EMPLOYMENT
        assert metadata.direction == +1
        assert metadata.weight == 10

    def test_known_event_with_whitespace(self):
        """Test metadata retrieval with leading/trailing whitespace."""
        metadata = get_event_metadata("  CPI m/m  ")
        assert metadata.event_type == EventType.INFLATION
        assert metadata.direction == +1
        assert metadata.weight == 10

    def test_unknown_event_returns_default(self):
        """Test that unknown events return default metadata."""
        metadata = get_event_metadata("Unknown Random Event XYZ")
        assert metadata.event_type == EventType.OTHER
        assert metadata.direction == +1
        assert metadata.weight == 1

    def test_empty_string_returns_default(self):
        """Test that empty string returns default metadata."""
        metadata = get_event_metadata("")
        assert metadata.event_type == EventType.OTHER
        assert metadata.direction == +1
        assert metadata.weight == 1

    def test_whitespace_only_returns_default(self):
        """Test that whitespace-only string returns default metadata."""
        metadata = get_event_metadata("   ")
        assert metadata.event_type == EventType.OTHER
        assert metadata.direction == +1
        assert metadata.weight == 1

    @pytest.mark.parametrize(
        "event_name,expected_type,expected_direction",
        [
            ("Unemployment Rate", EventType.EMPLOYMENT, -1),
            ("CPI y/y", EventType.INFLATION, +1),
            ("GDP q/q", EventType.GROWTH, +1),
            ("Manufacturing PMI", EventType.PMI, +1),
            ("Building Permits", EventType.HOUSING, +1),
            ("Consumer Confidence", EventType.SENTIMENT, +1),
            ("Trade Balance", EventType.TRADE, +1),
            ("Federal Funds Rate", EventType.INTEREST_RATE, +1),
        ],
    )
    def test_event_types_correctly_categorized(
        self, event_name, expected_type, expected_direction
    ):
        """Test that events are categorized into correct types."""
        metadata = get_event_metadata(event_name)
        assert metadata.event_type == expected_type
        assert metadata.direction == expected_direction

    def test_negative_direction_events(self):
        """Test events with negative direction (higher = bearish)."""
        # Unemployment rate - higher is bad for currency
        metadata = get_event_metadata("Unemployment Rate")
        assert metadata.direction == -1

        # Jobless claims - higher is bad
        metadata = get_event_metadata("Initial Jobless Claims")
        assert metadata.direction == -1

        # Import prices - higher imports = trade deficit
        metadata = get_event_metadata("Import Prices m/m")
        assert metadata.direction == -1


class TestEventTypeEnum:
    """Tests for EventType enum."""

    def test_all_event_types_have_values(self):
        """Test that all EventType enum members have string values."""
        for event_type in EventType:
            assert isinstance(event_type.value, str)
            assert len(event_type.value) > 0

    def test_event_type_values_unique(self):
        """Test that all EventType values are unique."""
        values = [et.value for et in EventType]
        assert len(values) == len(set(values))

    def test_expected_event_types_exist(self):
        """Test that expected event types are defined."""
        expected_types = [
            "interest_rate",
            "employment",
            "inflation",
            "growth",
            "pmi",
            "housing",
            "sentiment",
            "trade",
            "other",
        ]
        actual_values = [et.value for et in EventType]
        for expected in expected_types:
            assert expected in actual_values, f"EventType '{expected}' not found"
