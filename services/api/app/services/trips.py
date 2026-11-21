import uuid
from datetime import date
from typing import Any

from sqlalchemy import Select, case, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.core.errors import DomainError, NotFoundError
from app.models import Place, SavedTrip, Trip, TripMember, User
from app.models.enums import MemberRole
from app.schemas.common import UserSummary
from app.schemas.place import PlaceOut
from app.schemas.trip import TripCreate, TripDetail, TripOut
from app.schemas.trip_filters import TripFilters
from app.services.geo import LatLng, place_point, point, within
from app.services.places import place_columns

CURRENT_LOCATION = "current location"
MINUTES_PER_DAY = 24 * 60
TIME_WINDOW_MIN = 60


class PastDateError(DomainError):
    code, title = "past_date", "Date is in the past"


async def _place(session: AsyncSession, place_id: uuid.UUID) -> PlaceOut:
    row = (
        await session.execute(select(*place_columns()).where(Place.id == place_id))
    ).one_or_none()
    if row is None:
        raise NotFoundError("Place not found.")
    return PlaceOut.model_validate(row, from_attributes=True)


async def _to_out(session: AsyncSession, trip: Trip) -> TripOut:
    host = await session.get(User, trip.host_id)
    if host is None:
        raise NotFoundError("Trip host not found.")
    return TripOut(
        **{k: getattr(trip, k) for k in TripOut.model_fields if hasattr(Trip, k)},
        from_place=await _place(session, trip.from_place_id),
        to_place=await _place(session, trip.to_place_id),
        seats_left=trip.passenger_seats - trip.seats_taken,
        host=UserSummary.model_validate(host),
    )


async def create_trip(session: AsyncSession, host: User, data: TripCreate) -> TripOut:
    if data.depart_date < date.today():
        raise PastDateError("Past dates cannot be posted.")
    to_place = await _place(session, data.to_place_id)
    from_place = await _place(session, data.from_place_id)
    trip = Trip(
        host_id=host.id,
        title=data.title or f"Trip to {to_place.name}",
        tag="Cab trip",
        from_place_id=data.from_place_id,
        to_place_id=data.to_place_id,
        pickup=data.pickup or from_place.name,
        depart_date=data.depart_date,
        window_start=data.window_start,
        window_minutes=data.window_minutes,
        passenger_seats=data.passenger_seats,
        seats_taken=0,
        vehicle=data.vehicle,
        cost_per_person=data.cost_per_person,
        cost_shared=data.cost_shared,
        joining=data.joining,
        females_only=data.females_only,
    )
    session.add(trip)
    await session.flush()
    session.add(TripMember(trip_id=trip.id, user_id=host.id, role=MemberRole.host))
    await session.commit()
    return await _to_out(session, trip)


def _start_min() -> Any:
    """Minutes since midnight of the window start (spec: startMin)."""
    return func.extract("hour", Trip.window_start) * 60 + func.extract("minute", Trip.window_start)


def _place_filter(
    stmt: Select[Trip],
    column: Any,
    *,
    place_id: uuid.UUID | None,
    near: LatLng | None,
    text: str | None,
    radius_km: float,
) -> Select[Trip]:
    """Match by distance (ADR 0003). Free text is only a fallback for clients without a place."""
    place = aliased(Place)
    if place_id is not None:
        origin = place_point(place_id)
    elif near is not None:
        origin = point(near)
    elif text and text.strip().lower() != CURRENT_LOCATION:
        return stmt.join(place, place.id == column).where(place.name.icontains(text.strip()))
    else:
        return stmt
    return stmt.join(place, place.id == column).where(within(place.location, origin, radius_km))


def filtered(stmt: Select[Trip], f: TripFilters) -> Select[Trip]:
    stmt = _place_filter(
        stmt,
        Trip.from_place_id,
        place_id=f.from_place_id,
        near=f.from_near,
        text=f.from_text,
        radius_km=f.radius_km,
    )
    stmt = _place_filter(
        stmt,
        Trip.to_place_id,
        place_id=f.to_place_id,
        near=f.to_near,
        text=f.to_text,
        radius_km=f.radius_km,
    )
    if f.time_min is not None:
        # Distance on a 24 h clock: 23:30 and 00:00 are 30 minutes apart, not 1410 (YAL-B01).
        diff = func.abs(_start_min() - f.time_min)
        stmt = stmt.where(func.least(diff, MINUTES_PER_DAY - diff) <= TIME_WINDOW_MIN)
    return stmt


async def list_trips(session: AsyncSession, f: TripFilters) -> list[TripOut]:
    stmt = filtered(select(Trip), f).order_by(Trip.depart_date, Trip.window_start, Trip.id)
    trips = (await session.scalars(stmt)).all()
    return [await _to_out(session, t) for t in trips]


async def get_trip(session: AsyncSession, trip_id: uuid.UUID) -> TripDetail:
    trip = await session.get(Trip, trip_id)
    if trip is None:
        raise NotFoundError("Trip not found.")
    rows = await session.execute(
        select(User.id, User.name)
        .join(TripMember, TripMember.user_id == User.id)
        .where(TripMember.trip_id == trip_id)
        .order_by(case((TripMember.role == MemberRole.host, 0), else_=1), TripMember.joined_at)
    )
    out = await _to_out(session, trip)
    return TripDetail(
        **out.model_dump(),
        travellers=[UserSummary.model_validate(r, from_attributes=True) for r in rows],
    )


async def set_saved(session: AsyncSession, user: User, trip_id: uuid.UUID, saved: bool) -> None:
    if await session.get(Trip, trip_id) is None:
        raise NotFoundError("Trip not found.")
    exists = await session.get(SavedTrip, (user.id, trip_id))
    if saved and exists is None:
        session.add(SavedTrip(user_id=user.id, trip_id=trip_id))
    elif not saved and exists is not None:
        await session.execute(
            delete(SavedTrip).where(SavedTrip.user_id == user.id, SavedTrip.trip_id == trip_id)
        )
    await session.commit()
