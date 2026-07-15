from __future__ import annotations

from typing import Any

from app.core.logger import logger
from app.repositories.vector_repository import VectorRepository
from app.services.embedding_service import EmbeddingService


class SemanticSearchService:
    """
    Enterprise Semantic Search Service.

    Responsibilities
    ----------------
    - Generate query embeddings.
    - Perform pgvector similarity search.
    """

    def __init__(
        self,
        vector_repo: VectorRepository,
        embedding_service: EmbeddingService,
    ) -> None:
        self.vector_repo = vector_repo
        self.embedding_service = embedding_service

    async def search(
        self,
        question: str,
        top_k: int = 20,
        document_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Perform semantic vector search.

        Args:
            question: User query.
            top_k: Number of chunks to retrieve.
            document_id: Optional document filter.

        Returns:
            List of retrieved chunks ordered by similarity.
        """

        logger.info("Running semantic search.")

        # Generate embedding for the query
        query_embedding = await self.embedding_service.get_embedding(
            question
        )

        # Perform pgvector search
        chunks = await self.vector_repo.search_top_k(
            embedding=query_embedding,
            top_k=top_k,
            document_id=document_id,
        )

        logger.info(
            "Semantic search returned %d chunks.",
            len(chunks),
        )

        return chunks