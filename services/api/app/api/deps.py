from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import UnauthorizedError
from app.core.redis import get_redis
from app.core.security import decode_token
from app.db.session import get_session
from app.models import User
from app.services.otp import OtpStore, RedisOtpStore

SessionDep = Annotated[AsyncSession, Depends(get_session)]

_bearer = HTTPBearer(auto_error=False)


def get_otp_store() -> OtpStore:
    return RedisOtpStore(get_redis())


async def get_current_user(
    session: SessionDep,
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> User:
    if creds is None:
        raise UnauthorizedError("Missing bearer token.")
    user = await session.get(User, decode_token(creds.credentials, "access"))
    if user is None:
        raise UnauthorizedError("User no longer exists.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
OtpDep = Annotated[OtpStore, Depends(get_otp_store)]


def is_prod() -> bool:
    return get_settings().env == "prod"
