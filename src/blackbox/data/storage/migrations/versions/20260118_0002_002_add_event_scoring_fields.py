"""Add event scoring fields (event_type, direction, weight).

This migration adds support for fundamental scoring by adding:
- event_type: Category of event (employment, inflation, etc.)
- direction: +1 or -1 indicating if higher value is bullish or bearish
- weight: Importance from 1-10

For existing databases without these columns, this migration will add them.
For new databases (using 001_initial_schema), this is a no-op as columns already exist.

Revision ID: 002
Revises: 001
Create Date: 2026-01-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    """Add event_type, direction, weight columns if they don't exist."""
    # Only add columns if they don't already exist
    # (they will exist if database was created fresh with 001)
    if not column_exists("economic_events", "event_type"):
        op.add_column(
            "economic_events",
            sa.Column(
                "event_type", sa.String(20), nullable=False, server_default="other"
            ),
        )

    if not column_exists("economic_events", "direction"):
        op.add_column(
            "economic_events",
            sa.Column("direction", sa.Integer(), nullable=False, server_default="1"),
        )

    if not column_exists("economic_events", "weight"):
        op.add_column(
            "economic_events",
            sa.Column("weight", sa.Integer(), nullable=False, server_default="1"),
        )


def downgrade() -> None:
    """Remove event_type, direction, weight columns."""
    op.drop_column("economic_events", "weight")
    op.drop_column("economic_events", "direction")
    op.drop_column("economic_events", "event_type")
