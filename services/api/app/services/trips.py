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
        seats_left=trip.seats_total - trip.going,
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
        # Spec 7.5: total = seats + 1, going = 1 (the host).
        seats_total=data.seats + 1,
        going=1,
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


def filtered(
    stmt: Select[Trip],
    *,
    to: str | None,
    from_: str | None,
    time_min: int | None,
) -> Select[Trip]:
    """Spec 7.3 filter rules, as written."""
    to_p, from_p = aliased(Place), aliased(Place)
    if to and to.strip().lower() != CURRENT_LOCATION:
        stmt = stmt.join(to_p, to_p.id == Trip.to_place_id).where(to_p.name.icontains(to.strip()))
    if from_ and from_.strip().lower() != CURRENT_LOCATION:
        stmt = stmt.join(from_p, from_p.id == Trip.from_place_id).where(
            from_p.name.icontains(from_.strip())
        )
    if time_min is not None:
        # Distance on a 24 h clock: 23:30 and 00:00 are 30 minutes apart, not 1410 (YAL-B01).
        diff = func.abs(_start_min() - time_min)
        stmt = stmt.where(func.least(diff, MINUTES_PER_DAY - diff) <= TIME_WINDOW_MIN)
    return stmt


async def list_trips(
    session: AsyncSession, *, to: str | None, from_: str | None, time_min: int | None
) -> list[TripOut]:
    stmt = filtered(select(Trip), to=to, from_=from_, time_min=time_min).order_by(
        Trip.depart_date, Trip.window_start, Trip.id
    )
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
