from __future__ import annotations

from typing import Any

from app.core.logger import logger
from app.services.semantic_search_service import (
    SemanticSearchService,
)
from app.services.bm25_service import (
    BM25SearchService,
)


class HybridSearchService:
    """
    Hybrid Search using Reciprocal Rank Fusion (RRF).

    Combines:
    - Semantic Search
    - BM25 Search
    """

    RRF_K = 60

    def __init__(
        self,
        semantic_service: SemanticSearchService,
        bm25_service: BM25SearchService,
    ) -> None:

        self.semantic_service = semantic_service
        self.bm25_service = bm25_service

    async def search(
        self,
        question: str,
        top_k: int = 20,
        document_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Execute hybrid retrieval.
        """

        semantic_results = await self.semantic_service.search(
            question=question,
            top_k=top_k,
            document_id=document_id,
        )

        bm25_results = await self.bm25_service.search(
            question=question,
            top_k=top_k,
            document_id=document_id,
        )

        merged: dict[str, dict[str, Any]] = {}

        #
        # Semantic Ranking
        #
        for rank, chunk in enumerate(semantic_results, start=1):

            chunk_id = str(chunk["chunk_id"])

            score = 1 / (self.RRF_K + rank)

            if chunk_id not in merged:

                merged[chunk_id] = chunk.copy()

                merged[chunk_id]["rrf_score"] = 0.0

            merged[chunk_id]["rrf_score"] += score

        #
        # BM25 Ranking
        #
        for rank, chunk in enumerate(bm25_results, start=1):

            chunk_id = str(chunk["chunk_id"])

            score = 1 / (self.RRF_K + rank)

            if chunk_id not in merged:

                merged[chunk_id] = chunk.copy()

                merged[chunk_id]["rrf_score"] = 0.0

            merged[chunk_id]["rrf_score"] += score

        results = sorted(
            merged.values(),
            key=lambda item: item["rrf_score"],
            reverse=True,
        )

        logger.info(
            "Hybrid search returned %d merged chunks.",
            len(results),
        )

        return results[:top_k]