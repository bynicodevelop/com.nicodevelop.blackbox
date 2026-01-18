"""Repository pattern for economic events persistence.

This module provides a clean interface for CRUD operations
on economic events in the database.
"""

from collections.abc import Sequence
from datetime import date

from sqlalchemy import and_, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from blackbox.data.models import EconomicEvent, EventType, Impact
from blackbox.data.storage.models import EconomicEventDB


class EventRepository:
    """Repository for managing economic events in the database.

    Provides methods for querying, inserting, and updating events.
    """

    def __init__(self, session: Session):
        """Initialize the repository with a database session.

        Args:
            session: SQLAlchemy session instance.
        """
        self.session = session

    def get_events_needing_update(self, start_date: date, end_date: date) -> list[date]:
        """Get dates with events that need their actual values updated.

        Returns dates where events have actual IS NULL and date >= today.

        Args:
            start_date: Start of the date range.
            end_date: End of the date range.

        Returns:
            List of dates that need updating.
        """
        today = date.today()
        stmt = (
            select(EconomicEventDB.date)
            .where(
                and_(
                    EconomicEventDB.date >= start_date,
                    EconomicEventDB.date <= end_date,
                    EconomicEventDB.date >= today,
                    EconomicEventDB.actual.is_(None),
                )
            )
            .distinct()
            .order_by(EconomicEventDB.date)
        )
        result = self.session.execute(stmt)
        return [row[0] for row in result]

    def upsert_events(self, events: list[EconomicEvent]) -> int:
        """Insert or update events (ON CONFLICT).

        Args:
            events: List of EconomicEvent pydantic models to upsert.

        Returns:
            Number of affected rows.
        """
        if not events:
            return 0

        values = [
            {
                "date": e.date,
                "time": e.time,
                "currency": e.currency,
                "impact": e.impact.value,
                "event_name": e.event_name,
                "actual": e.actual,
                "forecast": e.forecast,
                "previous": e.previous,
                "event_type": e.event_type.value,
                "direction": e.direction,
                "weight": e.weight,
            }
            for e in events
        ]

        stmt = insert(EconomicEventDB).values(values)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_event",
            set_={
                "actual": stmt.excluded.actual,
                "forecast": stmt.excluded.forecast,
                "previous": stmt.excluded.previous,
                "impact": stmt.excluded.impact,
                "event_type": stmt.excluded.event_type,
                "direction": stmt.excluded.direction,
                "weight": stmt.excluded.weight,
                "updated_at": func.now(),
            },
        )

        result = self.session.execute(stmt)
        return result.rowcount

    def get_events(
        self,
        start_date: date,
        end_date: date,
        currencies: list[str] | None = None,
        impact: str | None = None,
    ) -> list[EconomicEvent]:
        """Retrieve events with optional filters.

        Args:
            start_date: Start of the date range (inclusive).
            end_date: End of the date range (inclusive).
            currencies: Optional list of currency codes to filter by.
            impact: Optional minimum impact level to filter by.

        Returns:
            List of EconomicEvent pydantic models.
        """
        stmt = select(EconomicEventDB).where(
            and_(
                EconomicEventDB.date >= start_date,
                EconomicEventDB.date <= end_date,
            )
        )

        if currencies:
            currencies_upper = [c.upper() for c in currencies]
            stmt = stmt.where(EconomicEventDB.currency.in_(currencies_upper))

        if impact:
            impact_order = {"low": 1, "medium": 2, "high": 3}
            min_level = impact_order.get(impact.lower(), 0)
            if min_level > 0:
                impact_values = [k for k, v in impact_order.items() if v >= min_level]
                stmt = stmt.where(EconomicEventDB.impact.in_(impact_values))

        stmt = stmt.order_by(EconomicEventDB.date, EconomicEventDB.time)
        result = self.session.execute(stmt)
        rows: Sequence[EconomicEventDB] = result.scalars().all()

        return [self._to_pydantic(row) for row in rows]

    def get_events_for_date(self, event_date: date) -> list[EconomicEvent]:
        """Retrieve all events for a specific date.

        Args:
            event_date: The date to query.

        Returns:
            List of EconomicEvent pydantic models.
        """
        return self.get_events(event_date, event_date)

    def has_events_for_month(self, year: int, month: int) -> bool:
        """Check if events exist for a given month.

        Args:
            year: The year to check.
            month: The month to check.

        Returns:
            True if events exist, False otherwise.
        """
        from calendar import monthrange

        _, last_day = monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        stmt = (
            select(func.count())
            .select_from(EconomicEventDB)
            .where(
                and_(
                    EconomicEventDB.date >= start_date,
                    EconomicEventDB.date <= end_date,
                )
            )
        )
        result = self.session.execute(stmt)
        count = result.scalar()
        return count > 0 if count else False

    def get_stats(self) -> dict:
        """Get statistics about stored events.

        Returns:
            Dictionary with statistics:
            - total_events: Total number of events
            - by_currency: Count per currency
            - by_impact: Count per impact level
            - date_range: (earliest_date, latest_date)
        """
        # Total count
        total_stmt = select(func.count()).select_from(EconomicEventDB)
        total = self.session.execute(total_stmt).scalar() or 0

        # Count by currency
        currency_stmt = select(EconomicEventDB.currency, func.count()).group_by(
            EconomicEventDB.currency
        )
        currency_result = self.session.execute(currency_stmt)
        by_currency = {row[0]: row[1] for row in currency_result}

        # Count by impact
        impact_stmt = select(EconomicEventDB.impact, func.count()).group_by(
            EconomicEventDB.impact
        )
        impact_result = self.session.execute(impact_stmt)
        by_impact = {row[0]: row[1] for row in impact_result}

        # Date range
        date_range_stmt = select(
            func.min(EconomicEventDB.date), func.max(EconomicEventDB.date)
        )
        date_range_result = self.session.execute(date_range_stmt).first()
        date_range = (
            (date_range_result[0], date_range_result[1])
            if date_range_result and date_range_result[0]
            else (None, None)
        )

        return {
            "total_events": total,
            "by_currency": by_currency,
            "by_impact": by_impact,
            "date_range": date_range,
        }

    def delete_events_for_month(self, year: int, month: int) -> int:
        """Delete all events for a given month.

        Args:
            year: The year.
            month: The month.

        Returns:
            Number of deleted rows.
        """
        from calendar import monthrange

        from sqlalchemy import delete

        _, last_day = monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        stmt = delete(EconomicEventDB).where(
            and_(
                EconomicEventDB.date >= start_date,
                EconomicEventDB.date <= end_date,
            )
        )
        result = self.session.execute(stmt)
        return result.rowcount

    def _to_pydantic(self, db_event: EconomicEventDB) -> EconomicEvent:
        """Convert a database model to a Pydantic model.

        Args:
            db_event: Database event instance.

        Returns:
            EconomicEvent Pydantic model.
        """
        return EconomicEvent(
            date=db_event.date,
            time=db_event.time,
            currency=db_event.currency,
            impact=Impact(db_event.impact),
            event_name=db_event.event_name,
            actual=db_event.actual,
            forecast=db_event.forecast,
            previous=db_event.previous,
            event_type=EventType(db_event.event_type),
            direction=db_event.direction,
            weight=db_event.weight,
        )
