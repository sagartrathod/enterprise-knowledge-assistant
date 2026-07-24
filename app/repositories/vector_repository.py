from __future__ import annotations

from asyncpg import Pool

from app.core.logger import logger
from app.sql import (
    BM25_SEARCH,
    SEMANTIC_TOP_K_RETRIEVAL,
    UPDATE_CHUNK_EMBEDDING,
)


class VectorRepository:
    """
    Repository responsible for vector storage and retrieval.

    Responsibilities
    ----------------
    - Store embeddings
    - Semantic vector search
    - PostgreSQL Full Text Search
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
        Convert Python embedding into pgvector format.
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
        Save embedding into pgvector column.
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
        question: str,
        top_k: int,
        document_id: str | None = None,
    ) -> list[dict]:
        """
        Semantic vector retrieval.

        SQL already returns results ordered by similarity.
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
                question,
            )

        results: list[dict] = []

        for row in rows:

            chunk = dict(row)

            chunk["distance"] = float(
                chunk.get("distance", 0.0)
            )

            chunk["similarity"] = float(
                chunk.get("similarity", 0.0)
            )

            chunk["keyword_score"] = float(
                chunk.get("keyword_score", 0.0)
            )

            results.append(chunk)

        logger.info(
            "Semantic search returned %d chunks.",
            len(results),
        )

        if results:

            logger.info(
                "Top Semantic Chunk | Similarity=%.4f | "
                "Keyword=%.4f | Pages=%s-%s | Chunk=%s",
                results[0]["similarity"],
                results[0]["keyword_score"],
                results[0]["page_start"],
                results[0]["page_end"],
                results[0]["chunk_number"],
            )
        return results

    # ==========================================================
    # Backward Compatibility
    # ==========================================================

    async def search_top_k(
        self,
        embedding: list[float],
        question: str,
        top_k: int,
        document_id: str | None = None,
    ) -> list[dict]:
        """
        Wrapper for semantic search.
        """

        return await self.semantic_search(
            query_embedding=embedding,
            question=question,
            top_k=top_k,
            document_id=document_id,
        )

    # ==========================================================
    # BM25 Search
    # ==========================================================

    async def bm25_search(
        self,
        query: str,
        top_k: int,
        document_id: str | None = None,
    ) -> list[dict]:
        """
        PostgreSQL Full Text Search.
        """

        async with self.pool.acquire() as conn:

            rows = await conn.fetch(
                BM25_SEARCH,
                query,
                top_k,
                document_id,
            )

        results = []

        for row in rows:

            chunk = dict(row)

            chunk["bm25_score"] = float(
                chunk.get("bm25_score", 0.0)
            )

            results.append(chunk)

        logger.info(
            "BM25 search returned %d chunks.",
            len(results),
        )

        if results:

            logger.info(
                "Top BM25 Chunk | Score=%.4f | "
                "Pages=%s-%s | Chunk=%s",
                results[0]["bm25_score"],
                results[0]["page_start"],
                results[0]["page_end"],
                results[0]["chunk_number"],
            )

        return results