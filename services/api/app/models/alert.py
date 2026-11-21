import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAt, UUIDPk
from app.models._types import str_enum
from app.models.enums import AlertKind


class Alert(UUIDPk, CreatedAt, Base):
    __tablename__ = "alerts"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    actor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    kind: Mapped[AlertKind] = mapped_column(str_enum(AlertKind, "alert_kind"))
    trip_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"))
    text: Mapped[str] = mapped_column(String(255))
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (Index("ix_alerts_user_created", "user_id", "created_at"),)


class Outbox(CreatedAt, Base):
    """Transactional outbox (ADR 0005). Written with the business change, drained by the worker."""

    __tablename__ = "outbox"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    topic: Mapped[str] = mapped_column(String(60))
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(default=0)

    __table_args__ = (
        Index("ix_outbox_pending", "id", postgresql_where=text("processed_at IS NULL")),
    )
