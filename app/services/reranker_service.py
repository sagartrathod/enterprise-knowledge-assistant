from __future__ import annotations

from sentence_transformers import CrossEncoder

from app.core.constants import (
    RERANKER_MODEL,
    RERANK_TOP_K,
    SORT_BY_RERANK,
    LOG_RERANKING,
)
from app.core.logger import logger


class RerankerService:
    """
    Enterprise CrossEncoder Reranker.

    Responsibilities
    ----------------
    - Compute CrossEncoder relevance scores.
    - Attach rerank_score to every chunk.
    - Optionally reorder chunks by rerank score.
    """

    def __init__(
        self,
        model_name: str = RERANKER_MODEL,
    ) -> None:

        logger.info(
            "Loading CrossEncoder model: %s",
            model_name,
        )

        self.model = CrossEncoder(
            model_name,
            max_length=512,
        )

        logger.info(
            "CrossEncoder loaded successfully."
        )

    async def rerank(
        self,
        question: str,
        chunks: list[dict],
        top_k: int = RERANK_TOP_K,
    ) -> list[dict]:

        if not chunks:

            logger.info(
                "No chunks available for reranking."
            )

            return []

        logger.info("=" * 100)
        logger.info("CROSS ENCODER RERANKING")
        logger.info("=" * 100)

        logger.info(
            "Computing rerank scores for %d chunks.",
            len(chunks),
        )

        sentence_pairs = [
            (
                question,
                chunk["chunk_text"],
            )
            for chunk in chunks
        ]

        scores = self.model.predict(
            sentence_pairs,
            convert_to_numpy=True,
        )

        reranked: list[dict] = []

        for chunk, score in zip(chunks, scores):

            updated = chunk.copy()

            updated["rerank_score"] = float(score)

            reranked.append(updated)

        # ------------------------------------------------------
        # Sort by CrossEncoder score
        # ------------------------------------------------------

        if SORT_BY_RERANK:

            reranked.sort(
                key=lambda chunk: (
                    float(chunk.get("rerank_score", 0.0)),
                    float(chunk.get("similarity", 0.0)),
                    float(chunk.get("rrf_score", 0.0)),
                    -int(chunk.get("chunk_number", 999999)),
                ),
                reverse=True,
            )

        # ------------------------------------------------------
        # Logging
        # ------------------------------------------------------

        if LOG_RERANKING:

            logger.info("=" * 100)
            logger.info("CROSS ENCODER RANKING")
            logger.info("=" * 100)

            for index, chunk in enumerate(reranked, start=1):

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

            if reranked:

                best = reranked[0]

                logger.info(
                    (
                        "PRIMARY RERANKED CHUNK | "
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

        return reranked[:top_k]