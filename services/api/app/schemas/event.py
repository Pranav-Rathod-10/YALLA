import uuid
from datetime import datetime

from app.schemas.common import Schema
from app.schemas.place import PlaceOut


class EventOut(Schema):
    id: uuid.UUID
    name: str
    venue: PlaceOut
    starts_at: datetime
    image_url: str | None
