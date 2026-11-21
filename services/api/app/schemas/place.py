import uuid

from app.schemas.common import Schema


class PlaceOut(Schema):
    id: uuid.UUID
    name: str
    address: str
    city: str
    lat: float
    lng: float
