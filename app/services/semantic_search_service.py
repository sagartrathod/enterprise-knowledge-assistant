from __future__ import annotations

from typing import Any

from app.core.constants import (
    LOG_RETRIEVAL,
    SEMANTIC_TOP_K,
)
from app.core.logger import logger
from app.repositories.vector_repository import VectorRepository
from app.services.embedding_service import EmbeddingService


class SemanticSearchService:
    """
    Enterprise Semantic Search Service.

    Responsibilities
    ----------------
    - Generate query embeddings.
    - Execute pgvector semantic retrieval.
    - Return chunks ranked by semantic similarity.
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
        top_k: int = SEMANTIC_TOP_K,
        document_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Execute semantic vector search.
        """

        logger.info("=" * 100)
        logger.info("SEMANTIC SEARCH")
        logger.info("=" * 100)
        logger.info("Question    : %s", question)
        logger.info("Document ID : %s", document_id)

        try:

            # ---------------------------------------------------------
            # Generate Query Embedding
            # ---------------------------------------------------------

            query_embedding = (
                await self.embedding_service.get_embedding(
                    question,
                )
            )

            logger.info("Query embedding generated successfully.")

            # ---------------------------------------------------------
            # Vector Search
            # ---------------------------------------------------------

            chunks = await self.vector_repo.search_top_k(
                embedding=query_embedding,
                question=question,
                top_k=top_k,
                document_id=document_id,
            )

            logger.info(
                "Retrieved %d semantic chunk(s).",
                len(chunks),
            )

            # ---------------------------------------------------------
            # Debug Ranking
            # ---------------------------------------------------------

            if LOG_RETRIEVAL:

                logger.info("=" * 100)
                logger.info("SEMANTIC SEARCH RANKING")
                logger.info("=" * 100)

                for index, chunk in enumerate(chunks, start=1):

                    logger.info(
                        (
                            "Rank=%02d | "
                            "Similarity=%.4f | "
                            "Keyword=%.4f | "
                            "Pages=%s-%s | "
                            "Chunk=%s | "
                            "Document=%s"
                        ),
                        index,
                        float(chunk.get("similarity", 0.0)),
                        float(chunk.get("keyword_score", 0.0)),
                        chunk.get("page_start"),
                        chunk.get("page_end"),
                        chunk.get("chunk_number"),
                        chunk.get("pdf_name"),
                    )

                if chunks:

                    best = chunks[0]

                    logger.info("=" * 100)
                    logger.info(
                        (
                            "PRIMARY SEMANTIC CHUNK | "
                            "Similarity=%.4f | "
                            "Keyword=%.4f | "
                            "Pages=%s-%s | "
                            "Chunk=%s | "
                            "Document=%s"
                        ),
                        float(best.get("similarity", 0.0)),
                        float(best.get("keyword_score", 0.0)),
                        best.get("page_start"),
                        best.get("page_end"),
                        best.get("chunk_number"),
                        best.get("pdf_name"),
                    )

                logger.info("=" * 100)

            return chunks

        except Exception:

            logger.exception(
                "Semantic search failed."
            )

            raise