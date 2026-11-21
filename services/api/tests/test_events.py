from datetime import UTC, date, datetime, timedelta

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event
from tests.conftest import Login
from tests.factories import add_places
from tests.test_trips import trip_body

TOMORROW = date.today() + timedelta(days=1)
DAY_AFTER = (TOMORROW + timedelta(days=1)).isoformat()


async def setup(client: AsyncClient, session: AsyncSession, login: Login):  # type: ignore[no-untyped-def]
    places = await add_places(session)
    # 8 PM IST tomorrow at Vagator; 14:30 UTC.
    starts = datetime.combine(TOMORROW, datetime.min.time(), UTC) + timedelta(hours=14, minutes=30)
    event = Event(
        name="Sunset Beats Festival", venue_place_id=places["Vagator"].id, starts_at=starts
    )
    session.add(event)
    session.add(Event(name="Candolim Live", venue_place_id=places["Candolim"].id, starts_at=starts))
    await session.commit()
    host = await login("+919800000001")
    rider = await login("+919800000002", home_place_id=str(places["Panjim"].id))
    return places, event, host, rider


async def test_list_events_in_local_time(
    client: AsyncClient, session: AsyncSession, login: Login
) -> None:
    _, _, _, rider = await setup(client, session, login)
    r = await client.get("/v1/events", params={"city": "goa"}, headers=rider)
    events = r.json()
    assert [e["name"] for e in events] == ["Sunset Beats Festival", "Candolim Live"]
    assert events[0]["starts_at"].endswith("T20:00:00+05:30")
    assert events[0]["venue"]["name"] == "Vagator"


async def test_rides_to_and_from_event(
    client: AsyncClient, session: AsyncSession, login: Login
) -> None:
    places, event, host, rider = await setup(client, session, login)
    there = trip_body(
        places, "Panjim", "Vagator", depart_date=TOMORROW.isoformat(), window_start="18:30"
    )
    # Ride back after midnight: the next local date, which a plain date filter would miss.
    back = trip_body(places, "Vagator", "Panjim", depart_date=DAY_AFTER, window_start="00:30")
    for body in (there, back):
        assert (await client.post("/v1/trips", json=body, headers=host)).status_code == 201

    url = f"/v1/events/{event.id}/rides"
    to_event = (await client.get(url, params={"direction": "to_event"}, headers=rider)).json()
    from_event = (await client.get(url, params={"direction": "from_event"}, headers=rider)).json()
    assert [t["title"] for t in to_event] == ["Trip to Vagator"]
    assert [t["title"] for t in from_event] == ["Trip to Panjim"]


async def test_event_with_no_rides_is_empty(
    client: AsyncClient, session: AsyncSession, login: Login
) -> None:
    """Spec 14: 'Candolim Live shows the empty state'."""
    _, _, _, rider = await setup(client, session, login)
    candolim = [
        e
        for e in (await client.get("/v1/events", headers=rider)).json()
        if e["name"] == "Candolim Live"
    ]
    r = await client.get(f"/v1/events/{candolim[0]['id']}/rides", headers=rider)
    assert r.json() == []


async def test_needs_home_place(client: AsyncClient, session: AsyncSession, login: Login) -> None:
    _, event, host, _ = await setup(client, session, login)
    r = await client.get(f"/v1/events/{event.id}/rides", headers=host)
    assert (r.status_code, r.json()["code"]) == (400, "no_home_place")
