from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="YALLA_", env_file=".env", extra="ignore")

    env: Literal["dev", "test", "prod"] = "dev"
    app_name: str = "Yalla API"
    log_level: str = "INFO"
    log_json: bool = False
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:8081"]

    database_url: str = "postgresql+asyncpg://yalla:yalla@localhost:5432/yalla"
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: SecretStr = SecretStr("dev-only-change-me-not-for-production")
    access_token_minutes: int = 15
    refresh_token_days: int = 30

    # ADR 0007: require gender_verified for Females only trips (off until verification exists).
    females_only_require_verified: bool = False


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if (
        settings.env == "prod"
        and settings.jwt_secret.get_secret_value() == "dev-only-change-me-not-for-production"
    ):
        raise RuntimeError("YALLA_JWT_SECRET must be set in production.")
    return settings
