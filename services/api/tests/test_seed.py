from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.seed import seed
from tests.conftest import Login


async def test_seed_is_idempotent_and_multi_city(
    client: AsyncClient, session: AsyncSession, login: Login
) -> None:
    assert await seed(session) is True
    assert await seed(session) is False

    headers = await login("+919800000002")  # seeded user, signs in through OTP
    cities = {
        t["from_place"]["city"] for t in (await client.get("/v1/trips", headers=headers)).json()
    }
    assert {"Goa", "Mumbai", "Bengaluru", "Dubai"} <= cities
