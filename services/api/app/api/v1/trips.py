import uuid
from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.api.deps import CurrentUser, SessionDep
from app.schemas.trip import TripCreate, TripDetail, TripOut
from app.services import trips

router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("")
async def list_trips(
    session: SessionDep,
    _: CurrentUser,
    to: Annotated[
        str | None, Query(max_length=120, description="Destination name contains")
    ] = None,
    from_: Annotated[
        str | None, Query(alias="from", max_length=120, description="Start point name contains")
    ] = None,
    time_min: Annotated[
        int | None, Query(ge=0, lt=1440, description="Minutes since midnight; +-60 min")
    ] = None,
) -> list[TripOut]:
    return await trips.list_trips(session, to=to, from_=from_, time_min=time_min)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_trip(body: TripCreate, user: CurrentUser, session: SessionDep) -> TripOut:
    return await trips.create_trip(session, user, body)


@router.get("/{trip_id}")
async def get_trip(trip_id: uuid.UUID, session: SessionDep, _: CurrentUser) -> TripDetail:
    return await trips.get_trip(session, trip_id)


@router.put("/{trip_id}/save", status_code=status.HTTP_204_NO_CONTENT)
async def save_trip(trip_id: uuid.UUID, user: CurrentUser, session: SessionDep) -> Response:
    await trips.set_saved(session, user, trip_id, saved=True)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{trip_id}/save", status_code=status.HTTP_204_NO_CONTENT)
async def unsave_trip(trip_id: uuid.UUID, user: CurrentUser, session: SessionDep) -> Response:
    await trips.set_saved(session, user, trip_id, saved=False)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
