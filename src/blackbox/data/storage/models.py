"""SQLAlchemy models for economic calendar persistence.

This module defines the database schema for storing economic events.
"""

from datetime import date, datetime, time

from sqlalchemy import (
    Date,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class EconomicEventDB(Base):
    """Database model for economic events.

    Attributes:
        id: Primary key.
        date: The date of the event.
        time: The time of the event (nullable for all-day events).
        currency: The currency affected (e.g., USD, EUR).
        impact: Impact level (low, medium, high, holiday, unknown).
        event_name: The name/title of the event.
        actual: The actual reported value.
        forecast: The forecasted value.
        previous: The previous period's value.
        event_type: Category of the event for fundamental scoring.
        direction: Impact direction (+1 = higher is bullish, -1 = higher is bearish).
        weight: Importance weight from 1 (low) to 10 (high).
        surprise: Normalized surprise score (actual vs forecast deviation).
        scraped_at: Timestamp when the event was first scraped.
        updated_at: Timestamp when the event was last updated.
    """

    __tablename__ = "economic_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    time: Mapped[time | None] = mapped_column(Time, nullable=True)
    currency: Mapped[str] = mapped_column(String(5), nullable=False, index=True)
    impact: Mapped[str] = mapped_column(String(10), nullable=False)
    event_name: Mapped[str] = mapped_column(String(255), nullable=False)
    actual: Mapped[float | None] = mapped_column(Float, nullable=True)
    forecast: Mapped[float | None] = mapped_column(Float, nullable=True)
    previous: Mapped[float | None] = mapped_column(Float, nullable=True)
    event_type: Mapped[str] = mapped_column(String(20), nullable=False, default="other")
    direction: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    weight: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    surprise: Mapped[float | None] = mapped_column(Float, nullable=True)
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("date", "time", "currency", "event_name", name="uq_event"),
        Index("idx_needs_update", "date", "actual"),
    )

    def __repr__(self) -> str:
        return f"<EconomicEventDB(date={self.date}, currency={self.currency}, event_name={self.event_name})>"
