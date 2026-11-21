import uuid
from datetime import UTC, datetime, timedelta
from typing import Literal

import jwt

from app.core.config import get_settings
from app.core.errors import UnauthorizedError

TokenType = Literal["access", "refresh"]
ALGORITHM = "HS256"


def create_token(user_id: uuid.UUID, kind: TokenType) -> str:
    s = get_settings()
    ttl = (
        timedelta(minutes=s.access_token_minutes)
        if kind == "access"
        else timedelta(days=s.refresh_token_days)
    )
    now = datetime.now(UTC)
    claims = {
        "sub": str(user_id),
        "typ": kind,
        "iat": now,
        "exp": now + ttl,
        "jti": uuid.uuid4().hex,
    }
    return jwt.encode(claims, s.jwt_secret.get_secret_value(), algorithm=ALGORITHM)


def decode_token(token: str, expected: TokenType) -> uuid.UUID:
    try:
        claims = jwt.decode(
            token, get_settings().jwt_secret.get_secret_value(), algorithms=[ALGORITHM]
        )
    except jwt.PyJWTError as exc:
        raise UnauthorizedError("Invalid or expired token.") from exc
    if claims.get("typ") != expected:
        raise UnauthorizedError("Wrong token type.")
    return uuid.UUID(claims["sub"])
