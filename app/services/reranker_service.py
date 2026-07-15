from __future__ import annotations

from sentence_transformers import CrossEncoder

from app.core.logger import logger


class RerankerService:
    """
    Cross-Encoder based reranker.

    Responsibilities
    ----------------
    - Re-score retrieved chunks.
    - Improve retrieval precision.
    - Return the highest ranked chunks.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-base",
    ) -> None:

        logger.info(
            "Loading reranker model: %s",
            model_name,
        )

        self.model = CrossEncoder(
            model_name,
            max_length=512,
        )

        logger.info("Reranker loaded successfully.")

    async def rerank(
        self,
        question: str,
        chunks: list[dict],
        top_k: int = 5,
    ) -> list[dict]:
        """
        Re-rank retrieved chunks.

        Args:
            question:
                User question.

            chunks:
                Retrieved chunks.

            top_k:
                Number of chunks to return.

        Returns:
            Top reranked chunks.
        """

        if not chunks:
            return []

        logger.info(
            "Reranking %d retrieved chunks.",
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

        reranked = []

        for chunk, score in zip(chunks, scores):

            updated_chunk = chunk.copy()

            updated_chunk["rerank_score"] = float(score)

            reranked.append(updated_chunk)

        reranked.sort(
            key=lambda x: x["rerank_score"],
            reverse=True,
        )

        logger.info(
            "Returning top %d reranked chunks.",
            min(top_k, len(reranked)),
        )

        return reranked[:top_k]