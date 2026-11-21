from collections.abc import Sequence
from typing import Any

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Place
from app.schemas.place import PlaceOut
from app.services.geo import LatLng, point

LIMIT = 5


def place_columns() -> list[Any]:
    """Place columns plus lat/lng pulled out of the geography point."""
    geom = func.ST_GeomFromWKB(func.ST_AsBinary(Place.location))
    return [
        Place.id,
        Place.name,
        Place.address,
        Place.city,
        func.ST_Y(geom).label("lat"),
        func.ST_X(geom).label("lng"),
    ]


def to_out(rows: Sequence[Any]) -> list[PlaceOut]:
    return [PlaceOut.model_validate(r, from_attributes=True) for r in rows]


async def search_places(
    session: AsyncSession, q: str, near: LatLng | None = None
) -> list[PlaceOut]:
    """Spec 8.1: prefix matches first, then other substring matches, max 5.
    With `near`, places closer to the user win ties (the app works in any city)."""
    q = q.strip()
    if not q:
        return []
    name = func.lower(Place.name)
    needle = q.lower()
    rank = case((name.startswith(needle), 0), else_=1)
    stmt = (
        select(*place_columns())
        .where(name.contains(needle))
        .order_by(
            rank,
            func.ST_Distance(Place.location, point(near)) if near else Place.name,
            Place.name,
        )
        .limit(LIMIT)
    )
    return to_out((await session.execute(stmt)).all())
