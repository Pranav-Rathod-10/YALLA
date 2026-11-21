import os

os.environ.setdefault("YALLA_ENV", "test")
os.environ.setdefault(
    "YALLA_DATABASE_URL", "postgresql+asyncpg://yalla:yalla@localhost:5433/yalla_test"
)

from collections.abc import AsyncIterator, Awaitable, Callable

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

import app.models  # noqa: F401  (register tables)
from app.api.deps import get_otp_store
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.main import create_app
from app.services.otp import MemoryOtpStore


@pytest.fixture(scope="session", autouse=True)
async def _schema() -> AsyncIterator[None]:
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@pytest.fixture(autouse=True)
async def _clean() -> AsyncIterator[None]:
    yield
    tables = ", ".join(t.name for t in Base.metadata.sorted_tables)
    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))


@pytest.fixture
async def session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as s:
        yield s


@pytest.fixture
def otp_store() -> MemoryOtpStore:
    return MemoryOtpStore()


@pytest.fixture
async def client(otp_store: MemoryOtpStore) -> AsyncIterator[AsyncClient]:
    app = create_app()
    app.dependency_overrides[get_otp_store] = lambda: otp_store
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        yield c


Login = Callable[..., Awaitable[dict[str, str]]]


@pytest.fixture
def login(client: AsyncClient) -> Login:
    """Sign in through the real OTP flow; returns auth headers."""

    async def _login(phone: str = "+919800000001", **profile: object) -> dict[str, str]:
        code = (await client.post("/v1/auth/otp/request", json={"phone": phone})).json()["dev_code"]
        tokens = (
            await client.post("/v1/auth/otp/verify", json={"phone": phone, "code": code})
        ).json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        if profile:
            await client.patch("/v1/me", json=profile, headers=headers)
        return headers

    return _login
