import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPk


class Event(UUIDPk, Base):
    """Concerts and similar. Spec calls these 'concerts'; generalised for any city."""

    __tablename__ = "events"

    name: Mapped[str] = mapped_column(String(120))
    venue_place_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("places.id"))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    image_url: Mapped[str | None] = mapped_column(String(500))
