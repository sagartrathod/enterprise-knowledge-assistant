from __future__ import annotations

from app.core.logger import logger
from app.llm.prompt import (
    SYSTEM_PROMPT,
    build_user_prompt,
)


class PromptService:
    """
    Enterprise Prompt Service.

    Responsibilities
    ----------------
    - Provide the system prompt.
    - Build the complete prompt.
    - Keep prompt engineering centralized.
    - Remain provider agnostic.
    """

    def __init__(self) -> None:

        self.system_prompt = SYSTEM_PROMPT

        logger.info(
            "PromptService initialized successfully."
        )

    # ==========================================================
    # Build Complete Prompt
    # ==========================================================

    def build(
        self,
        context_chunks: list[dict],
        question: str,
    ) -> tuple[str, str]:
        """
        Build the prompts used by the LLM.

        Returns
        -------
        (
            system_prompt,
            user_prompt
        )
        """

        logger.info("=" * 100)
        logger.info("PROMPT GENERATION")
        logger.info("=" * 100)

        logger.info(
            "Question: %s",
            question,
        )

        logger.info(
            "Retrieved Context Chunks: %d",
            len(context_chunks),
        )

        if not context_chunks:

            logger.warning(
                "Prompt requested with empty context."
            )

        user_prompt = build_user_prompt(
            context_chunks=context_chunks,
            user_query=question,
        )

        logger.info(
            "Prompt generated successfully."
        )

        logger.info(
            "System Prompt Length : %d chars",
            len(self.system_prompt),
        )

        logger.info(
            "User Prompt Length : %d chars",
            len(user_prompt),
        )

        logger.info(
            "Total Prompt Length : %d chars",
            len(self.system_prompt)
            + len(user_prompt),
        )

        logger.debug("=" * 100)
        logger.debug("SYSTEM PROMPT")
        logger.debug("=" * 100)
        logger.debug(self.system_prompt)

        logger.debug("=" * 100)
        logger.debug("USER PROMPT")
        logger.debug("=" * 100)
        logger.debug(user_prompt)

        logger.debug("=" * 100)

        return (
            self.system_prompt,
            user_prompt,
        )

    # ==========================================================
    # Get System Prompt
    # ==========================================================

    def get_system_prompt(
        self,
    ) -> str:
        """
        Return the system prompt.
        """

        return self.system_prompt

    # ==========================================================
    # Get User Prompt
    # ==========================================================

    def get_user_prompt(
        self,
        context_chunks: list[dict],
        question: str,
    ) -> str:
        """
        Build only the user prompt.

        Useful for testing or debugging.
        """

        return build_user_prompt(
            context_chunks=context_chunks,
            user_query=question,
        )

    # ==========================================================
    # Prompt Statistics
    # ==========================================================

    def prompt_stats(
        self,
        context_chunks: list[dict],
        question: str,
    ) -> dict:
        """
        Return prompt statistics.

        Useful for debugging token usage.
        """

        user_prompt = build_user_prompt(
            context_chunks=context_chunks,
            user_query=question,
        )

        return {
            "system_prompt_length": len(
                self.system_prompt
            ),
            "user_prompt_length": len(
                user_prompt
            ),
            "total_prompt_length": len(
                self.system_prompt
            )
            + len(user_prompt),
            "chunk_count": len(
                context_chunks
            ),
        }