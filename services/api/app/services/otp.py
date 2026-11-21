"""One-time login codes. Redis in real environments, in-memory for tests."""

import secrets
import time
from typing import Protocol

from redis.asyncio import Redis

OTP_TTL_SECONDS = 300


def new_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


class OtpStore(Protocol):
    async def put(self, phone: str, code: str) -> None: ...
    async def pop_if_match(self, phone: str, code: str) -> bool: ...


class RedisOtpStore:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def put(self, phone: str, code: str) -> None:
        await self.redis.set(f"otp:{phone}", code, ex=OTP_TTL_SECONDS)

    async def pop_if_match(self, phone: str, code: str) -> bool:
        stored = await self.redis.getdel(f"otp:{phone}")
        if stored is None:
            return False
        value = stored.decode() if isinstance(stored, bytes) else stored
        return secrets.compare_digest(value, code)


class MemoryOtpStore:
    def __init__(self) -> None:
        self._codes: dict[str, tuple[str, float]] = {}

    async def put(self, phone: str, code: str) -> None:
        self._codes[phone] = (code, time.monotonic() + OTP_TTL_SECONDS)

    async def pop_if_match(self, phone: str, code: str) -> bool:
        stored = self._codes.pop(phone, None)
        if stored is None or stored[1] < time.monotonic():
            return False
        return secrets.compare_digest(stored[0], code)
