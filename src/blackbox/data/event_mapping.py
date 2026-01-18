"""Event metadata mapping for economic events.

This module provides categorization and weighting metadata for economic events
to support fundamental scoring calculations.

The mapping system uses two strategies:
1. Exact match: For specific event names with known metadata
2. Pattern match: Regex patterns for generic categorization (fallback)
"""

import re
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


@dataclass(frozen=True)
class EventPattern:
    """Pattern-based event matcher.

    Attributes:
        pattern: Compiled regex pattern.
        metadata: Metadata to apply when pattern matches.
        priority: Higher priority patterns are checked first (default: 0).
    """

    pattern: re.Pattern[str]
    metadata: EventMetadata
    priority: int = 0


# Regex patterns for event categorization, ordered by priority
# Higher priority = more specific patterns checked first
EVENT_PATTERNS: list[EventPattern] = [
    # === INTEREST RATE (priority 100) - Most important ===
    EventPattern(
        re.compile(r"\b(federal funds rate|interest rate decision)\b", re.IGNORECASE),
        EventMetadata(EventType.INTEREST_RATE, +1, 10),
        priority=100,
    ),
    EventPattern(
        re.compile(r"\b(official bank rate|main refinancing rate)\b", re.IGNORECASE),
        EventMetadata(EventType.INTEREST_RATE, +1, 10),
        priority=100,
    ),
    EventPattern(
        re.compile(r"\bfomc\s+(statement|press conference)\b", re.IGNORECASE),
        EventMetadata(EventType.INTEREST_RATE, +1, 10),
        priority=100,
    ),
    EventPattern(
        re.compile(r"\bfomc\s+meeting\s+minutes\b", re.IGNORECASE),
        EventMetadata(EventType.INTEREST_RATE, +1, 8),
        priority=100,
    ),
    EventPattern(
        re.compile(r"\becb\s+press\s+conference\b", re.IGNORECASE),
        EventMetadata(EventType.INTEREST_RATE, +1, 9),
        priority=100,
    ),
    # === EMPLOYMENT (priority 90) ===
    EventPattern(
        re.compile(r"\bnon-?farm\s+(employment|payroll)", re.IGNORECASE),
        EventMetadata(EventType.EMPLOYMENT, +1, 10),
        priority=90,
    ),
    EventPattern(
        re.compile(r"\bunemployment\s+rate\b", re.IGNORECASE),
        EventMetadata(EventType.EMPLOYMENT, -1, 10),
        priority=90,
    ),
    EventPattern(
        re.compile(r"\bunemployment\s+(claims|change)\b", re.IGNORECASE),
        EventMetadata(EventType.EMPLOYMENT, -1, 8),
        priority=90,
    ),
    EventPattern(
        re.compile(r"\b(initial|continuing)\s+jobless\s+claims\b", re.IGNORECASE),
        EventMetadata(EventType.EMPLOYMENT, -1, 8),
        priority=90,
    ),
    EventPattern(
        re.compile(r"\badp\s+.*employment", re.IGNORECASE),
        EventMetadata(EventType.EMPLOYMENT, +1, 7),
        priority=90,
    ),
    EventPattern(
        re.compile(r"\baverage\s+hourly\s+earnings\b", re.IGNORECASE),
        EventMetadata(EventType.EMPLOYMENT, +1, 7),
        priority=90,
    ),
    EventPattern(
        re.compile(r"\bemployment\s+change\b", re.IGNORECASE),
        EventMetadata(EventType.EMPLOYMENT, +1, 8),
        priority=90,
    ),
    EventPattern(
        re.compile(r"\bclaimant\s+count\b", re.IGNORECASE),
        EventMetadata(EventType.EMPLOYMENT, -1, 7),
        priority=90,
    ),
    EventPattern(
        re.compile(r"\bjob\s+(openings|cuts)\b", re.IGNORECASE),
        EventMetadata(EventType.EMPLOYMENT, +1, 6),
        priority=90,
    ),
    EventPattern(
        re.compile(r"\bjolts\b", re.IGNORECASE),
        EventMetadata(EventType.EMPLOYMENT, +1, 7),
        priority=90,
    ),
    # === INFLATION (priority 85) ===
    EventPattern(
        re.compile(r"\bcore\s+pce\b", re.IGNORECASE),
        EventMetadata(EventType.INFLATION, +1, 10),
        priority=85,
    ),
    EventPattern(
        re.compile(r"\bpce\s+price\s+index\b", re.IGNORECASE),
        EventMetadata(EventType.INFLATION, +1, 9),
        priority=85,
    ),
    EventPattern(
        re.compile(r"\bcore\s+cpi\b", re.IGNORECASE),
        EventMetadata(EventType.INFLATION, +1, 10),
        priority=85,
    ),
    EventPattern(
        re.compile(r"\bcpi\b", re.IGNORECASE),
        EventMetadata(EventType.INFLATION, +1, 9),
        priority=85,
    ),
    EventPattern(
        re.compile(r"\bcore\s+ppi\b", re.IGNORECASE),
        EventMetadata(EventType.INFLATION, +1, 8),
        priority=85,
    ),
    EventPattern(
        re.compile(r"\bppi\b", re.IGNORECASE),
        EventMetadata(EventType.INFLATION, +1, 7),
        priority=85,
    ),
    EventPattern(
        re.compile(r"\bhicp\b", re.IGNORECASE),
        EventMetadata(EventType.INFLATION, +1, 9),
        priority=85,
    ),
    EventPattern(
        re.compile(r"\binflation\s+expectations?\b", re.IGNORECASE),
        EventMetadata(EventType.INFLATION, +1, 5),
        priority=85,
    ),
    # === GROWTH (priority 80) ===
    EventPattern(
        re.compile(r"\b(advance|preliminary|prelim|final)?\s*gdp\b", re.IGNORECASE),
        EventMetadata(EventType.GROWTH, +1, 9),
        priority=80,
    ),
    EventPattern(
        re.compile(r"\bretail\s+sales\b", re.IGNORECASE),
        EventMetadata(EventType.GROWTH, +1, 7),
        priority=80,
    ),
    EventPattern(
        re.compile(r"\bindustrial\s+production\b", re.IGNORECASE),
        EventMetadata(EventType.GROWTH, +1, 6),
        priority=80,
    ),
    EventPattern(
        re.compile(r"\bfactory\s+orders\b", re.IGNORECASE),
        EventMetadata(EventType.GROWTH, +1, 5),
        priority=80,
    ),
    EventPattern(
        re.compile(r"\bmanufacturing\s+(production|sales)\b", re.IGNORECASE),
        EventMetadata(EventType.GROWTH, +1, 5),
        priority=80,
    ),
    EventPattern(
        re.compile(r"\bwholesale\s+sales\b", re.IGNORECASE),
        EventMetadata(EventType.GROWTH, +1, 4),
        priority=80,
    ),
    # === PMI (priority 75) ===
    EventPattern(
        re.compile(r"\bism\s+.*pmi\b", re.IGNORECASE),
        EventMetadata(EventType.PMI, +1, 8),
        priority=75,
    ),
    EventPattern(
        re.compile(r"\bflash\s+.*pmi\b", re.IGNORECASE),
        EventMetadata(EventType.PMI, +1, 8),
        priority=75,
    ),
    EventPattern(
        re.compile(r"\bpmi\b", re.IGNORECASE),
        EventMetadata(EventType.PMI, +1, 6),
        priority=75,
    ),
    EventPattern(
        re.compile(
            r"\b(empire\s+state|philly\s+fed)\s+manufacturing\s+index\b", re.IGNORECASE
        ),
        EventMetadata(EventType.PMI, +1, 5),
        priority=75,
    ),
    EventPattern(
        re.compile(r"\bmanufacturing\s+index\b", re.IGNORECASE),
        EventMetadata(EventType.PMI, +1, 5),
        priority=75,
    ),
    # === HOUSING (priority 70) ===
    EventPattern(
        re.compile(r"\bbuilding\s+(permits?|approvals?|consents?)\b", re.IGNORECASE),
        EventMetadata(EventType.HOUSING, +1, 4),
        priority=70,
    ),
    EventPattern(
        re.compile(r"\bhousing\s+starts\b", re.IGNORECASE),
        EventMetadata(EventType.HOUSING, +1, 4),
        priority=70,
    ),
    EventPattern(
        re.compile(r"\b(existing|new|pending)\s+home\s+sales\b", re.IGNORECASE),
        EventMetadata(EventType.HOUSING, +1, 4),
        priority=70,
    ),
    EventPattern(
        re.compile(r"\bhpi\b", re.IGNORECASE),
        EventMetadata(EventType.HOUSING, +1, 3),
        priority=70,
    ),
    EventPattern(
        re.compile(r"\bhouse\s+price\b", re.IGNORECASE),
        EventMetadata(EventType.HOUSING, +1, 3),
        priority=70,
    ),
    EventPattern(
        re.compile(r"\bconstruction\s+(spending|output)\b", re.IGNORECASE),
        EventMetadata(EventType.HOUSING, +1, 3),
        priority=70,
    ),
    EventPattern(
        re.compile(r"\bmortgage\s+approvals?\b", re.IGNORECASE),
        EventMetadata(EventType.HOUSING, +1, 3),
        priority=70,
    ),
    # === SENTIMENT (priority 65) ===
    EventPattern(
        re.compile(r"\bconsumer\s+(confidence|sentiment)\b", re.IGNORECASE),
        EventMetadata(EventType.SENTIMENT, +1, 5),
        priority=65,
    ),
    EventPattern(
        re.compile(r"\bbusiness\s+(confidence|sentiment|climate)\b", re.IGNORECASE),
        EventMetadata(EventType.SENTIMENT, +1, 4),
        priority=65,
    ),
    EventPattern(
        re.compile(r"\binvestor\s+(confidence|sentiment)\b", re.IGNORECASE),
        EventMetadata(EventType.SENTIMENT, +1, 4),
        priority=65,
    ),
    EventPattern(
        re.compile(r"\bzew\s+economic\s+sentiment\b", re.IGNORECASE),
        EventMetadata(EventType.SENTIMENT, +1, 5),
        priority=65,
    ),
    EventPattern(
        re.compile(r"\bifo\s+business\s+climate\b", re.IGNORECASE),
        EventMetadata(EventType.SENTIMENT, +1, 5),
        priority=65,
    ),
    EventPattern(
        re.compile(r"\bgfk\s+consumer\s+climate\b", re.IGNORECASE),
        EventMetadata(EventType.SENTIMENT, +1, 4),
        priority=65,
    ),
    EventPattern(
        re.compile(r"\beconomic\s+optimism\b", re.IGNORECASE),
        EventMetadata(EventType.SENTIMENT, +1, 4),
        priority=65,
    ),
    EventPattern(
        re.compile(r"\bsentiment\b", re.IGNORECASE),
        EventMetadata(EventType.SENTIMENT, +1, 4),
        priority=65,
    ),
    # === TRADE (priority 60) ===
    EventPattern(
        re.compile(r"\btrade\s+balance\b", re.IGNORECASE),
        EventMetadata(EventType.TRADE, +1, 4),
        priority=60,
    ),
    EventPattern(
        re.compile(r"\bcurrent\s+account\b", re.IGNORECASE),
        EventMetadata(EventType.TRADE, +1, 4),
        priority=60,
    ),
    EventPattern(
        re.compile(r"\bgoods\s+trade\s+balance\b", re.IGNORECASE),
        EventMetadata(EventType.TRADE, +1, 3),
        priority=60,
    ),
    EventPattern(
        re.compile(r"\b(import|export)\s+prices?\b", re.IGNORECASE),
        EventMetadata(EventType.TRADE, +1, 3),
        priority=60,
    ),
    # === OTHER (priority 10) - Low priority catchalls ===
    EventPattern(
        re.compile(r"\bbank\s+holiday\b", re.IGNORECASE),
        EventMetadata(EventType.OTHER, +1, 1),
        priority=10,
    ),
    EventPattern(
        re.compile(r"\b(fomc|mpc|ecb)\s+member\s+.*speaks\b", re.IGNORECASE),
        EventMetadata(EventType.OTHER, +1, 3),
        priority=10,
    ),
    EventPattern(
        re.compile(r"\bpresident\s+.*speaks\b", re.IGNORECASE),
        EventMetadata(EventType.OTHER, +1, 4),
        priority=10,
    ),
    EventPattern(
        re.compile(r"\bbond\s+auction\b", re.IGNORECASE),
        EventMetadata(EventType.OTHER, +1, 2),
        priority=10,
    ),
]

# Sort patterns by priority (highest first)
EVENT_PATTERNS.sort(key=lambda p: p.priority, reverse=True)


# Exact match mapping for specific events with known metadata
# Keys are lowercase, trimmed event names
EXACT_EVENT_MAPPING: dict[str, EventMetadata] = {
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


def _match_pattern(event_name: str) -> EventMetadata | None:
    """Try to match event name against regex patterns.

    Args:
        event_name: The event name to match.

    Returns:
        EventMetadata if a pattern matches, None otherwise.
    """
    for event_pattern in EVENT_PATTERNS:
        if event_pattern.pattern.search(event_name):
            return event_pattern.metadata
    return None


def get_event_metadata(event_name: str) -> EventMetadata:
    """Get metadata for an economic event.

    Uses a two-tier matching strategy:
    1. First, tries exact match in EXACT_EVENT_MAPPING
    2. If not found, tries regex pattern matching in EVENT_PATTERNS
    3. If still not found, returns default metadata

    Args:
        event_name: The name of the economic event.

    Returns:
        EventMetadata with type, direction, and weight.
    """
    normalized = _normalize_event_name(event_name)

    # Try exact match first
    if normalized in EXACT_EVENT_MAPPING:
        return EXACT_EVENT_MAPPING[normalized]

    # Try pattern matching
    pattern_match = _match_pattern(event_name)
    if pattern_match is not None:
        return pattern_match

    # Default fallback
    return EventMetadata(EventType.OTHER, +1, 1)
