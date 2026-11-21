from typing import Any

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionLocal
from app.models import Outbox
from app.workers.outbox import drain
from tests.conftest import Login
from tests.test_requests import RIDER, setup_trip


class FakeSender:
    def __init__(self, fail_on: str | None = None) -> None:
        self.sent: list[dict[str, Any]] = []
        self.fail_on = fail_on

    async def send(self, payload: dict[str, Any]) -> None:
        if self.fail_on and self.fail_on in payload["text"]:
            raise RuntimeError("provider down")
        self.sent.append(payload)


async def test_request_and_decision_create_alerts(
    client: AsyncClient, session: AsyncSession, login: Login
) -> None:
    trip, host = await setup_trip(client, session, login)
    rider = await login(RIDER, name="Meera N")
    req = (await client.post(f"/v1/trips/{trip['id']}/requests", json={}, headers=rider)).json()
    await client.patch(f"/v1/requests/{req['id']}", json={"status": "accepted"}, headers=host)

    [host_alert] = (await client.get("/v1/me/alerts", headers=host)).json()
    assert host_alert["actor"]["name"] == "Meera N"
    assert host_alert["kind"] == "request"
    assert host_alert["text"] == "requested to join your Trip to Vagator"

    [rider_alert] = (await client.get("/v1/me/alerts", headers=rider)).json()
    assert (rider_alert["kind"], rider_alert["actor"]["name"]) == ("accepted", "Pranav R")
    assert rider_alert["read_at"] is None
    assert (await client.post("/v1/me/alerts/read", headers=rider)).status_code == 204
    assert (await client.get("/v1/me/alerts", headers=rider)).json()[0]["read_at"] is not None


async def test_failed_business_change_writes_no_alert(
    client: AsyncClient, session: AsyncSession, login: Login
) -> None:
    trip, host = await setup_trip(client, session, login)
    await client.post(f"/v1/trips/{trip['id']}/requests", json={}, headers=host)  # own trip: 400
    assert (await client.get("/v1/me/alerts", headers=host)).json() == []
    assert (await session.scalars(select(Outbox))).all() == []


async def test_worker_drains_outbox_once(
    client: AsyncClient, session: AsyncSession, login: Login
) -> None:
    trip, host = await setup_trip(client, session, login)
    await client.post(f"/v1/trips/{trip['id']}/requests", json={}, headers=await login(RIDER))

    sender = FakeSender()
    assert await drain(SessionLocal, sender) == 1
    assert await drain(SessionLocal, sender) == 0
    assert [p["kind"] for p in sender.sent] == ["request"]


async def test_failed_delivery_is_retried(
    client: AsyncClient, session: AsyncSession, login: Login
) -> None:
    trip, _ = await setup_trip(client, session, login)
    await client.post(f"/v1/trips/{trip['id']}/requests", json={}, headers=await login(RIDER))

    assert await drain(SessionLocal, FakeSender(fail_on="requested")) == 0
    ok = FakeSender()
    assert await drain(SessionLocal, ok) == 1
    [row] = (await session.scalars(select(Outbox))).all()
    assert row.attempts == 2
