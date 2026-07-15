from __future__ import annotations

from typing import Any

from app.core.logger import logger
from app.repositories.vector_repository import VectorRepository


class BM25SearchService:
    """
    Performs PostgreSQL Full-Text Search.
    """

    def __init__(
        self,
        vector_repo: VectorRepository,
    ) -> None:

        self.vector_repo = vector_repo

    async def search(
        self,
        question: str,
        top_k: int = 20,
        document_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Execute BM25/FTS search.
        """

        logger.info("Running BM25 search.")

        chunks = await self.vector_repo.bm25_search(
            query=question,
            top_k=top_k,
            document_id=document_id,
        )

        logger.info(
            "BM25 search returned %d chunks.",
            len(chunks),
        )

        return chunks