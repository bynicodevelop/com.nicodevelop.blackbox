"""Tests for the EventRepository class."""

from datetime import date, time

from blackbox.data.models import EconomicEvent, Impact
from blackbox.data.storage.repository import EventRepository


class TestEventRepositoryInsert:
    """Tests for inserting events into the database."""

    def test_upsert_events_insert(self, test_session, sample_events_for_db):
        """Test inserting new events."""
        repo = EventRepository(test_session)
        count = repo.upsert_events(sample_events_for_db)

        assert count == 4
        test_session.commit()

        # Verify events were inserted
        events = repo.get_events(date(2026, 1, 1), date(2026, 1, 31))
        assert len(events) == 4

    def test_upsert_events_empty_list(self, test_session):
        """Test upserting an empty list returns 0."""
        repo = EventRepository(test_session)
        count = repo.upsert_events([])
        assert count == 0

    def test_upsert_events_update(self, test_session, sample_events_for_db):
        """Test updating existing events with new values."""
        repo = EventRepository(test_session)

        # Insert initial events
        repo.upsert_events(sample_events_for_db)
        test_session.commit()

        # Create updated event with actual value changed (normalized float)
        updated_event = EconomicEvent(
            date=date(2026, 1, 15),
            time=time(10, 0),
            currency="EUR",
            impact=Impact.MEDIUM,
            event_name="ECB President Speech",
            actual="2.5%",  # Updated actual value (normalized to 0.025)
            forecast="2.1%",  # Normalized to 0.021
            previous=None,
        )

        count = repo.upsert_events([updated_event])
        test_session.commit()

        # The count shows rows affected by upsert
        assert count >= 1

        # Verify the update - values are normalized
        events = repo.get_events(date(2026, 1, 15), date(2026, 1, 15))
        ecb_events = [e for e in events if e.event_name == "ECB President Speech"]
        assert len(ecb_events) == 1
        assert ecb_events[0].actual == 0.025
        assert ecb_events[0].forecast == 0.021


class TestEventRepositoryQuery:
    """Tests for querying events from the database."""

    def test_get_events_date_range(self, test_session, sample_events_for_db):
        """Test filtering events by date range."""
        repo = EventRepository(test_session)
        repo.upsert_events(sample_events_for_db)
        test_session.commit()

        events = repo.get_events(date(2026, 1, 15), date(2026, 1, 16))
        assert len(events) == 3  # 2 on 15th, 1 on 16th

    def test_get_events_with_currency_filter(self, test_session, sample_events_for_db):
        """Test filtering events by currency."""
        repo = EventRepository(test_session)
        repo.upsert_events(sample_events_for_db)
        test_session.commit()

        events = repo.get_events(
            date(2026, 1, 1), date(2026, 1, 31), currencies=["USD"]
        )
        assert len(events) == 2
        assert all(e.currency == "USD" for e in events)

    def test_get_events_with_impact_filter(self, test_session, sample_events_for_db):
        """Test filtering events by minimum impact level."""
        repo = EventRepository(test_session)
        repo.upsert_events(sample_events_for_db)
        test_session.commit()

        events = repo.get_events(date(2026, 1, 1), date(2026, 1, 31), impact="high")
        assert len(events) == 1
        assert events[0].impact == Impact.HIGH

    def test_get_events_for_date(self, test_session, sample_events_for_db):
        """Test getting events for a specific date."""
        repo = EventRepository(test_session)
        repo.upsert_events(sample_events_for_db)
        test_session.commit()

        events = repo.get_events_for_date(date(2026, 1, 15))
        assert len(events) == 2

    def test_get_events_sorted_by_date_and_time(
        self, test_session, sample_events_for_db
    ):
        """Test that events are sorted by date and time."""
        repo = EventRepository(test_session)
        repo.upsert_events(sample_events_for_db)
        test_session.commit()

        events = repo.get_events(date(2026, 1, 1), date(2026, 1, 31))

        # Check ordering
        for i in range(len(events) - 1):
            if events[i].date == events[i + 1].date:
                # Same date: time should be in order (None comes first)
                if events[i].time is not None and events[i + 1].time is not None:
                    assert events[i].time <= events[i + 1].time
            else:
                # Different dates: earlier date first
                assert events[i].date < events[i + 1].date


class TestEventRepositoryNeedsUpdate:
    """Tests for the needs update functionality."""

    def test_get_events_needing_update(
        self, test_session, sample_events_for_db, future_events_for_db
    ):
        """Test finding dates with events that need actual values updated."""
        repo = EventRepository(test_session)
        repo.upsert_events(sample_events_for_db + future_events_for_db)
        test_session.commit()

        # Get dates needing update (future events without actual values)
        dates = repo.get_events_needing_update(date(2026, 2, 1), date(2026, 2, 28))

        assert len(dates) == 2
        assert date(2026, 2, 15) in dates
        assert date(2026, 2, 16) in dates


class TestEventRepositoryStats:
    """Tests for statistics functionality."""

    def test_get_stats(self, test_session, sample_events_for_db):
        """Test getting database statistics."""
        repo = EventRepository(test_session)
        repo.upsert_events(sample_events_for_db)
        test_session.commit()

        stats = repo.get_stats()

        assert stats["total_events"] == 4
        assert stats["by_currency"]["USD"] == 2
        assert stats["by_currency"]["EUR"] == 1
        assert stats["by_currency"]["JPY"] == 1
        assert stats["by_impact"]["high"] == 1
        assert stats["by_impact"]["medium"] == 1
        assert stats["by_impact"]["low"] == 1
        assert stats["by_impact"]["holiday"] == 1
        assert stats["date_range"] == (date(2026, 1, 15), date(2026, 1, 17))

    def test_get_stats_empty_database(self, test_session):
        """Test getting stats from empty database."""
        repo = EventRepository(test_session)
        stats = repo.get_stats()

        assert stats["total_events"] == 0
        assert stats["by_currency"] == {}
        assert stats["by_impact"] == {}
        assert stats["date_range"] == (None, None)


class TestEventRepositoryMonthOperations:
    """Tests for month-level operations."""

    def test_has_events_for_month_true(self, test_session, sample_events_for_db):
        """Test checking if events exist for a month (positive case)."""
        repo = EventRepository(test_session)
        repo.upsert_events(sample_events_for_db)
        test_session.commit()

        assert repo.has_events_for_month(2026, 1) is True

    def test_has_events_for_month_false(self, test_session, sample_events_for_db):
        """Test checking if events exist for a month (negative case)."""
        repo = EventRepository(test_session)
        repo.upsert_events(sample_events_for_db)
        test_session.commit()

        assert repo.has_events_for_month(2026, 3) is False

    def test_delete_events_for_month(self, test_session, sample_events_for_db):
        """Test deleting all events for a month."""
        repo = EventRepository(test_session)
        repo.upsert_events(sample_events_for_db)
        test_session.commit()

        count = repo.delete_events_for_month(2026, 1)
        test_session.commit()

        assert count == 4
        assert repo.has_events_for_month(2026, 1) is False
