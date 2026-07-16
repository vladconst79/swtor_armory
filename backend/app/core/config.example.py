from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SWTOR Armory API"
    app_env: str = "local"
    debug: bool = False

    api_prefix: str = "/api"
    backend_cors_origins: Annotated[list[str], NoDecode] = Field(default_factory=list)

    database_url: str = "postgresql+psycopg://user:password@localhost:5432/database"

    secret_key: str = "change-me-to-a-secure-random-secret"
    access_token_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
