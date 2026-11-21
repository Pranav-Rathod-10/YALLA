import uuid
from datetime import datetime

from pydantic import Field

from app.models.enums import Gender
from app.schemas.common import Schema


class Me(Schema):
    id: uuid.UUID
    phone: str
    name: str
    gender: Gender
    gender_verified: bool
    home_place_id: uuid.UUID | None
    created_at: datetime


class MeUpdate(Schema):
    name: str | None = Field(None, min_length=1, max_length=80)
    gender: Gender | None = None
    home_place_id: uuid.UUID | None = None
