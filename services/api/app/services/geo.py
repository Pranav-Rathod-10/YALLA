"""Distance helpers on PostGIS geography (metres, spheroid)."""

import uuid
from dataclasses import dataclass
from typing import Any

from geoalchemy2 import Geography
from sqlalchemy import cast, func, select

from app.models import Place


@dataclass(frozen=True)
class LatLng:
    lat: float
    lng: float

    @classmethod
    def parse(cls, raw: str) -> "LatLng":
        lat, lng = (float(part) for part in raw.split(","))
        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            raise ValueError("lat,lng out of range")
        return cls(lat, lng)


def point(at: LatLng) -> Any:
    return cast(func.ST_SetSRID(func.ST_MakePoint(at.lng, at.lat), 4326), Geography)


def place_point(place_id: uuid.UUID) -> Any:
    return select(Place.location).where(Place.id == place_id).scalar_subquery()


def within(column: Any, origin: Any, radius_km: float) -> Any:
    return func.ST_DWithin(column, origin, radius_km * 1000)
