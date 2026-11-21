import asyncio
from typing import Any

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import Login
from tests.factories import add_places
from tests.test_trips import trip_body

HOST, RIDER, RIDER2 = "+919800000001", "+919800000002", "+919800000003"


async def setup_trip(
    client: AsyncClient, session: AsyncSession, login: Login, **trip: Any
) -> tuple[dict[str, Any], dict[str, str]]:
    places = await add_places(session)
    host = await login(HOST, name="Pranav R")
    r = await client.post(
        "/v1/trips", json=trip_body(places, "Panjim", "Vagator", **trip), headers=host
    )
    return r.json(), host


async def test_request_accept_flow(
    client: AsyncClient, session: AsyncSession, login: Login
) -> None:
    trip, host = await setup_trip(client, session, login)
    rider = await login(RIDER, name="Meera N")

    r = await client.post(
        f"/v1/trips/{trip['id']}/requests", json={"message": "Hi!"}, headers=rider
    )
    assert r.status_code == 201, r.text
    req = r.json()
    assert (req["status"], req["trip_title"], req["host"]["name"]) == (
        "pending",
        "Trip to Vagator",
        "Pranav R",
    )

    received = (
        await client.get("/v1/me/requests", params={"direction": "received"}, headers=host)
    ).json()
    assert [x["requester"]["name"] for x in received] == ["Meera N"]

    r = await client.patch(f"/v1/requests/{req['id']}", json={"status": "accepted"}, headers=host)
    assert r.json()["status"] == "accepted"

    detail = (await client.get(f"/v1/trips/{trip['id']}", headers=host)).json()
    assert detail["seats_taken"] == 1
    assert [t["name"] for t in detail["travellers"]] == ["Pranav R", "Meera N"]


async def test_decline(client: AsyncClient, session: AsyncSession, login: Login) -> None:
    trip, host = await setup_trip(client, session, login)
    rider = await login(RIDER)
    req = (await client.post(f"/v1/trips/{trip['id']}/requests", json={}, headers=rider)).json()
    r = await client.patch(f"/v1/requests/{req['id']}", json={"status": "declined"}, headers=host)
    assert r.json()["status"] == "declined"
    # A decided request cannot be decided again.
    r = await client.patch(f"/v1/requests/{req['id']}", json={"status": "accepted"}, headers=host)
    assert r.status_code == 409
    assert r.json()["code"] == "invalid_transition"


async def test_rules(client: AsyncClient, session: AsyncSession, login: Login) -> None:
    trip, host = await setup_trip(client, session, login)
    rider = await login(RIDER)
    url = f"/v1/trips/{trip['id']}/requests"

    own = await client.post(url, json={}, headers=host)
    assert own.json()["code"] == "own_trip"

    assert (await client.post(url, json={}, headers=rider)).status_code == 201
    dup = await client.post(url, json={}, headers=rider)
    assert (dup.status_code, dup.json()["code"]) == (409, "duplicate_request")

    too_long = await client.post(url, json={"message": "x" * 1025}, headers=await login(RIDER2))
    assert too_long.status_code == 422


async def test_only_host_decides(client: AsyncClient, session: AsyncSession, login: Login) -> None:
    trip, _ = await setup_trip(client, session, login)
    rider = await login(RIDER)
    req = (await client.post(f"/v1/trips/{trip['id']}/requests", json={}, headers=rider)).json()
    r = await client.patch(f"/v1/requests/{req['id']}", json={"status": "accepted"}, headers=rider)
    assert r.status_code == 403


async def test_cancel_accepted_frees_the_seat(
    client: AsyncClient, session: AsyncSession, login: Login
) -> None:
    trip, host = await setup_trip(client, session, login, passenger_seats=1)
    rider = await login(RIDER)
    req = (await client.post(f"/v1/trips/{trip['id']}/requests", json={}, headers=rider)).json()
    await client.patch(f"/v1/requests/{req['id']}", json={"status": "accepted"}, headers=host)
    full = (await client.get(f"/v1/trips/{trip['id']}", headers=host)).json()
    assert (full["status"], full["seats_left"]) == ("full", 0)

    r = await client.delete(f"/v1/requests/{req['id']}", headers=rider)
    assert r.json()["status"] == "cancelled"
    reopened = (await client.get(f"/v1/trips/{trip['id']}", headers=host)).json()
    assert (reopened["status"], reopened["seats_left"]) == ("open", 1)
    # Cancelling frees the slot for a fresh request.
    again = await client.post(f"/v1/trips/{trip['id']}/requests", json={}, headers=rider)
    assert again.status_code == 201


async def test_instant_join_takes_a_seat(
    client: AsyncClient, session: AsyncSession, login: Login
) -> None:
    trip, _ = await setup_trip(client, session, login, joining="instant", passenger_seats=1)
    r = await client.post(f"/v1/trips/{trip['id']}/requests", json={}, headers=await login(RIDER))
    assert r.json()["status"] == "accepted"
    full = await client.post(
        f"/v1/trips/{trip['id']}/requests", json={}, headers=await login(RIDER2)
    )
    assert (full.status_code, full.json()["code"]) == (409, "trip_full")


async def test_concurrent_accepts_never_overbook(
    client: AsyncClient, session: AsyncSession, login: Login
) -> None:
    trip, host = await setup_trip(client, session, login, passenger_seats=1)
    ids = []
    for phone in (RIDER, RIDER2):
        r = await client.post(
            f"/v1/trips/{trip['id']}/requests", json={}, headers=await login(phone)
        )
        ids.append(r.json()["id"])

    results = await asyncio.gather(
        *(client.patch(f"/v1/requests/{i}", json={"status": "accepted"}, headers=host) for i in ids)
    )
    assert sorted(r.status_code for r in results) == [200, 409]
    detail = (await client.get(f"/v1/trips/{trip['id']}", headers=host)).json()
    assert detail["seats_taken"] == 1
