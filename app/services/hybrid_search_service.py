from __future__ import annotations

from typing import Any

from app.core.constants import (
    HYBRID_TOP_K,
    RRF_K,
    SORT_BY_RERANK,
    SORT_BY_SIMILARITY,
    LOG_RETRIEVAL,
)
from app.core.logger import logger
from app.services.bm25_service import BM25SearchService
from app.services.semantic_search_service import (
    SemanticSearchService,
)


class HybridSearchService:
    """
    Enterprise Hybrid Search Service.

    Pipeline
    --------
        Semantic Search
               +
          BM25 Search
               ↓
      Reciprocal Rank Fusion
               ↓
         Final Hybrid Ranking

    Final Ranking Priority
    ----------------------
    If SORT_BY_RERANK:

        1. Rerank Score
        2. Semantic Similarity
        3. RRF Score
        4. Chunk Number

    Else If SORT_BY_SIMILARITY:

        1. Semantic Similarity
        2. RRF Score
        3. Chunk Number

    Else:

        1. RRF Score
        2. Semantic Similarity
        3. Chunk Number
    """

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
        top_k: int = HYBRID_TOP_K,
        document_id: str | None = None,
    ) -> list[dict[str, Any]]:

        logger.info("=" * 100)
        logger.info("HYBRID SEARCH")
        logger.info("=" * 100)
        logger.info("Question : %s", question)

        # ---------------------------------------------------------
        # Semantic Search
        # ---------------------------------------------------------

        semantic_results = await self.semantic_service.search(
            question=question,
            top_k=top_k,
            document_id=document_id,
        )

        # ---------------------------------------------------------
        # BM25 Search
        # ---------------------------------------------------------

        bm25_results = await self.bm25_service.search(
            question=question,
            top_k=top_k,
            document_id=document_id,
        )

        merged: dict[str, dict[str, Any]] = {}

        # ---------------------------------------------------------
        # Merge Semantic Results
        # ---------------------------------------------------------

        for rank, chunk in enumerate(semantic_results, start=1):

            chunk_id = str(chunk["chunk_id"])

            if chunk_id not in merged:

                merged[chunk_id] = chunk.copy()
                merged[chunk_id]["rrf_score"] = 0.0

            merged[chunk_id]["rrf_score"] += (
                1.0 / (RRF_K + rank)
            )

        # ---------------------------------------------------------
        # Merge BM25 Results
        # ---------------------------------------------------------

        for rank, chunk in enumerate(bm25_results, start=1):

            chunk_id = str(chunk["chunk_id"])

            if chunk_id not in merged:

                merged[chunk_id] = chunk.copy()
                merged[chunk_id]["rrf_score"] = 0.0

            merged[chunk_id]["rrf_score"] += (
                1.0 / (RRF_K + rank)
            )

        # ---------------------------------------------------------
        # Final Ranking
        # ---------------------------------------------------------

        if SORT_BY_RERANK:

            results = sorted(
                merged.values(),
                key=lambda chunk: (
                    float(chunk.get("rerank_score", 0.0)),
                    float(chunk.get("similarity", 0.0)),
                    float(chunk.get("rrf_score", 0.0)),
                    -int(chunk.get("chunk_number", 999999)),
                ),
                reverse=True,
            )

        elif SORT_BY_SIMILARITY:

            results = sorted(
                merged.values(),
                key=lambda chunk: (
                    float(chunk.get("similarity", 0.0)),
                    float(chunk.get("rrf_score", 0.0)),
                    -int(chunk.get("chunk_number", 999999)),
                ),
                reverse=True,
            )

        else:

            results = sorted(
                merged.values(),
                key=lambda chunk: (
                    float(chunk.get("rrf_score", 0.0)),
                    float(chunk.get("similarity", 0.0)),
                    -int(chunk.get("chunk_number", 999999)),
                ),
                reverse=True,
            )

        logger.info(
            "Hybrid search merged %d unique chunks.",
            len(results),
        )

        # ---------------------------------------------------------
        # Debug Ranking
        # ---------------------------------------------------------

        if LOG_RETRIEVAL:

            logger.info("=" * 100)
            logger.info("FINAL HYBRID SEARCH RANKING")
            logger.info("=" * 100)

            for index, chunk in enumerate(results, start=1):

                logger.info(
                    (
                        "Rank=%02d | "
                        "Rerank=%.4f | "
                        "Similarity=%.4f | "
                        "RRF=%.4f | "
                        "Keyword=%.4f | "
                        "Page=%s | "
                        "Chunk=%s | "
                        "Document=%s"
                    ),
                    index,
                    float(chunk.get("rerank_score", 0.0)),
                    float(chunk.get("similarity", 0.0)),
                    float(chunk.get("rrf_score", 0.0)),
                    float(chunk.get("keyword_score", 0.0)),
                    chunk.get("page_number"),
                    chunk.get("chunk_number"),
                    chunk.get("pdf_name"),
                )

            logger.info("=" * 100)

            if results:

                best = results[0]

                logger.info(
                    (
                        "PRIMARY HYBRID CHUNK | "
                        "Rerank=%.4f | "
                        "Similarity=%.4f | "
                        "RRF=%.4f | "
                        "Keyword=%.4f | "
                        "Page=%s | "
                        "Chunk=%s | "
                        "Document=%s"
                    ),
                    float(best.get("rerank_score", 0.0)),
                    float(best.get("similarity", 0.0)),
                    float(best.get("rrf_score", 0.0)),
                    float(best.get("keyword_score", 0.0)),
                    best.get("page_number"),
                    best.get("chunk_number"),
                    best.get("pdf_name"),
                )

            logger.info("=" * 100)

        return results[:top_k]