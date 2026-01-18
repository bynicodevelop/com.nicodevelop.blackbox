"""FastAPI application for Blackbox Trading Robot.

This module defines the REST API endpoints for the trading robot.
"""

from datetime import date
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from blackbox import __version__
from blackbox.data.config import ForexFactoryConfig
from blackbox.data.exceptions import ScraperError
from blackbox.data.models import Impact
from blackbox.data.scraper.forex_factory import ForexFactoryScraper

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
    time: Optional[str]
    currency: str
    impact: str
    event_name: str
    actual: Optional[str]
    forecast: Optional[str]
    previous: Optional[str]


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
    currencies: Optional[str] = Query(None, description="Comma-separated currency codes (e.g., USD,EUR)"),
    high_impact_only: bool = Query(False, description="Only return high impact events"),
) -> CalendarMonthResponse:
    """Fetch the economic calendar for a specific month.

    Args:
        year: The year to fetch.
        month: The month to fetch (1-12).
        currencies: Optional comma-separated list of currencies to filter by.
        high_impact_only: If true, only return high impact events.

    Returns:
        CalendarMonthResponse with all matching events.
    """
    currency_list = [c.strip().upper() for c in currencies.split(",")] if currencies else None

    try:
        config = ForexFactoryConfig()
        with ForexFactoryScraper(config) as scraper:
            calendar_month = scraper.fetch_month(year, month, currency_list)

            events = calendar_month.all_events
            if high_impact_only:
                events = [e for e in events if e.impact == Impact.HIGH]

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
        raise HTTPException(status_code=503, detail=f"Failed to fetch calendar: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/api/v1/calendar/today", response_model=CalendarTodayResponse)
async def get_calendar_today(
    currencies: Optional[str] = Query(None, description="Comma-separated currency codes"),
    high_impact_only: bool = Query(False, description="Only return high impact events"),
) -> CalendarTodayResponse:
    """Fetch today's economic calendar.

    Args:
        currencies: Optional comma-separated list of currencies to filter by.
        high_impact_only: If true, only return high impact events.

    Returns:
        CalendarTodayResponse with today's events.
    """
    currency_list = [c.strip().upper() for c in currencies.split(",")] if currencies else None

    try:
        config = ForexFactoryConfig()
        with ForexFactoryScraper(config) as scraper:
            events = scraper.fetch_today()

            # Filter by currencies
            if currency_list:
                events = [e for e in events if e.currency.upper() in currency_list]

            # Filter by impact
            if high_impact_only:
                events = [e for e in events if e.impact == Impact.HIGH]

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
        raise HTTPException(status_code=503, detail=f"Failed to fetch calendar: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# Background refresh state
_refresh_status = {"status": "idle", "message": "No refresh in progress"}


def _do_calendar_refresh(year: int, month: int) -> None:
    """Background task to refresh calendar data."""
    global _refresh_status
    _refresh_status = {"status": "running", "message": f"Refreshing {year}-{month:02d}"}

    try:
        config = ForexFactoryConfig()
        with ForexFactoryScraper(config) as scraper:
            scraper.fetch_month(year, month)
        _refresh_status = {"status": "completed", "message": f"Successfully refreshed {year}-{month:02d}"}
    except Exception as e:
        _refresh_status = {"status": "error", "message": str(e)}


@app.post("/api/v1/calendar/refresh", response_model=RefreshResponse)
async def refresh_calendar(
    background_tasks: BackgroundTasks,
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Year to refresh (default: current)"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Month to refresh (default: current)"),
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
