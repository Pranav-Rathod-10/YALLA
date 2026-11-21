import uuid
from datetime import date
from typing import Annotated

from fastapi import HTTPException, Query
from pydantic import BaseModel

from app.services.geo import LatLng

LAT_LNG = r"^-?\d{1,2}(\.\d+)?,-?\d{1,3}(\.\d+)?$"


class TripFilters(BaseModel):
    from_place_id: uuid.UUID | None = None
    to_place_id: uuid.UUID | None = None
    from_near: LatLng | None = None
    to_near: LatLng | None = None
    from_text: str | None = None
    to_text: str | None = None
    radius_km: float = 3.0
    time_min: int | None = None
    on_date: date | None = None


def _latlng(raw: str | None, name: str) -> LatLng | None:
    if raw is None:
        return None
    try:
        return LatLng.parse(raw)
    except ValueError as exc:
        raise HTTPException(422, f"{name} must be 'lat,lng'") from exc


def trip_filters(
    from_place_id: Annotated[uuid.UUID | None, Query(description="Start near this place")] = None,
    to_place_id: Annotated[
        uuid.UUID | None, Query(description="Destination near this place")
    ] = None,
    from_near: Annotated[
        str | None, Query(pattern=LAT_LNG, description="'lat,lng', e.g. current location")
    ] = None,
    to_near: Annotated[str | None, Query(pattern=LAT_LNG)] = None,
    from_: Annotated[
        str | None, Query(alias="from", max_length=120, description="Fallback: name contains")
    ] = None,
    to: Annotated[str | None, Query(max_length=120, description="Fallback: name contains")] = None,
    radius_km: Annotated[float, Query(gt=0, le=50)] = 3.0,
    time_min: Annotated[
        int | None, Query(ge=0, lt=1440, description="Minutes since midnight; +-60 min")
    ] = None,
    on_date: Annotated[
        date | None, Query(alias="date", description="Local departure date at the pickup")
    ] = None,
) -> TripFilters:
    return TripFilters(
        from_place_id=from_place_id,
        to_place_id=to_place_id,
        from_near=_latlng(from_near, "from_near"),
        to_near=_latlng(to_near, "to_near"),
        from_text=from_,
        to_text=to,
        radius_km=radius_km,
        time_min=time_min,
        on_date=on_date,
    )
