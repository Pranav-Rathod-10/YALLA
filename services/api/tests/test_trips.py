from datetime import date, timedelta

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Place
from tests.conftest import Login
from tests.factories import add_places

TOMORROW = (date.today() + timedelta(days=1)).isoformat()


def trip_body(
    places: dict[str, Place], frm: str, to: str, **overrides: object
) -> dict[str, object]:
    body: dict[str, object] = {
        "from_place_id": str(places[frm].id),
        "to_place_id": str(places[to].id),
        "depart_date": TOMORROW,
        "window_start": "18:00",
    }
    body.update(overrides)
    return body


async def test_post_trip_applies_spec_defaults(
    client: AsyncClient, session: AsyncSession, login: Login
) -> None:
    places = await add_places(session)
    headers = await login(name="Pranav R")
    r = await client.post(
        "/v1/trips", json=trip_body(places, "Panjim", "Vagator", seats=2), headers=headers
    )
    assert r.status_code == 201, r.text
    trip = r.json()
    assert trip["title"] == "Trip to Vagator"
    assert trip["tag"] == "Cab trip"
    assert trip["pickup"] == "Panjim"
    # Spec 7.5: total = seats + 1 and going = 1 (host counted).
    assert (trip["seats_total"], trip["going"], trip["seats_left"]) == (3, 1, 2)
    assert trip["joining"] == "approval"
    assert trip["females_only"] is False
    assert trip["host"]["name"] == "Pranav R"


async def test_trip_detail_lists_host_first(
    client: AsyncClient, session: AsyncSession, login: Login
) -> None:
    places = await add_places(session)
    headers = await login(name="Pranav R")
    trip = (
        await client.post("/v1/trips", json=trip_body(places, "Panjim", "Vagator"), headers=headers)
    ).json()
    r = await client.get(f"/v1/trips/{trip['id']}", headers=headers)
    assert r.status_code == 200
    assert [t["name"] for t in r.json()["travellers"]] == ["Pranav R"]


async def test_post_trip_validation(
    client: AsyncClient, session: AsyncSession, login: Login
) -> None:
    places = await add_places(session)
    headers = await login()
    for bad in ({"seats": 4}, {"seats": 0}, {"window_minutes": 45}):
        r = await client.post(
            "/v1/trips", json=trip_body(places, "Panjim", "Vagator", **bad), headers=headers
        )
        assert r.status_code == 422, bad
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    r = await client.post(
        "/v1/trips",
        json=trip_body(places, "Panjim", "Vagator", depart_date=yesterday),
        headers=headers,
    )
    assert r.status_code == 400
    assert r.json()["code"] == "past_date"


async def test_filters_combine_with_and(
    client: AsyncClient, session: AsyncSession, login: Login
) -> None:
    places = await add_places(session)
    headers = await login()
    for frm, to, start in [
        ("Panjim", "Vagator", "16:00"),
        ("Margao", "Gokarna", "07:00"),
        ("Panjim", "Anjuna", "19:00"),
    ]:
        await client.post(
            "/v1/trips", json=trip_body(places, frm, to, window_start=start), headers=headers
        )

    async def titles(**params: object) -> list[str]:
        r = await client.get("/v1/trips", params=params, headers=headers)
        return [t["title"] for t in r.json()]

    assert len(await titles()) == 3
    assert await titles(to="vag") == ["Trip to Vagator"]
    assert await titles(**{"from": "PANJIM"}) == ["Trip to Vagator", "Trip to Anjuna"]
    assert await titles(**{"from": "Current location"}) != []
    assert await titles(**{"from": "panjim", "time_min": 17 * 60}) == ["Trip to Vagator"]
    assert await titles(**{"from": "panjim", "time_min": 20 * 60}) == ["Trip to Anjuna"]
    assert await titles(to="hampi") == []


async def test_save_and_unsave(client: AsyncClient, session: AsyncSession, login: Login) -> None:
    places = await add_places(session)
    headers = await login()
    trip = (
        await client.post("/v1/trips", json=trip_body(places, "Panjim", "Vagator"), headers=headers)
    ).json()
    assert (await client.put(f"/v1/trips/{trip['id']}/save", headers=headers)).status_code == 204
    assert (await client.put(f"/v1/trips/{trip['id']}/save", headers=headers)).status_code == 204
    assert (await client.delete(f"/v1/trips/{trip['id']}/save", headers=headers)).status_code == 204


async def test_unknown_trip_is_404(client: AsyncClient, login: Login) -> None:
    r = await client.get("/v1/trips/00000000-0000-0000-0000-000000000000", headers=await login())
    assert r.status_code == 404


async def test_time_filter_wraps_past_midnight(
    client: AsyncClient, session: AsyncSession, login: Login
) -> None:
    """YAL-B01: an 11:30 PM filter must find a 12:00 AM concert ride back."""
    places = await add_places(session)
    headers = await login()
    await client.post(
        "/v1/trips",
        json=trip_body(places, "Vagator", "Panjim", window_start="00:00"),
        headers=headers,
    )
    r = await client.get("/v1/trips", params={"time_min": 23 * 60 + 30}, headers=headers)
    assert [t["title"] for t in r.json()] == ["Trip to Panjim"]
    r = await client.get("/v1/trips", params={"time_min": 22 * 60 + 30}, headers=headers)
    assert r.json() == []


async def test_place_filters_match_by_distance(
    client: AsyncClient, session: AsyncSession, login: Login
) -> None:
    """YAL-B02: Candolim is ~3 km from Calangute; text matching can never connect them."""
    places = await add_places(session)
    headers = await login()
    await client.post("/v1/trips", json=trip_body(places, "Calangute", "Panjim"), headers=headers)
    await client.post("/v1/trips", json=trip_body(places, "Margao", "Panjim"), headers=headers)

    async def titles_from(**params: object) -> list[str]:
        r = await client.get("/v1/trips", params=params, headers=headers)
        return [f"{t['from_place']['name']}->{t['to_place']['name']}" for t in r.json()]

    candolim = str(places["Candolim"].id)
    assert await titles_from(from_place_id=candolim) == ["Calangute->Panjim"]
    assert await titles_from(from_place_id=candolim, radius_km=1) == []
    # "Current location using GPS": standing in Margao.
    assert await titles_from(from_near="15.2832,73.9862") == ["Margao->Panjim"]
    assert await titles_from(to_near="15.49,73.83") == ["Calangute->Panjim", "Margao->Panjim"]
