"""Add surprise column for economic events.

This migration adds the surprise column to store the normalized
surprise score: direction * (actual - forecast) / |forecast|

It also migrates existing data by computing surprise for events
that have both actual and forecast values.

Revision ID: 003
Revises: 002
Create Date: 2026-01-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: str | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    """Add surprise column and compute values for existing events."""
    # Add the column if it doesn't exist
    if not column_exists("economic_events", "surprise"):
        op.add_column(
            "economic_events",
            sa.Column("surprise", sa.Float(), nullable=True),
        )

    # Migrate existing data: compute surprise for events with actual and forecast
    op.execute(
        """
        UPDATE economic_events
        SET surprise = direction * (actual - forecast) / ABS(forecast)
        WHERE actual IS NOT NULL
          AND forecast IS NOT NULL
          AND forecast != 0
          AND surprise IS NULL
        """
    )


def downgrade() -> None:
    """Remove surprise column."""
    op.drop_column("economic_events", "surprise")
