# app/services/retrieval_service.py

from __future__ import annotations

from typing import Any

from app.core.logger import logger
from app.repositories.vector_repository import VectorRepository
from app.services.embedding_service import EmbeddingService


class RetrievalService:
    """
    Enterprise Retrieval Service.

    Responsibilities:
    - Generate query embeddings.
    - Perform semantic search.
    - Merge retrieval results.
    - Remove duplicate chunks.
    - Sort by similarity.
    - Return Top-K candidate chunks.

    Future Extensions:
    - BM25 retrieval
    - Hybrid search
    - Metadata filtering
    - Reciprocal Rank Fusion (RRF)
    """

    def __init__(
        self,
        vector_repo: VectorRepository,
        embedding_service: EmbeddingService,
    ) -> None:

        self.vector_repo = vector_repo
        self.embedding_service = embedding_service

    async def retrieve(
        self,
        question: str,
        top_k: int = 10,
        document_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve relevant document chunks.

        Args:
            question:
                User question.

            top_k:
                Maximum number of chunks to return.

            document_id:
                Optional document filter.

        Returns:
            Ranked list of candidate chunks.
        """

        logger.info(
            "Retrieving context | top_k=%d | document_id=%s",
            top_k,
            document_id,
        )

        # ---------------------------------------------------------
        # Step 1: Generate query embedding
        # ---------------------------------------------------------

        query_embedding = await self.embedding_service.get_embedding(
            question
        )

        # ---------------------------------------------------------
        # Step 2: Semantic search
        # ---------------------------------------------------------

        semantic_chunks = await self.vector_repo.search_top_k(
            query_embedding=query_embedding,
            top_k=top_k,
            document_id=document_id,
        )

        logger.info(
            "Semantic search returned %d chunks.",
            len(semantic_chunks),
        )

        # ---------------------------------------------------------
        # Step 3:
        # Placeholder for future BM25 retrieval.
        #
        # bm25_chunks = ...
        #
        # merged_chunks = semantic_chunks + bm25_chunks
        # ---------------------------------------------------------

        merged_chunks = semantic_chunks

        # ---------------------------------------------------------
        # Step 4: Remove duplicates
        # ---------------------------------------------------------

        merged_chunks = self._remove_duplicates(
            merged_chunks
        )

        # ---------------------------------------------------------
        # Step 5: Sort by similarity
        # ---------------------------------------------------------

        merged_chunks.sort(
            key=lambda chunk: chunk.get(
                "similarity",
                0.0,
            ),
            reverse=True,
        )

        logger.info(
            "Returning %d retrieved chunks.",
            len(merged_chunks),
        )

        return merged_chunks[:top_k]

    def _remove_duplicates(
        self,
        chunks: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Remove duplicate chunks.

        Uses chunk_id when available.
        """

        unique_chunks = {}
        results = []

        for chunk in chunks:

            chunk_id = chunk.get("chunk_id")

            if chunk_id is None:

                key = (
                    chunk.get("document_id"),
                    chunk.get("page_number"),
                    chunk.get("chunk_number"),
                )

            else:

                key = chunk_id

            if key in unique_chunks:
                continue

            unique_chunks[key] = True
            results.append(chunk)

        return results

