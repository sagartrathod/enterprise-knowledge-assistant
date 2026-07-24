from asyncpg import Pool

from app.sql import (
    INSERT_CHUNK_METADATA,
    GET_CHUNKS_BY_DOCUMENT,
)


class ChunkRepository:

    def __init__(
        self,
        db_pool: Pool,
    ):
        self.pool = db_pool

    def _format_vector(
        self,
        embedding: list[float],
    ) -> str:

        return "[" + ",".join(
            str(x)
            for x in embedding
        ) + "]"

    async def save_chunk_metadata(
        self,
        document_id: str,
        chunk_number: int,
        page_start: int,
        page_end: int,
        line_start: int,
        line_end: int,
        chunk_text: str,
        embedding: list[float],
    ) -> str:

        vector_string = self._format_vector(
            embedding
        )

        async with self.pool.acquire() as conn:

            chunk_id = await conn.fetchval(
                INSERT_CHUNK_METADATA,
                document_id,
                chunk_number,
                page_start,
                page_end,
                line_start,
                line_end,
                chunk_text,
                vector_string,
            )

        return str(chunk_id)

    async def get_by_document_id(
        self,
        document_id: str,
    ) -> list[dict]:

        async with self.pool.acquire() as conn:

            rows = await conn.fetch(
                GET_CHUNKS_BY_DOCUMENT,
                document_id,
            )

        return [
            dict(row)
            for row in rows
        ]