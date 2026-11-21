"""departure as instant plus timezone

Revision ID: 5c1e0b7d2a44
Revises: 93977820ce3e
Create Date: 2026-11-21 21:58:02.771904

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5c1e0b7d2a44"
down_revision: str | Sequence[str] | None = "93977820ce3e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """depart_date + window_start had no zone (YAL-B04). Interpret existing rows in the
    pickup place's zone and store an instant (ADR 0006)."""
    op.add_column("trips", sa.Column("departs_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("trips", sa.Column("timezone", sa.String(length=64), nullable=True))
    op.execute(
        """
        UPDATE trips t
        SET timezone = p.timezone,
            departs_at = (t.depart_date + t.window_start) AT TIME ZONE p.timezone
        FROM places p
        WHERE p.id = t.from_place_id
        """
    )
    op.alter_column("trips", "departs_at", nullable=False)
    op.alter_column("trips", "timezone", nullable=False)
    op.drop_index("ix_trips_status_date", table_name="trips")
    op.drop_column("trips", "depart_date")
    op.drop_column("trips", "window_start")
    op.create_index("ix_trips_status_departs_at", "trips", ["status", "departs_at"])


def downgrade() -> None:
    op.add_column("trips", sa.Column("depart_date", sa.Date(), nullable=True))
    op.add_column("trips", sa.Column("window_start", sa.Time(), nullable=True))
    op.execute(
        """
        UPDATE trips
        SET depart_date = (departs_at AT TIME ZONE timezone)::date,
            window_start = (departs_at AT TIME ZONE timezone)::time
        """
    )
    op.alter_column("trips", "depart_date", nullable=False)
    op.alter_column("trips", "window_start", nullable=False)
    op.drop_index("ix_trips_status_departs_at", table_name="trips")
    op.drop_column("trips", "timezone")
    op.drop_column("trips", "departs_at")
    op.create_index("ix_trips_status_date", "trips", ["status", "depart_date"])
