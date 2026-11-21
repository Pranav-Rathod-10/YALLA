import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import CurrentUser, SessionDep
from app.schemas.trip import TripCreate, TripDetail, TripOut
from app.schemas.trip_filters import TripFilters, trip_filters
from app.services import trips

router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("")
async def list_trips(
    session: SessionDep,
    _: CurrentUser,
    filters: Annotated[TripFilters, Depends(trip_filters)],
) -> list[TripOut]:
    return await trips.list_trips(session, filters)


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
