import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, SessionDep
from app.schemas.event import EventOut
from app.schemas.trip import TripOut
from app.services import events

router = APIRouter(prefix="/events", tags=["events"])


@router.get("")
async def list_events(
    session: SessionDep, _: CurrentUser, city: Annotated[str | None, Query(max_length=80)] = None
) -> list[EventOut]:
    return await events.list_events(session, city)


@router.get("/{event_id}/rides")
async def event_rides(
    event_id: uuid.UUID,
    user: CurrentUser,
    session: SessionDep,
    direction: Literal["to_event", "from_event"] = "to_event",
) -> list[TripOut]:
    return await events.event_rides(session, user, event_id, direction)
