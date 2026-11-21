"""Drains the outbox (ADR 0005). Safe to run several workers: rows are claimed with
FOR UPDATE SKIP LOCKED, so each row is handled by exactly one of them at a time."""

from typing import Any, Protocol

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models import Outbox

log = structlog.get_logger()
BATCH = 100
MAX_ATTEMPTS = 5


class PushSender(Protocol):
    async def send(self, payload: dict[str, Any]) -> None: ...


class LogPushSender:
    """Placeholder until a push provider (e.g. Expo Push) is chosen."""

    async def send(self, payload: dict[str, Any]) -> None:
        log.info("push.send", **payload)


async def drain(sessions: async_sessionmaker[AsyncSession], sender: PushSender) -> int:
    """Process one batch. Returns how many rows were delivered."""
    async with sessions() as session, session.begin():
        rows = (
            await session.scalars(
                select(Outbox)
                .where(Outbox.processed_at.is_(None), Outbox.attempts < MAX_ATTEMPTS)
                .order_by(Outbox.id)
                .limit(BATCH)
                .with_for_update(skip_locked=True)
            )
        ).all()
        delivered = 0
        for row in rows:
            row.attempts += 1
            try:
                await sender.send(row.payload)
            except Exception:  # one bad row must not block the batch
                log.exception("outbox.deliver_failed", outbox_id=row.id, attempts=row.attempts)
                continue
            row.processed_at = func.now()
            delivered += 1
        return delivered
