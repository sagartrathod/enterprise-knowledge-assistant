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
    - Build the complete user prompt.
    - Provide the system prompt.
    - Centralize prompt engineering.
    - Keep LLMService model-agnostic.
    """

    def __init__(self):
        self.system_prompt = SYSTEM_PROMPT

    def build(
        self,
        context_chunks: list[dict],
        question: str,
    ) -> tuple[str, str]:
        """
        Build prompts for the LLM.

        Returns
        -------
        (
            system_prompt,
            user_prompt
        )
        """

        logger.info(
            "Building prompt using %d retrieved chunks.",
            len(context_chunks),
        )

        user_prompt = build_user_prompt(
            context_chunks=context_chunks,
            user_query=question,
        )

        logger.debug(
            "User prompt length: %d characters",
            len(user_prompt),
        )

        return (
            self.system_prompt,
            user_prompt,
        )

    def get_system_prompt(self) -> str:
        """
        Return the system prompt.
        """

        return self.system_prompt

    def get_user_prompt(
        self,
        context_chunks: list[dict],
        question: str,
    ) -> str:
        """
        Return only the user prompt.

        Useful for testing/debugging.
        """

        return build_user_prompt(
            context_chunks=context_chunks,
            user_query=question,
        )