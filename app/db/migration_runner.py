# app/db/migration_runner.py

import asyncio
from pathlib import Path

import asyncpg

from app.core.config import settings


MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


async def run_migrations():
    print("Connecting to database...")

    conn = await asyncpg.connect(
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB,
    )

    try:
        print("Creating migration tracking table...")

        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                filename TEXT UNIQUE NOT NULL,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        sql_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

        if not sql_files:
            print("No migration files found.")
            return

        for sql_file in sql_files:
            filename = sql_file.name

            exists = await conn.fetchval(
                """
                SELECT EXISTS(
                    SELECT 1 
                    FROM schema_migrations
                    WHERE filename = $1
                )
                """,
                filename,
            )

            if exists:
                print(f"Skipping {filename}")
                continue

            print(f"Running {filename}")

            sql = sql_file.read_text(encoding="utf-8")

            async with conn.transaction():
                await conn.execute(sql)

                await conn.execute(
                    """
                    INSERT INTO schema_migrations(filename)
                    VALUES($1)
                    """,
                    filename,
                )

            print(f"Completed {filename}")

        print("All migrations completed successfully.")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(run_migrations())