from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import Login
from tests.factories import add_places


async def test_substring_matches_sorted_by_name(
    client: AsyncClient, session: AsyncSession, login: Login
) -> None:
    await add_places(session)
    r = await client.get("/v1/places/search", params={"q": "ga"}, headers=await login())
    names = [p["name"] for p in r.json()]
    assert names == ["Dudhsagar Falls", "Margao", "Vagator", "Vasco da Gama"]


async def test_prefix_before_substring(
    client: AsyncClient, session: AsyncSession, login: Login
) -> None:
    await add_places(session)
    r = await client.get("/v1/places/search", params={"q": "an"}, headers=await login())
    names = [p["name"] for p in r.json()]
    assert names[0] == "Anjuna"
    assert set(names[1:]) <= {"Candolim", "Calangute", "Panjim", "Vasco da Gama"}
    assert len(names) <= 5


async def test_returns_coordinates(
    client: AsyncClient, session: AsyncSession, login: Login
) -> None:
    await add_places(session)
    r = await client.get("/v1/places/search", params={"q": "panjim"}, headers=await login())
    [panjim] = r.json()
    assert round(panjim["lat"], 3) == 15.491
    assert round(panjim["lng"], 3) == 73.828


async def test_empty_query_returns_nothing(client: AsyncClient, login: Login) -> None:
    r = await client.get("/v1/places/search", params={"q": "  "}, headers=await login())
    assert r.json() == []


async def test_near_ranks_closer_places_first(
    client: AsyncClient, session: AsyncSession, login: Login
) -> None:
    await add_places(session)
    # Standing in Margao (south): Margao beats Vagator (north) among "ga" matches.
    r = await client.get(
        "/v1/places/search", params={"q": "ga", "near": "15.28,73.98"}, headers=await login()
    )
    assert r.json()[0]["name"] == "Margao"
