"""Alerts plus transactional outbox (ADR 0005).

`notify` must run inside the caller's transaction: the alert and its outbox row commit or roll
back together with the business change that caused them."""

import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models import Alert, Outbox, User
from app.models.enums import AlertKind
from app.schemas.alert import AlertOut
from app.schemas.common import UserSummary

PUSH_TOPIC = "push"


def notify(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    actor_id: uuid.UUID | None,
    kind: AlertKind,
    trip_id: uuid.UUID | None,
    text: str,
) -> None:
    session.add(Alert(user_id=user_id, actor_id=actor_id, kind=kind, trip_id=trip_id, text=text))
    session.add(
        Outbox(
            topic=PUSH_TOPIC,
            payload={
                "user_id": str(user_id),
                "kind": kind.value,
                "trip_id": str(trip_id) if trip_id else None,
                "text": text,
            },
        )
    )


async def list_alerts(session: AsyncSession, user: User, limit: int = 50) -> list[AlertOut]:
    actor = aliased(User)
    rows = await session.execute(
        select(Alert, actor)
        .outerjoin(actor, actor.id == Alert.actor_id)
        .where(Alert.user_id == user.id)
        .order_by(Alert.created_at.desc())
        .limit(limit)
    )
    return [
        AlertOut(
            id=a.id,
            kind=a.kind,
            text=a.text,
            actor=UserSummary.model_validate(who) if who else None,
            trip_id=a.trip_id,
            created_at=a.created_at,
            read_at=a.read_at,
        )
        for a, who in rows.all()
    ]


async def mark_all_read(session: AsyncSession, user: User) -> None:
    await session.execute(
        update(Alert)
        .where(Alert.user_id == user.id, Alert.read_at.is_(None))
        .values(read_at=func.now())
    )
