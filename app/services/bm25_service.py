from __future__ import annotations

from typing import Any

from app.core.constants import BM25_TOP_K
from app.core.logger import logger
from app.repositories.vector_repository import VectorRepository


class BM25SearchService:
    """
    Enterprise BM25 Search Service.

    Responsibilities
    ----------------
    - Execute PostgreSQL Full Text Search.
    - Return chunks ranked by BM25 score.
    """

    def __init__(
        self,
        vector_repo: VectorRepository,
    ) -> None:

        self.vector_repo = vector_repo

    async def search(
        self,
        question: str,
        top_k: int = BM25_TOP_K,
        document_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Execute PostgreSQL Full-Text Search.
        """

        logger.info("=" * 80)
        logger.info("BM25 SEARCH")
        logger.info("=" * 80)
        logger.info("Question: %s", question)

        chunks = await self.vector_repo.bm25_search(
            query=question,
            top_k=top_k,
            document_id=document_id,
        )

        logger.info(
            "BM25 search returned %d chunks.",
            len(chunks),
        )

        logger.info("=" * 80)
        logger.info("BM25 SEARCH RANKING")
        logger.info("=" * 80)

        for index, chunk in enumerate(chunks, start=1):

            logger.info(
                (
                    "Rank=%02d | "
                    "BM25=%.4f | "
                    "Page=%s | "
                    "Chunk=%s"
                ),
                index,
                float(chunk.get("bm25_score", 0.0)),
                chunk.get("page_number"),
                chunk.get("chunk_number"),
            )

        if chunks:

            best = chunks[0]

            logger.info("=" * 80)
            logger.info(
                (
                    "PRIMARY BM25 CHUNK | "
                    "Score=%.4f | "
                    "Page=%s | "
                    "Chunk=%s"
                ),
                float(best.get("bm25_score", 0.0)),
                best.get("page_number"),
                best.get("chunk_number"),
            )

        return chunks