from datetime import date, time

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Place, Trip, User


async def _place(session: AsyncSession, name: str) -> Place:
    p = Place(name=name, address=f"{name}, Goa", city="Goa", location="POINT(73.83 15.49)")
    session.add(p)
    await session.flush()
    return p


async def _trip(session: AsyncSession, **overrides: object) -> Trip:
    host = User(phone="+919800000001", name="Pranav R")
    session.add(host)
    a, b = await _place(session, "Panjim"), await _place(session, "Vagator")
    await session.flush()
    fields: dict[str, object] = {
        "host_id": host.id,
        "title": "Trip",
        "from_place_id": a.id,
        "to_place_id": b.id,
        "pickup": "Bus stand",
        "depart_date": date(2030, 1, 1),
        "window_start": time(18, 0),
        "window_minutes": 30,
        "seats_total": 3,
    }
    fields.update(overrides)
    trip = Trip(**fields)
    session.add(trip)
    await session.flush()
    return trip


async def test_trip_defaults(session: AsyncSession) -> None:
    trip = await _trip(session)
    assert trip.going == 1
    assert trip.status == "open"


@pytest.mark.parametrize(
    "overrides",
    [{"window_minutes": 45}, {"seats_total": 5}, {"going": 4}, {"cost_per_person": -1}],
)
async def test_trip_constraints(session: AsyncSession, overrides: dict[str, object]) -> None:
    with pytest.raises(IntegrityError):
        await _trip(session, **overrides)
