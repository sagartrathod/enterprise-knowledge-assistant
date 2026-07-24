from __future__ import annotations

from typing import Literal
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Environment configuration.
    Loads deployment-specific values from .env.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ======================================================
    # Application
    # ======================================================

    APP_NAME: str = "Enterprise AI Knowledge Assistant"

    APP_ENV: Literal[
        "development",
        "testing",
        "production",
    ] = "development"

    DEBUG: bool = True

    SECRET_KEY: str

    # ======================================================
    # PostgreSQL
    # ======================================================

    POSTGRES_USER: str

    POSTGRES_PASSWORD: str

    POSTGRES_HOST: str

    POSTGRES_PORT: int = 5432

    POSTGRES_DB: str

    # ======================================================
    # LLM Providers
    # ======================================================

    GROQ_API_KEY: str

    OPENAI_API_KEY: str | None = None

    @property
    def DATABASE_URL(self) -> str:
        """
        PostgreSQL connection URL.
        """

        password = quote_plus(
            self.POSTGRES_PASSWORD
        )

        return (
            f"postgresql://"
            f"{self.POSTGRES_USER}:"
            f"{password}@"
            f"{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )


settings = Settings()