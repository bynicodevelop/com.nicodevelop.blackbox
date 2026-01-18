"""Tests for event mapping module."""

import pytest

from blackbox.data.event_mapping import (
    EVENT_PATTERNS,
    EXACT_EVENT_MAPPING,
    EventMetadata,
    EventPattern,
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


class TestEventPattern:
    """Tests for EventPattern dataclass."""

    def test_event_pattern_creation(self):
        """Test creating EventPattern with valid values."""
        import re

        pattern = EventPattern(
            re.compile(r"\btest\b", re.IGNORECASE),
            EventMetadata(EventType.PMI, +1, 5),
            priority=50,
        )
        assert pattern.priority == 50
        assert pattern.metadata.event_type == EventType.PMI


class TestEventPatterns:
    """Tests for EVENT_PATTERNS list."""

    def test_patterns_not_empty(self):
        """Test that patterns list contains patterns."""
        assert len(EVENT_PATTERNS) > 0

    def test_patterns_sorted_by_priority(self):
        """Test that patterns are sorted by priority (highest first)."""
        priorities = [p.priority for p in EVENT_PATTERNS]
        assert priorities == sorted(priorities, reverse=True)

    def test_all_patterns_have_valid_metadata(self):
        """Test that all patterns have valid metadata."""
        for pattern in EVENT_PATTERNS:
            assert isinstance(pattern, EventPattern)
            assert isinstance(pattern.metadata, EventMetadata)
            assert isinstance(pattern.metadata.event_type, EventType)
            assert pattern.metadata.direction in (-1, 0, +1)
            assert 1 <= pattern.metadata.weight <= 10


class TestExactEventMapping:
    """Tests for EXACT_EVENT_MAPPING dictionary."""

    def test_mapping_not_empty(self):
        """Test that mapping contains events."""
        assert len(EXACT_EVENT_MAPPING) > 0

    def test_mapping_keys_lowercase(self):
        """Test that all mapping keys are lowercase."""
        for key in EXACT_EVENT_MAPPING:
            assert key == key.lower(), f"Key '{key}' is not lowercase"

    def test_mapping_keys_trimmed(self):
        """Test that all mapping keys are trimmed."""
        for key in EXACT_EVENT_MAPPING:
            assert key == key.strip(), f"Key '{key}' has leading/trailing whitespace"

    def test_mapping_values_valid(self):
        """Test that all mapping values have valid metadata."""
        for key, metadata in EXACT_EVENT_MAPPING.items():
            assert isinstance(metadata, EventMetadata), f"Invalid metadata for '{key}'"
            assert isinstance(metadata.event_type, EventType), (
                f"Invalid event_type for '{key}'"
            )
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
            assert event in EXACT_EVENT_MAPPING, (
                f"High-impact event '{event}' missing from mapping"
            )


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


class TestPatternMatching:
    """Tests for regex pattern matching functionality."""

    @pytest.mark.parametrize(
        "event_name,expected_type",
        [
            # PMI variants - should all match PMI
            ("Spanish Manufacturing PMI", EventType.PMI),
            ("Italian Manufacturing PMI", EventType.PMI),
            ("French Final Manufacturing PMI", EventType.PMI),
            ("German Final Manufacturing PMI", EventType.PMI),
            ("Final Manufacturing PMI", EventType.PMI),
            ("Spanish Services PMI", EventType.PMI),
            ("Italian Services PMI", EventType.PMI),
            ("Construction PMI", EventType.PMI),
            ("Ivey PMI", EventType.PMI),
            ("ISM Manufacturing PMI", EventType.PMI),
            ("ISM Services PMI", EventType.PMI),
            ("Flash Manufacturing PMI", EventType.PMI),
            ("Flash Services PMI", EventType.PMI),
            ("Chicago PMI", EventType.PMI),
            # CPI variants - should all match INFLATION
            ("German Prelim CPI m/m", EventType.INFLATION),
            ("French Prelim CPI m/m", EventType.INFLATION),
            ("Core CPI Flash Estimate y/y", EventType.INFLATION),
            ("CPI Flash Estimate y/y", EventType.INFLATION),
            ("Italian Prelim CPI m/m", EventType.INFLATION),
            ("French Final CPI m/m", EventType.INFLATION),
            ("German Final CPI m/m", EventType.INFLATION),
            ("Core CPI m/m", EventType.INFLATION),
            ("Core CPI y/y", EventType.INFLATION),
            ("National Core CPI y/y", EventType.INFLATION),
            ("Tokyo Core CPI y/y", EventType.INFLATION),
            ("Core PCE Price Index m/m", EventType.INFLATION),
            # PPI variants
            ("Core PPI m/m", EventType.INFLATION),
            ("PPI m/m", EventType.INFLATION),
            ("PPI y/y", EventType.INFLATION),
            ("German PPI m/m", EventType.INFLATION),
            # Unemployment/Employment variants
            ("Spanish Unemployment Change", EventType.EMPLOYMENT),
            ("German Unemployment Change", EventType.EMPLOYMENT),
            ("Italian Monthly Unemployment Rate", EventType.EMPLOYMENT),
            ("Claimant Count Change", EventType.EMPLOYMENT),
            ("ADP Non-Farm Employment Change", EventType.EMPLOYMENT),
            ("ADP Weekly Employment Change", EventType.EMPLOYMENT),
            ("Employment Change", EventType.EMPLOYMENT),
            ("JOLTS Job Openings", EventType.EMPLOYMENT),
            ("Challenger Job Cuts y/y", EventType.EMPLOYMENT),
            # Trade Balance variants
            ("French Trade Balance", EventType.TRADE),
            ("German Trade Balance", EventType.TRADE),
            ("Italian Trade Balance", EventType.TRADE),
            ("USD-Denominated Trade Balance", EventType.TRADE),
            ("Goods Trade Balance", EventType.TRADE),
            ("Current Account", EventType.TRADE),
            ("Import Prices m/m", EventType.TRADE),
            # Housing variants
            ("Building Approvals m/m", EventType.HOUSING),
            ("Building Consents m/m", EventType.HOUSING),
            ("Building Permits", EventType.HOUSING),
            ("Building Permits m/m", EventType.HOUSING),
            ("Halifax HPI m/m", EventType.HOUSING),
            ("Nationwide HPI m/m", EventType.HOUSING),
            ("S&P/CS Composite-20 HPI y/y", EventType.HOUSING),
            ("New Home Sales", EventType.HOUSING),
            ("Existing Home Sales", EventType.HOUSING),
            ("Pending Home Sales m/m", EventType.HOUSING),
            ("Housing Starts", EventType.HOUSING),
            ("Construction Spending m/m", EventType.HOUSING),
            ("Construction Output m/m", EventType.HOUSING),
            ("Mortgage Approvals", EventType.HOUSING),
            # Retail Sales / Growth
            ("German Retail Sales m/m", EventType.GROWTH),
            ("Italian Retail Sales m/m", EventType.GROWTH),
            ("Retail Sales m/m", EventType.GROWTH),
            ("Core Retail Sales m/m", EventType.GROWTH),
            ("Industrial Production m/m", EventType.GROWTH),
            ("German Industrial Production m/m", EventType.GROWTH),
            ("French Industrial Production m/m", EventType.GROWTH),
            ("Factory Orders m/m", EventType.GROWTH),
            ("German Factory Orders m/m", EventType.GROWTH),
            # Sentiment
            ("Consumer Confidence", EventType.SENTIMENT),
            ("CB Consumer Confidence", EventType.SENTIMENT),
            ("Sentix Investor Confidence", EventType.SENTIMENT),
            ("NZIER Business Confidence", EventType.SENTIMENT),
            ("NAB Business Confidence", EventType.SENTIMENT),
            ("ANZ Business Confidence", EventType.SENTIMENT),
            ("Westpac Consumer Sentiment", EventType.SENTIMENT),
            ("Economy Watchers Sentiment", EventType.SENTIMENT),
            ("ZEW Economic Sentiment", EventType.SENTIMENT),
            ("German ifo Business Climate", EventType.SENTIMENT),
            ("GfK Consumer Confidence", EventType.SENTIMENT),
            # Interest Rate
            ("Federal Funds Rate", EventType.INTEREST_RATE),
            ("FOMC Statement", EventType.INTEREST_RATE),
            ("FOMC Press Conference", EventType.INTEREST_RATE),
            ("Overnight Rate", EventType.INTEREST_RATE),
            # GDP / Growth
            ("Final GDP q/q", EventType.GROWTH),
            ("German Prelim GDP q/q", EventType.GROWTH),
            ("French Flash GDP q/q", EventType.GROWTH),
            ("Spanish Flash GDP q/q", EventType.GROWTH),
            ("Italian Prelim GDP q/q", EventType.GROWTH),
        ],
    )
    def test_pattern_matching_categorizes_correctly(self, event_name, expected_type):
        """Test that pattern matching correctly categorizes events."""
        metadata = get_event_metadata(event_name)
        assert metadata.event_type == expected_type, (
            f"Event '{event_name}' should be {expected_type.value}, "
            f"got {metadata.event_type.value}"
        )

    @pytest.mark.parametrize(
        "event_name",
        [
            "FOMC Member Paulson Speaks",
            "FOMC Member Kashkari Speaks",
            "FOMC Member Barkin Speaks",
            "MPC Member Taylor Speaks",
            "President Trump Speaks",
            "ECB President Lagarde Speaks",
            "BOE Gov Bailey Speaks",
        ],
    )
    def test_speakers_categorized_as_other(self, event_name):
        """Test that speaker events are categorized as OTHER."""
        metadata = get_event_metadata(event_name)
        assert metadata.event_type == EventType.OTHER

    @pytest.mark.parametrize(
        "event_name",
        [
            "Bank Holiday",
            "French Bank Holiday",
            "German Bank Holiday",
            "Italian Bank Holiday",
        ],
    )
    def test_bank_holidays_categorized_as_other(self, event_name):
        """Test that bank holidays are categorized as OTHER with low weight."""
        metadata = get_event_metadata(event_name)
        assert metadata.event_type == EventType.OTHER
        assert metadata.weight == 1  # Minimum weight

    def test_exact_match_takes_priority(self):
        """Test that exact match in EXACT_EVENT_MAPPING takes priority over patterns."""
        # "manufacturing pmi" is in exact mapping with weight 7
        metadata = get_event_metadata("Manufacturing PMI")
        assert metadata.event_type == EventType.PMI
        assert metadata.weight == 7  # From exact match

        # "Spanish Manufacturing PMI" uses pattern match
        metadata = get_event_metadata("Spanish Manufacturing PMI")
        assert metadata.event_type == EventType.PMI
        assert metadata.weight == 6  # From pattern (generic PMI)
