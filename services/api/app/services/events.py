"""Events (concerts and similar) and the one-tap ride searches to and from them (spec 7.7)."""

import uuid
from datetime import timedelta
from typing import Literal
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import DomainError, NotFoundError
from app.models import Event, Place, User
from app.schemas.event import EventOut
from app.schemas.trip import TripOut
from app.schemas.trip_filters import TripFilters
from app.services.trips import list_trips, load_place

# Rides there leave up to 6 h before the start; rides back up to 12 h after (late shows).
BEFORE, AFTER = timedelta(hours=6), timedelta(hours=12)


class NoHomePlaceError(DomainError):
    code, title = "no_home_place", "Home place not set"


async def _out(session: AsyncSession, event: Event) -> EventOut:
    venue = await load_place(session, event.venue_place_id)
    return EventOut(
        id=event.id,
        name=event.name,
        venue=venue,
        starts_at=event.starts_at.astimezone(ZoneInfo(venue.timezone)),
        image_url=event.image_url,
    )


async def list_events(session: AsyncSession, city: str | None) -> list[EventOut]:
    stmt = select(Event).join(Place, Place.id == Event.venue_place_id).order_by(Event.starts_at)
    if city:
        stmt = stmt.where(Place.city.ilike(city))
    return [await _out(session, e) for e in (await session.scalars(stmt)).all()]


async def event_rides(
    session: AsyncSession,
    user: User,
    event_id: uuid.UUID,
    direction: Literal["to_event", "from_event"],
) -> list[TripOut]:
    """Home to Event: from home, to venue. Event to Home: the reverse. 'Home' is the user's
    home place (spec: Home base)."""
    event = await session.get(Event, event_id)
    if event is None:
        raise NotFoundError("Event not found.")
    if user.home_place_id is None:
        raise NoHomePlaceError("Set a home place in your profile to search event rides.")
    home, venue = user.home_place_id, event.venue_place_id
    from_id, to_id = (home, venue) if direction == "to_event" else (venue, home)
    filters = TripFilters(
        from_place_id=from_id,
        to_place_id=to_id,
        departs_after=event.starts_at - BEFORE,
        departs_before=event.starts_at + AFTER,
    )
    return await list_trips(session, filters, user)
