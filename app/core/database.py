import asyncpg
from typing import AsyncGenerator

from app.core.config import settings
from app.core.logger import logger


class DatabaseManager:
    def __init__(self) -> None:
        self.pool: asyncpg.Pool | None = None

    async def connect_to_db(self) -> None:
        """Initialize PostgreSQL connection pool."""
        if self.pool:
            return

        try:
            logger.info("Initializing asyncpg connection pool...")

            # Debug configuration (do not log passwords)
            logger.info(
                f"""
Database Configuration
----------------------
HOST     : {settings.POSTGRES_HOST!r}
PORT     : {settings.POSTGRES_PORT}
DATABASE : {settings.POSTGRES_DB}
USER     : {settings.POSTGRES_USER}
DEBUG    : {settings.DEBUG}
"""
            )

            self.pool = await asyncpg.create_pool(
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB,
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                min_size=5,
                max_size=20,
                max_queries=50000,
                max_inactive_connection_lifetime=300.0,
            )

            logger.info("Database connection pool established successfully.")

        except Exception:
            logger.exception("Failed to establish PostgreSQL connection pool.")
            raise

    async def close_db_connection(self) -> None:
        """Close all database connections."""
        if self.pool:
            logger.info("Closing database connection pool...")
            await self.pool.close()
            self.pool = None
            logger.info("Database connection pool closed.")

    def get_pool(self) -> asyncpg.Pool:
        if self.pool is None:
            raise RuntimeError("Database pool has not been initialized.")

        return self.pool


db_manager = DatabaseManager()


async def get_db_pool() -> AsyncGenerator[asyncpg.Pool, None]:
    yield db_manager.get_pool()