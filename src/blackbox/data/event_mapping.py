"""Event metadata mapping for economic events.

This module provides categorization and weighting metadata for economic events
to support fundamental scoring calculations.
"""

from dataclasses import dataclass

from blackbox.data.models import EventType


@dataclass(frozen=True)
class EventMetadata:
    """Metadata for an economic event.

    Attributes:
        event_type: Category of the event.
        direction: Impact direction (+1 = higher is bullish, -1 = higher is bearish).
        weight: Importance weight from 1 (low) to 10 (high).
    """

    event_type: EventType
    direction: int  # +1 or -1
    weight: int  # 1 to 10


# Mapping of event names to their metadata
# Keys are lowercase, trimmed event names for matching
EVENT_MAPPING: dict[str, EventMetadata] = {
    # Employment - High Impact
    "non-farm employment change": EventMetadata(EventType.EMPLOYMENT, +1, 10),
    "nonfarm payrolls": EventMetadata(EventType.EMPLOYMENT, +1, 10),
    "unemployment rate": EventMetadata(EventType.EMPLOYMENT, -1, 10),
    "unemployment claims": EventMetadata(EventType.EMPLOYMENT, -1, 8),
    "initial jobless claims": EventMetadata(EventType.EMPLOYMENT, -1, 8),
    "continuing jobless claims": EventMetadata(EventType.EMPLOYMENT, -1, 6),
    "adp non-farm employment change": EventMetadata(EventType.EMPLOYMENT, +1, 7),
    "adp nonfarm employment change": EventMetadata(EventType.EMPLOYMENT, +1, 7),
    "average hourly earnings m/m": EventMetadata(EventType.EMPLOYMENT, +1, 7),
    "average hourly earnings y/y": EventMetadata(EventType.EMPLOYMENT, +1, 7),
    "employment change": EventMetadata(EventType.EMPLOYMENT, +1, 8),
    "claimant count change": EventMetadata(EventType.EMPLOYMENT, -1, 7),
    # Inflation - High Impact
    "cpi m/m": EventMetadata(EventType.INFLATION, +1, 10),
    "cpi y/y": EventMetadata(EventType.INFLATION, +1, 10),
    "core cpi m/m": EventMetadata(EventType.INFLATION, +1, 10),
    "core cpi y/y": EventMetadata(EventType.INFLATION, +1, 10),
    "ppi m/m": EventMetadata(EventType.INFLATION, +1, 8),
    "ppi y/y": EventMetadata(EventType.INFLATION, +1, 8),
    "core ppi m/m": EventMetadata(EventType.INFLATION, +1, 8),
    "core ppi y/y": EventMetadata(EventType.INFLATION, +1, 8),
    "pce price index m/m": EventMetadata(EventType.INFLATION, +1, 9),
    "pce price index y/y": EventMetadata(EventType.INFLATION, +1, 9),
    "core pce price index m/m": EventMetadata(EventType.INFLATION, +1, 10),
    "core pce price index y/y": EventMetadata(EventType.INFLATION, +1, 10),
    "hicp y/y": EventMetadata(EventType.INFLATION, +1, 9),
    "hicp m/m": EventMetadata(EventType.INFLATION, +1, 9),
    # Growth - High Impact
    "gdp q/q": EventMetadata(EventType.GROWTH, +1, 9),
    "gdp y/y": EventMetadata(EventType.GROWTH, +1, 9),
    "advance gdp q/q": EventMetadata(EventType.GROWTH, +1, 10),
    "preliminary gdp q/q": EventMetadata(EventType.GROWTH, +1, 9),
    "final gdp q/q": EventMetadata(EventType.GROWTH, +1, 8),
    "gdp growth rate q/q": EventMetadata(EventType.GROWTH, +1, 9),
    "retail sales m/m": EventMetadata(EventType.GROWTH, +1, 8),
    "core retail sales m/m": EventMetadata(EventType.GROWTH, +1, 8),
    "industrial production m/m": EventMetadata(EventType.GROWTH, +1, 6),
    "industrial production y/y": EventMetadata(EventType.GROWTH, +1, 6),
    # Interest Rates - High Impact
    "federal funds rate": EventMetadata(EventType.INTEREST_RATE, +1, 10),
    "interest rate decision": EventMetadata(EventType.INTEREST_RATE, +1, 10),
    "official bank rate": EventMetadata(EventType.INTEREST_RATE, +1, 10),
    "main refinancing rate": EventMetadata(EventType.INTEREST_RATE, +1, 10),
    "deposit facility rate": EventMetadata(EventType.INTEREST_RATE, +1, 10),
    "overnight rate": EventMetadata(EventType.INTEREST_RATE, +1, 10),
    "cash rate": EventMetadata(EventType.INTEREST_RATE, +1, 10),
    "policy rate": EventMetadata(EventType.INTEREST_RATE, +1, 10),
    "fomc statement": EventMetadata(EventType.INTEREST_RATE, +1, 10),
    "fomc meeting minutes": EventMetadata(EventType.INTEREST_RATE, +1, 8),
    "fomc press conference": EventMetadata(EventType.INTEREST_RATE, +1, 9),
    "ecb press conference": EventMetadata(EventType.INTEREST_RATE, +1, 9),
    "boe monetary policy summary": EventMetadata(EventType.INTEREST_RATE, +1, 9),
    # PMI - Medium to High Impact
    "manufacturing pmi": EventMetadata(EventType.PMI, +1, 7),
    "services pmi": EventMetadata(EventType.PMI, +1, 7),
    "composite pmi": EventMetadata(EventType.PMI, +1, 7),
    "flash manufacturing pmi": EventMetadata(EventType.PMI, +1, 8),
    "flash services pmi": EventMetadata(EventType.PMI, +1, 8),
    "ism manufacturing pmi": EventMetadata(EventType.PMI, +1, 8),
    "ism non-manufacturing pmi": EventMetadata(EventType.PMI, +1, 8),
    "ism services pmi": EventMetadata(EventType.PMI, +1, 8),
    "chicago pmi": EventMetadata(EventType.PMI, +1, 5),
    "empire state manufacturing index": EventMetadata(EventType.PMI, +1, 5),
    "philly fed manufacturing index": EventMetadata(EventType.PMI, +1, 5),
    # Housing - Low to Medium Impact
    "building permits": EventMetadata(EventType.HOUSING, +1, 4),
    "housing starts": EventMetadata(EventType.HOUSING, +1, 4),
    "existing home sales": EventMetadata(EventType.HOUSING, +1, 4),
    "new home sales": EventMetadata(EventType.HOUSING, +1, 4),
    "pending home sales m/m": EventMetadata(EventType.HOUSING, +1, 3),
    "house price index m/m": EventMetadata(EventType.HOUSING, +1, 3),
    "s&p/cs composite-20 hpi y/y": EventMetadata(EventType.HOUSING, +1, 3),
    "construction spending m/m": EventMetadata(EventType.HOUSING, +1, 3),
    "nationwide hpi m/m": EventMetadata(EventType.HOUSING, +1, 3),
    # Sentiment - Low to Medium Impact
    "consumer confidence": EventMetadata(EventType.SENTIMENT, +1, 5),
    "cb consumer confidence": EventMetadata(EventType.SENTIMENT, +1, 6),
    "michigan consumer sentiment": EventMetadata(EventType.SENTIMENT, +1, 5),
    "university of michigan consumer sentiment": EventMetadata(
        EventType.SENTIMENT, +1, 5
    ),
    "zew economic sentiment": EventMetadata(EventType.SENTIMENT, +1, 5),
    "ifo business climate": EventMetadata(EventType.SENTIMENT, +1, 5),
    "gfk consumer climate": EventMetadata(EventType.SENTIMENT, +1, 4),
    "consumer confidence index": EventMetadata(EventType.SENTIMENT, +1, 5),
    "business confidence": EventMetadata(EventType.SENTIMENT, +1, 4),
    # Trade - Low to Medium Impact
    "trade balance": EventMetadata(EventType.TRADE, +1, 4),
    "current account": EventMetadata(EventType.TRADE, +1, 4),
    "current account q/q": EventMetadata(EventType.TRADE, +1, 4),
    "goods trade balance": EventMetadata(EventType.TRADE, +1, 3),
    "import prices m/m": EventMetadata(EventType.TRADE, -1, 3),
    "export prices m/m": EventMetadata(EventType.TRADE, +1, 3),
}


def _normalize_event_name(event_name: str) -> str:
    """Normalize event name for matching.

    Args:
        event_name: Raw event name from scraper.

    Returns:
        Normalized name (lowercase, trimmed).
    """
    return event_name.strip().lower()


def get_event_metadata(event_name: str) -> EventMetadata:
    """Get metadata for an economic event.

    Looks up the event in the mapping table. If not found, returns
    default metadata (OTHER type, direction +1, weight 1).

    Args:
        event_name: The name of the economic event.

    Returns:
        EventMetadata with type, direction, and weight.
    """
    normalized = _normalize_event_name(event_name)
    return EVENT_MAPPING.get(
        normalized,
        EventMetadata(EventType.OTHER, +1, 1),
    )
