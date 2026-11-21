"""Join requests. Every seat change locks the trip row (SELECT ... FOR UPDATE) so concurrent
accepts or instant joins can never overbook a trip."""

import uuid
from datetime import UTC, datetime
from typing import Literal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.core.errors import ConflictError, DomainError, ForbiddenError, NotFoundError
from app.models import Trip, TripMember, TripRequest, User
from app.models.enums import Joining, MemberRole, RequestStatus, TripStatus
from app.schemas.common import UserSummary
from app.schemas.request import TripRequestOut

LIVE = (RequestStatus.pending, RequestStatus.accepted)


class TripFullError(ConflictError):
    code, title = "trip_full", "Trip is full"


class OwnTripError(DomainError):
    code, title = "own_trip", "Cannot request your own trip"


class DuplicateRequestError(ConflictError):
    code, title = "duplicate_request", "Already requested"


class TripClosedError(ConflictError):
    code, title = "trip_closed", "Trip is not open"


class InvalidTransitionError(ConflictError):
    code, title = "invalid_transition", "Request cannot change to that status"


async def _locked_trip(session: AsyncSession, trip_id: uuid.UUID) -> Trip:
    trip = await session.scalar(select(Trip).where(Trip.id == trip_id).with_for_update())
    if trip is None:
        raise NotFoundError("Trip not found.")
    return trip


def _take_seat(session: AsyncSession, trip: Trip, user_id: uuid.UUID) -> None:
    if trip.seats_taken >= trip.passenger_seats:
        raise TripFullError("No seats left on this trip.")
    trip.seats_taken += 1
    if trip.seats_taken == trip.passenger_seats:
        trip.status = TripStatus.full
    session.add(TripMember(trip_id=trip.id, user_id=user_id, role=MemberRole.traveller))


async def _free_seat(session: AsyncSession, trip: Trip, user_id: uuid.UUID) -> None:
    trip.seats_taken -= 1
    if trip.status == TripStatus.full:
        trip.status = TripStatus.open
    member = await session.get(TripMember, (trip.id, user_id))
    if member is not None:
        await session.delete(member)


async def create_request(
    session: AsyncSession, user: User, trip_id: uuid.UUID, message: str | None
) -> TripRequest:
    trip = await _locked_trip(session, trip_id)
    if trip.host_id == user.id:
        raise OwnTripError("You cannot request your own trip.")
    if trip.status not in (TripStatus.open, TripStatus.full):
        raise TripClosedError("This trip is no longer taking requests.")
    if trip.departs_at <= datetime.now(UTC):
        raise TripClosedError("This trip has already left.")

    req = TripRequest(trip_id=trip.id, requester_id=user.id, message=message or None)
    if trip.joining == Joining.instant:
        _take_seat(session, trip, user.id)
        req.status = RequestStatus.accepted
        req.decided_at = datetime.now(UTC)
    session.add(req)
    try:
        await session.flush()
    except IntegrityError as exc:  # partial unique index on live requests
        await session.rollback()
        raise DuplicateRequestError("You already requested this trip.") from exc
    return req


async def decide_request(
    session: AsyncSession,
    host: User,
    request_id: uuid.UUID,
    status: Literal[RequestStatus.accepted, RequestStatus.declined],
) -> TripRequest:
    req = await session.get(TripRequest, request_id)
    if req is None:
        raise NotFoundError("Request not found.")
    trip = await _locked_trip(session, req.trip_id)
    if trip.host_id != host.id:
        raise ForbiddenError("Only the host can decide on requests.")
    await session.refresh(req, with_for_update=True)
    if req.status != RequestStatus.pending:
        raise InvalidTransitionError(f"Request is already {req.status.value}.")
    if status == RequestStatus.accepted:
        _take_seat(session, trip, req.requester_id)
    req.status = status
    req.decided_at = datetime.now(UTC)
    return req


async def cancel_request(session: AsyncSession, user: User, request_id: uuid.UUID) -> TripRequest:
    req = await session.get(TripRequest, request_id)
    if req is None or req.requester_id != user.id:
        raise NotFoundError("Request not found.")
    trip = await _locked_trip(session, req.trip_id)
    await session.refresh(req, with_for_update=True)
    if req.status not in LIVE:
        raise InvalidTransitionError(f"Request is already {req.status.value}.")
    if req.status == RequestStatus.accepted:
        await _free_seat(session, trip, user.id)
    req.status = RequestStatus.cancelled
    req.decided_at = datetime.now(UTC)
    return req


async def list_requests(
    session: AsyncSession,
    user: User,
    direction: Literal["sent", "received"],
    request_id: uuid.UUID | None = None,
) -> list[TripRequestOut]:
    requester, host = aliased(User), aliased(User)
    stmt = (
        select(TripRequest, Trip.title, requester, host)
        .join(Trip, Trip.id == TripRequest.trip_id)
        .join(requester, requester.id == TripRequest.requester_id)
        .join(host, host.id == Trip.host_id)
        .order_by(TripRequest.created_at.desc())
    )
    stmt = stmt.where(
        TripRequest.requester_id == user.id if direction == "sent" else Trip.host_id == user.id
    )
    if request_id is not None:
        stmt = stmt.where(TripRequest.id == request_id)
    return [
        TripRequestOut(
            id=r.id,
            trip_id=r.trip_id,
            trip_title=title,
            requester=UserSummary.model_validate(rq),
            host=UserSummary.model_validate(h),
            message=r.message,
            status=r.status,
            created_at=r.created_at,
            decided_at=r.decided_at,
        )
        for r, title, rq, h in (await session.execute(stmt)).all()
    ]


async def request_out(session: AsyncSession, user: User, req: TripRequest) -> TripRequestOut:
    """The request as seen by `user` (requester or host)."""
    direction: Literal["sent", "received"] = "sent" if req.requester_id == user.id else "received"
    [out] = await list_requests(session, user, direction, request_id=req.id)
    return out
