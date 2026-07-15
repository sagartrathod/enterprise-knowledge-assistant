from __future__ import annotations

from typing import Any

from app.core.logger import logger
from app.llm.prompt import format_context


class ContextService:
    """
    Enterprise Context Service.

    Responsibilities
    ----------------
    - Filter low-quality chunks.
    - Sort chunks by similarity.
    - Remove duplicate chunks.
    - Limit context size.
    - Build LLM-ready context.
    """

    DEFAULT_SIMILARITY_THRESHOLD = 0.20

    DEFAULT_MAX_CONTEXT_CHUNKS = 8

    def __init__(
        self,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
        max_context_chunks: int = DEFAULT_MAX_CONTEXT_CHUNKS,
    ):

        self.similarity_threshold = similarity_threshold
        self.max_context_chunks = max_context_chunks

    def prepare_context(
        self,
        retrieved_chunks: list[dict[str, Any]],
    ) -> tuple[str, list[dict[str, Any]]]:
        """
        Prepare context for the LLM.

        Returns
        -------
        (
            formatted_context,
            filtered_chunks
        )
        """

        logger.info(
            "Preparing context from %d retrieved chunks.",
            len(retrieved_chunks),
        )

        if not retrieved_chunks:
            return "", []

        # --------------------------------------------------------
        # Step 1
        # Remove duplicates
        # --------------------------------------------------------

        chunks = self._remove_duplicates(
            retrieved_chunks
        )

        # --------------------------------------------------------
        # Step 2
        # Filter low similarity
        # --------------------------------------------------------

        chunks = self._filter_similarity(
            chunks
        )

        # --------------------------------------------------------
        # Step 3
        # Sort by similarity
        # --------------------------------------------------------

        chunks.sort(
            key=lambda x: x.get(
                "similarity",
                0.0,
            ),
            reverse=True,
        )

        # --------------------------------------------------------
        # Step 4
        # Limit context size
        # --------------------------------------------------------

        chunks = chunks[
            : self.max_context_chunks
        ]

        logger.info(
            "Selected %d chunks for prompt.",
            len(chunks),
        )

        context = format_context(
            chunks
        )

        return context, chunks

    def _filter_similarity(
        self,
        chunks: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Remove low similarity chunks.
        """

        filtered = []

        for chunk in chunks:

            similarity = chunk.get(
                "similarity",
                0.0,
            )

            if (
                similarity
                >= self.similarity_threshold
            ):
                filtered.append(chunk)

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
        """
        Remove duplicate chunks.
        """

        seen = set()

        unique = []

        for chunk in chunks:

            key = chunk.get(
                "chunk_id"
            )

            if key is None:

                key = (
                    chunk.get(
                        "document_id"
                    ),
                    chunk.get(
                        "page_number"
                    ),
                    chunk.get(
                        "chunk_number"
                    ),
                )

            if key in seen:
                continue

            seen.add(key)

            unique.append(chunk)

        logger.info(
            "Removed duplicates. Remaining chunks=%d",
            len(unique),
        )

        return unique