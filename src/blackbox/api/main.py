"""FastAPI application for Blackbox Trading Robot.

This module defines the REST API endpoints for the trading robot.
"""

from datetime import date, datetime

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from blackbox import __version__
from blackbox.core.scoring import ScoringConfig, ScoringService
from blackbox.data.exceptions import ScraperError
from blackbox.data.services import CalendarService
from blackbox.data.storage.database import get_session
from blackbox.data.storage.repository import EventRepository

app = FastAPI(
    title="Blackbox Trading Robot API",
    description="REST API for the Blackbox Trading Robot",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict:
    """Root endpoint returning API information."""
    return {
        "name": "Blackbox Trading Robot API",
        "version": __version__,
        "status": "running",
    }


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/v1/status")
async def get_status() -> dict:
    """Get the current status of the trading robot."""
    return {
        "status": "ready",
        "version": __version__,
        "trading": False,
        "active_strategies": [],
    }


@app.get("/api/v1/strategies")
async def list_strategies() -> dict:
    """List all available trading strategies."""
    # TODO: Implement strategy listing from core module
    return {
        "strategies": [],
        "message": "No strategies configured yet",
    }


@app.post("/api/v1/strategies/{strategy_name}/start")
async def start_strategy(strategy_name: str, dry_run: bool = True) -> dict:
    """Start a trading strategy.

    Args:
        strategy_name: Name of the strategy to start
        dry_run: If True, run in simulation mode
    """
    # TODO: Implement strategy start logic
    return {
        "message": f"Strategy '{strategy_name}' start requested",
        "dry_run": dry_run,
        "status": "not_implemented",
    }


@app.post("/api/v1/strategies/{strategy_name}/stop")
async def stop_strategy(strategy_name: str) -> dict:
    """Stop a running trading strategy.

    Args:
        strategy_name: Name of the strategy to stop
    """
    # TODO: Implement strategy stop logic
    return {
        "message": f"Strategy '{strategy_name}' stop requested",
        "status": "not_implemented",
    }


# Calendar API response models
class EventResponse(BaseModel):
    """API response model for a single economic event."""

    date: str
    time: str | None
    currency: str
    impact: str
    event_name: str
    actual: float | None
    forecast: float | None
    previous: float | None


class CalendarMonthResponse(BaseModel):
    """API response model for a month's calendar."""

    year: int
    month: int
    total_events: int
    events: list[EventResponse]


class CalendarTodayResponse(BaseModel):
    """API response model for today's calendar."""

    date: str
    total_events: int
    events: list[EventResponse]


class RefreshResponse(BaseModel):
    """API response model for calendar refresh."""

    status: str
    message: str


# Calendar endpoints
@app.get("/api/v1/calendar/month", response_model=CalendarMonthResponse)
async def get_calendar_month(
    year: int = Query(..., ge=2000, le=2100, description="Year to fetch"),
    month: int = Query(..., ge=1, le=12, description="Month to fetch (1-12)"),
    currencies: str | None = Query(
        None, description="Comma-separated currency codes (e.g., USD,EUR)"
    ),
    high_impact_only: bool = Query(False, description="Only return high impact events"),
    force_refresh: bool = Query(False, description="Force re-scraping even if cached"),
) -> CalendarMonthResponse:
    """Fetch the economic calendar for a specific month.

    Uses cached data from PostgreSQL when available.
    Use force_refresh=true to always scrape fresh data.

    Args:
        year: The year to fetch.
        month: The month to fetch (1-12).
        currencies: Optional comma-separated list of currencies to filter by.
        high_impact_only: If true, only return high impact events.
        force_refresh: If true, ignore cache and scrape fresh data.

    Returns:
        CalendarMonthResponse with all matching events.
    """
    currency_list = (
        [c.strip().upper() for c in currencies.split(",")] if currencies else None
    )
    impact = "high" if high_impact_only else None

    try:
        service = CalendarService()
        events = service.fetch_month(year, month, currency_list, impact, force_refresh)

        event_responses = [
            EventResponse(
                date=str(e.date),
                time=str(e.time) if e.time else None,
                currency=e.currency,
                impact=e.impact.value,
                event_name=e.event_name,
                actual=e.actual,
                forecast=e.forecast,
                previous=e.previous,
            )
            for e in events
        ]

        return CalendarMonthResponse(
            year=year,
            month=month,
            total_events=len(event_responses),
            events=event_responses,
        )

    except ScraperError as e:
        raise HTTPException(
            status_code=503, detail=f"Failed to fetch calendar: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/api/v1/calendar/today", response_model=CalendarTodayResponse)
async def get_calendar_today(
    currencies: str | None = Query(None, description="Comma-separated currency codes"),
    high_impact_only: bool = Query(False, description="Only return high impact events"),
) -> CalendarTodayResponse:
    """Fetch today's economic calendar.

    Uses cached data from PostgreSQL when available.

    Args:
        currencies: Optional comma-separated list of currencies to filter by.
        high_impact_only: If true, only return high impact events.

    Returns:
        CalendarTodayResponse with today's events.
    """
    currency_list = (
        [c.strip().upper() for c in currencies.split(",")] if currencies else None
    )

    try:
        service = CalendarService()
        events = service.fetch_today(currency_list, high_impact_only)

        event_responses = [
            EventResponse(
                date=str(e.date),
                time=str(e.time) if e.time else None,
                currency=e.currency,
                impact=e.impact.value,
                event_name=e.event_name,
                actual=e.actual,
                forecast=e.forecast,
                previous=e.previous,
            )
            for e in events
        ]

        return CalendarTodayResponse(
            date=str(date.today()),
            total_events=len(event_responses),
            events=event_responses,
        )

    except ScraperError as e:
        raise HTTPException(
            status_code=503, detail=f"Failed to fetch calendar: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# Background refresh state
_refresh_status = {"status": "idle", "message": "No refresh in progress"}


def _do_calendar_refresh(year: int, month: int) -> None:
    """Background task to refresh calendar data."""
    global _refresh_status
    _refresh_status = {"status": "running", "message": f"Refreshing {year}-{month:02d}"}

    try:
        service = CalendarService()
        count = service.refresh_month(year, month)
        _refresh_status = {
            "status": "completed",
            "message": f"Successfully refreshed {year}-{month:02d}: {count} events",
        }
    except Exception as e:
        _refresh_status = {"status": "error", "message": str(e)}


@app.post("/api/v1/calendar/refresh", response_model=RefreshResponse)
async def refresh_calendar(
    background_tasks: BackgroundTasks,
    year: int | None = Query(
        None, ge=2000, le=2100, description="Year to refresh (default: current)"
    ),
    month: int | None = Query(
        None, ge=1, le=12, description="Month to refresh (default: current)"
    ),
) -> RefreshResponse:
    """Trigger a background refresh of the calendar data.

    Args:
        year: The year to refresh (defaults to current year).
        month: The month to refresh (defaults to current month).

    Returns:
        RefreshResponse indicating the refresh has started.
    """
    today = date.today()
    year = year or today.year
    month = month or today.month

    background_tasks.add_task(_do_calendar_refresh, year, month)

    return RefreshResponse(
        status="started",
        message=f"Calendar refresh started for {year}-{month:02d}",
    )


@app.get("/api/v1/calendar/refresh/status", response_model=RefreshResponse)
async def get_refresh_status() -> RefreshResponse:
    """Get the status of the last calendar refresh operation.

    Returns:
        RefreshResponse with the current refresh status.
    """
    return RefreshResponse(**_refresh_status)


class StatsResponse(BaseModel):
    """API response model for database statistics."""

    total_events: int
    by_currency: dict[str, int]
    by_impact: dict[str, int]
    date_range_start: str | None
    date_range_end: str | None


@app.get("/api/v1/calendar/stats", response_model=StatsResponse)
async def get_calendar_stats() -> StatsResponse:
    """Get statistics about stored calendar events.

    Returns:
        StatsResponse with counts and date range information.
    """
    try:
        service = CalendarService()
        stats = service.get_stats()

        return StatsResponse(
            total_events=stats["total_events"],
            by_currency=stats["by_currency"],
            by_impact=stats["by_impact"],
            date_range_start=str(stats["date_range"][0])
            if stats["date_range"][0]
            else None,
            date_range_end=str(stats["date_range"][1])
            if stats["date_range"][1]
            else None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# Scoring API response models
class CurrencyScoreResponse(BaseModel):
    """API response model for currency score."""

    currency: str
    score: float
    reference_time: str
    config: dict


class PairBiasResponse(BaseModel):
    """API response model for pair bias."""

    base: str
    quote: str
    pair: str
    base_score: float
    quote_score: float
    bias: float
    reference_time: str


class PairSignalResponse(BaseModel):
    """API response model for pair signal."""

    base: str
    quote: str
    pair: str
    bias: float
    signal: str
    threshold: float
    reference_time: str


@app.get("/api/v1/scoring/currency/{currency}", response_model=CurrencyScoreResponse)
async def get_currency_score(
    currency: str,
    half_life_hours: float = Query(
        48.0, gt=0, description="Half-life for decay in hours"
    ),
    lookback_days: int = Query(7, gt=0, description="Days to look back for events"),
) -> CurrencyScoreResponse:
    """Get the fundamental score for a currency.

    The score is calculated from economic events with temporal decay.
    Positive scores indicate bullish sentiment, negative indicates bearish.

    Args:
        currency: Currency code (e.g., USD, EUR, GBP).
        half_life_hours: Half-life for temporal decay.
        lookback_days: Number of days to include in analysis.

    Returns:
        CurrencyScoreResponse with the calculated score.
    """
    try:
        config = ScoringConfig(
            half_life_hours=half_life_hours,
            lookback_days=lookback_days,
        )
        reference_time = datetime.now()

        with get_session() as session:
            repository = EventRepository(session)
            service = ScoringService(config, repository)
            score = service.get_currency_score(currency.upper(), reference_time)

        return CurrencyScoreResponse(
            currency=currency.upper(),
            score=round(score, 4),
            reference_time=reference_time.isoformat(),
            config={
                "half_life_hours": half_life_hours,
                "lookback_days": lookback_days,
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/api/v1/scoring/pair/{base}/{quote}", response_model=PairBiasResponse)
async def get_pair_bias(
    base: str,
    quote: str,
    half_life_hours: float = Query(
        48.0, gt=0, description="Half-life for decay in hours"
    ),
    lookback_days: int = Query(7, gt=0, description="Days to look back for events"),
) -> PairBiasResponse:
    """Get the directional bias for a currency pair.

    Bias = base_currency_score - quote_currency_score.
    Positive bias indicates bullish sentiment for the pair.

    Args:
        base: Base currency code (e.g., EUR in EURUSD).
        quote: Quote currency code (e.g., USD in EURUSD).
        half_life_hours: Half-life for temporal decay.
        lookback_days: Number of days to include in analysis.

    Returns:
        PairBiasResponse with scores and bias.
    """
    try:
        config = ScoringConfig(
            half_life_hours=half_life_hours,
            lookback_days=lookback_days,
        )
        reference_time = datetime.now()
        base_upper = base.upper()
        quote_upper = quote.upper()

        with get_session() as session:
            repository = EventRepository(session)
            service = ScoringService(config, repository)
            base_score = service.get_currency_score(base_upper, reference_time)
            quote_score = service.get_currency_score(quote_upper, reference_time)
            bias = service.get_pair_bias(base_upper, quote_upper, reference_time)

        return PairBiasResponse(
            base=base_upper,
            quote=quote_upper,
            pair=f"{base_upper}{quote_upper}",
            base_score=round(base_score, 4),
            quote_score=round(quote_score, 4),
            bias=round(bias, 4),
            reference_time=reference_time.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/api/v1/scoring/signal/{base}/{quote}", response_model=PairSignalResponse)
async def get_pair_signal(
    base: str,
    quote: str,
    half_life_hours: float = Query(
        48.0, gt=0, description="Half-life for decay in hours"
    ),
    lookback_days: int = Query(7, gt=0, description="Days to look back for events"),
    min_bias_threshold: float = Query(
        1.0, ge=0, description="Minimum bias for directional signal"
    ),
) -> PairSignalResponse:
    """Get a trading signal for a currency pair.

    Returns BULLISH if bias > threshold, BEARISH if bias < -threshold,
    otherwise NEUTRAL.

    Args:
        base: Base currency code (e.g., EUR in EURUSD).
        quote: Quote currency code (e.g., USD in EURUSD).
        half_life_hours: Half-life for temporal decay.
        lookback_days: Number of days to include in analysis.
        min_bias_threshold: Minimum absolute bias for directional signal.

    Returns:
        PairSignalResponse with signal and bias.
    """
    try:
        config = ScoringConfig(
            half_life_hours=half_life_hours,
            lookback_days=lookback_days,
            min_bias_threshold=min_bias_threshold,
        )
        reference_time = datetime.now()
        base_upper = base.upper()
        quote_upper = quote.upper()

        with get_session() as session:
            repository = EventRepository(session)
            service = ScoringService(config, repository)
            bias = service.get_pair_bias(base_upper, quote_upper, reference_time)
            signal = service.get_bias_signal(base_upper, quote_upper, reference_time)

        return PairSignalResponse(
            base=base_upper,
            quote=quote_upper,
            pair=f"{base_upper}{quote_upper}",
            bias=round(bias, 4),
            signal=signal,
            threshold=min_bias_threshold,
            reference_time=reference_time.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
