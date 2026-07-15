from __future__ import annotations

from asyncpg import Pool

from app.core.logger import logger
from app.sql import (
    UPDATE_CHUNK_EMBEDDING,
    SEMANTIC_TOP_K_RETRIEVAL,
    BM25_SEARCH,
)


class VectorRepository:
    """
    Repository responsible for vector storage and retrieval.

    Responsibilities
    ----------------
    - Store embeddings in pgvector
    - Semantic vector search
    - BM25 / PostgreSQL Full Text Search
    """

    def __init__(
        self,
        db_pool: Pool,
    ) -> None:
        self.pool = db_pool

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _format_vector(
        embedding: list[float],
    ) -> str:
        """
        Convert Python embedding list into pgvector format.
        """

        if not embedding:
            raise ValueError(
                "Embedding cannot be empty."
            )

        return "[" + ",".join(map(str, embedding)) + "]"

    # ==========================================================
    # Save Embedding
    # ==========================================================

    async def save_embedding(
        self,
        chunk_id: str,
        embedding: list[float],
    ) -> None:
        """
        Store embedding for a document chunk.
        """

        vector = self._format_vector(
            embedding
        )

        async with self.pool.acquire() as conn:

            await conn.execute(
                UPDATE_CHUNK_EMBEDDING,
                vector,
                chunk_id,
            )

        logger.debug(
            "Embedding stored for chunk %s",
            chunk_id,
        )

    # ==========================================================
    # Semantic Search
    # ==========================================================

    async def semantic_search(
        self,
        query_embedding: list[float],
        top_k: int = 20,
        document_id: str | None = None,
    ) -> list[dict]:
        """
        Perform semantic search using pgvector.
        """

        vector = self._format_vector(
            query_embedding
        )

        async with self.pool.acquire() as conn:

            rows = await conn.fetch(
                SEMANTIC_TOP_K_RETRIEVAL,
                vector,
                top_k,
                document_id,
            )

        logger.info(
            "Semantic search returned %d chunks.",
            len(rows),
        )

        return [dict(row) for row in rows]

    # ==========================================================
    # Backward Compatibility
    # ==========================================================

    async def search_top_k(
        self,
        embedding: list[float],
        top_k: int = 20,
        document_id: str | None = None,
    ) -> list[dict]:
        """
        Backward-compatible wrapper.

        Older services call search_top_k().
        Internally this delegates to semantic_search().
        """

        return await self.semantic_search(
            query_embedding=embedding,
            top_k=top_k,
            document_id=document_id,
        )

    # ==========================================================
    # BM25 Search
    # ==========================================================

    async def bm25_search(
        self,
        query: str,
        top_k: int = 20,
        document_id: str | None = None,
    ) -> list[dict]:
        """
        PostgreSQL Full-Text Search.
        """

        async with self.pool.acquire() as conn:

            rows = await conn.fetch(
                BM25_SEARCH,
                query,
                top_k,
                document_id,
            )

        logger.info(
            "BM25 search returned %d chunks.",
            len(rows),
        )

        return [dict(row) for row in rows]