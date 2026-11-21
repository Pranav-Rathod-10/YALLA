import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, SessionDep
from app.schemas.request import RequestCreate, RequestDecision, TripRequestOut
from app.services import requests

router = APIRouter(tags=["requests"])


@router.post("/trips/{trip_id}/requests", status_code=status.HTTP_201_CREATED)
async def request_to_join(
    trip_id: uuid.UUID, body: RequestCreate, user: CurrentUser, session: SessionDep
) -> TripRequestOut:
    req = await requests.create_request(session, user, trip_id, body.message)
    await session.commit()
    return await requests.request_out(session, user, req)


@router.patch("/requests/{request_id}")
async def decide(
    request_id: uuid.UUID, body: RequestDecision, user: CurrentUser, session: SessionDep
) -> TripRequestOut:
    req = await requests.decide_request(session, user, request_id, body.status)
    await session.commit()
    return await requests.request_out(session, user, req)


@router.delete("/requests/{request_id}")
async def cancel(request_id: uuid.UUID, user: CurrentUser, session: SessionDep) -> TripRequestOut:
    req = await requests.cancel_request(session, user, request_id)
    await session.commit()
    return await requests.request_out(session, user, req)


@router.get("/me/requests")
async def my_requests(
    user: CurrentUser,
    session: SessionDep,
    direction: Annotated[Literal["sent", "received"], Query()] = "sent",
) -> list[TripRequestOut]:
    return await requests.list_requests(session, user, direction)
