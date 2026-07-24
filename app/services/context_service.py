from __future__ import annotations

from typing import Any

from app.core.constants import (
    FINAL_TOP_K,
    SIMILARITY_THRESHOLD,
    REMOVE_DUPLICATE_CHUNKS,
    LOG_FINAL_CONTEXT,
    LOG_PRIMARY_CHUNK,
)
from app.core.logger import logger
from app.llm.prompt import format_context


class ContextService:
    """
    Enterprise Context Service.

    Responsibilities
    ----------------
    - Remove duplicate chunks.
    - Remove weak similarity chunks.
    - Preserve CrossEncoder ranking.
    - Keep Top-K chunks.
    - Build LLM-ready context.

    Notes
    -----
    Chunks are already ranked by RerankerService.

    ContextService NEVER changes that order.
    """

    def __init__(
        self,
        similarity_threshold: float = SIMILARITY_THRESHOLD,
        max_context_chunks: int = FINAL_TOP_K,
    ) -> None:

        self.similarity_threshold = similarity_threshold
        self.max_context_chunks = max_context_chunks

    def prepare_context(
        self,
        retrieved_chunks: list[dict[str, Any]],
    ) -> tuple[str, list[dict[str, Any]]]:

        logger.info("=" * 100)
        logger.info("CONTEXT PREPARATION")
        logger.info("=" * 100)

        logger.info(
            "Preparing context from %d retrieved chunks.",
            len(retrieved_chunks),
        )

        if not retrieved_chunks:
            return "", []

        # --------------------------------------------------
        # Remove duplicates
        # --------------------------------------------------

        if REMOVE_DUPLICATE_CHUNKS:

            chunks = self._remove_duplicates(
                retrieved_chunks
            )

        else:

            chunks = retrieved_chunks

        # --------------------------------------------------
        # Similarity filtering
        # --------------------------------------------------

        chunks = self._filter_similarity(
            chunks
        )

        if not chunks:

            logger.info(
                "No chunks remained after similarity filtering."
            )

            return "", []

        # --------------------------------------------------
        # IMPORTANT
        #
        # Do NOT sort again.
        #
        # RerankerService already produced the final ranking.
        # Preserve that ordering.
        # --------------------------------------------------

        logger.info(
            "Preserving CrossEncoder ranking."
        )

        # --------------------------------------------------
        # Keep Top-K
        # --------------------------------------------------

        chunks = chunks[: self.max_context_chunks]

        logger.info(
            "Selected %d chunks for context.",
            len(chunks),
        )

        # --------------------------------------------------
        # Debug
        # --------------------------------------------------

        if LOG_FINAL_CONTEXT:

            logger.info("=" * 100)
            logger.info("FINAL CONTEXT")
            logger.info("=" * 100)

            for index, chunk in enumerate(chunks, start=1):

                logger.info(
                    (
                        "Rank=%02d | "
                        "Rerank=%.4f | "
                        "Similarity=%.4f | "
                        "Keyword=%.4f | "
                        "RRF=%.4f | "
                        "Pages=%s-%s | "
                        "Chunk=%s | "
                        "Document=%s"
                    ),
                    index,
                    float(chunk.get("rerank_score", 0.0)),
                    float(chunk.get("similarity", 0.0)),
                    float(chunk.get("keyword_score", 0.0)),
                    float(chunk.get("rrf_score", 0.0)),
                    chunk.get("page_start"),
                    chunk.get("page_end"),
                    chunk.get("chunk_number"),
                    chunk.get("pdf_name"),
                )

            logger.info("=" * 100)

        if LOG_PRIMARY_CHUNK and chunks:

            primary = chunks[0]

            logger.info(
                (
                    "PRIMARY CONTEXT CHUNK | "
                    "Rerank=%.4f | "
                    "Similarity=%.4f | "
                    "Keyword=%.4f | "
                    "RRF=%.4f | "
                    "Pages=%s-%s | "
                    "Chunk=%s | "
                    "Document=%s"
                ),
                float(primary.get("rerank_score", 0.0)),
                float(primary.get("similarity", 0.0)),
                float(primary.get("keyword_score", 0.0)),
                float(primary.get("rrf_score", 0.0)),
                primary.get("page_start"),
                primary.get("page_end"),
                primary.get("chunk_number"),
                primary.get("pdf_name"),
            )

            logger.info("=" * 100)

        context = format_context(chunks)

        return context, chunks

    def _filter_similarity(
        self,
        chunks: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        filtered = [
            chunk
            for chunk in chunks
            if float(chunk.get("similarity", 0.0))
            >= self.similarity_threshold
        ]

        logger.info(
            "Similarity filter kept %d/%d chunks.",
            len(filtered),
            len(chunks),
        )

        return filtered

    def _remove_duplicates(
        self,
        chunks: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        seen = set()

        unique = []

        for chunk in chunks:

            key = chunk.get("chunk_id")

            if key is None:

                key = (
                    chunk.get("document_id"),
                    chunk.get("page_start"),
                    chunk.get("page_end"),
                    chunk.get("chunk_number"),
                )

            if key in seen:
                continue

            seen.add(key)

            unique.append(chunk)

        logger.info(
            "Removed duplicates. Remaining=%d",
            len(unique),
        )

        return unique

    from typing import Any


    def calculate_confidence(
        self,
        chunks: list[dict[str, Any]],
    ) -> float:
        """
        Calculate overall answer confidence.

        Uses

        • Vector similarity
        • CrossEncoder rerank score
        • BM25 keyword score
        • Number of supporting chunks

        Returns
        -------
        float
            Confidence percentage (0-100)
        """

        if not chunks:
            return 0.0

        similarities = [
            max(0.0, min(1.0, float(c.get("similarity", 0.0))))
            for c in chunks
        ]

        reranks = [
            max(0.0, min(1.0, float(c.get("rerank_score", 0.0))))
            for c in chunks
        ]

        keywords = [
            max(0.0, min(1.0, float(c.get("keyword_score", 0.0))))
            for c in chunks
        ]

        avg_similarity = sum(similarities) / len(similarities)
        avg_rerank = sum(reranks) / len(reranks)
        avg_keyword = sum(keywords) / len(keywords)

        chunk_bonus = min(len(chunks), 5) / 5

        confidence = (
            avg_similarity * 0.40 +
            avg_rerank * 0.40 +
            avg_keyword * 0.15 +
            chunk_bonus * 0.05
        )

        confidence = max(0.0, min(1.0, confidence))

        return round(confidence * 100, 2)