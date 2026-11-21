"""arq worker entrypoint:  arq app.workers.main.WorkerSettings"""

from typing import Any, ClassVar

from arq import cron
from arq.connections import RedisSettings

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.workers.outbox import LogPushSender, drain


async def drain_outbox(ctx: dict[str, Any]) -> int:
    return await drain(SessionLocal, ctx["push"])


async def startup(ctx: dict[str, Any]) -> None:
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_json)
    ctx["push"] = LogPushSender()


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(get_settings().redis_url)
    on_startup = startup
    cron_jobs: ClassVar[list[Any]] = [
        cron(drain_outbox, second={0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55})
    ]
