import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAt, UUIDPk
from app.models._types import str_enum
from app.models.enums import Gender


class User(UUIDPk, CreatedAt, Base):
    __tablename__ = "users"

    phone: Mapped[str] = mapped_column(String(20), unique=True)
    name: Mapped[str] = mapped_column(String(80), default="")
    gender: Mapped[Gender] = mapped_column(str_enum(Gender, "gender"), default=Gender.undisclosed)
    gender_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    home_place_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("places.id"))
