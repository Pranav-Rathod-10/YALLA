"""passenger seats exclude the host

Revision ID: 93977820ce3e
Revises: 93b675be55cd
Create Date: 2026-11-21 21:52:10.418220

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93977820ce3e'
down_revision: Union[str, Sequence[str], None] = '93b675be55cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Spec 7.5 stored total = seats + 1 and going = 1 (host counted). Switch to passenger-only
    counts (YAL-B03) and carry existing rows over."""
    op.add_column("trips", sa.Column("passenger_seats", sa.SmallInteger(), nullable=True))
    op.add_column("trips", sa.Column("seats_taken", sa.SmallInteger(), nullable=True))
    op.execute("UPDATE trips SET passenger_seats = seats_total - 1, seats_taken = going - 1")
    op.alter_column("trips", "passenger_seats", nullable=False)
    op.alter_column("trips", "seats_taken", nullable=False)
    op.drop_constraint("going", "trips", type_="check")
    op.drop_constraint("seats_total", "trips", type_="check")
    op.drop_column("trips", "going")
    op.drop_column("trips", "seats_total")
    op.create_check_constraint("passenger_seats", "trips", "passenger_seats BETWEEN 1 AND 3")
    op.create_check_constraint("seats_taken", "trips", "seats_taken BETWEEN 0 AND passenger_seats")


def downgrade() -> None:
    op.add_column("trips", sa.Column("seats_total", sa.SmallInteger(), nullable=True))
    op.add_column("trips", sa.Column("going", sa.SmallInteger(), nullable=True))
    op.execute("UPDATE trips SET seats_total = passenger_seats + 1, going = seats_taken + 1")
    op.alter_column("trips", "seats_total", nullable=False)
    op.alter_column("trips", "going", nullable=False)
    op.drop_constraint("seats_taken", "trips", type_="check")
    op.drop_constraint("passenger_seats", "trips", type_="check")
    op.drop_column("trips", "seats_taken")
    op.drop_column("trips", "passenger_seats")
    op.create_check_constraint("seats_total", "trips", "seats_total BETWEEN 2 AND 4")
    op.create_check_constraint("going", "trips", "going BETWEEN 1 AND seats_total")
