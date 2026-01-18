"""Initial schema with economic_events table.

Revision ID: 001
Revises: None
Create Date: 2026-01-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create economic_events table with all columns including new scoring fields."""
    op.create_table(
        "economic_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("date", sa.Date(), nullable=False, index=True),
        sa.Column("time", sa.Time(), nullable=True),
        sa.Column("currency", sa.String(5), nullable=False, index=True),
        sa.Column("impact", sa.String(10), nullable=False),
        sa.Column("event_name", sa.String(255), nullable=False),
        sa.Column("actual", sa.Float(), nullable=True),
        sa.Column("forecast", sa.Float(), nullable=True),
        sa.Column("previous", sa.Float(), nullable=True),
        sa.Column("event_type", sa.String(20), nullable=False, server_default="other"),
        sa.Column("direction", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("weight", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "scraped_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("date", "time", "currency", "event_name", name="uq_event"),
    )
    op.create_index("idx_needs_update", "economic_events", ["date", "actual"])


def downgrade() -> None:
    """Drop economic_events table."""
    op.drop_index("idx_needs_update", table_name="economic_events")
    op.drop_table("economic_events")
