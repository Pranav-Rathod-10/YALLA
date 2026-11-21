from typing import Any

from geoalchemy2 import Geography
from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPk


class Place(UUIDPk, Base):
    __tablename__ = "places"

    name: Mapped[str] = mapped_column(String(120))
    address: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(80), index=True)
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Kolkata")
    location: Mapped[Any] = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=False)
    )

    __table_args__ = (
        Index("ix_places_location", "location", postgresql_using="gist"),
        Index("ix_places_name_lower", "name"),
    )
