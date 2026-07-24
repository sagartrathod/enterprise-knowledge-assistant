from __future__ import annotations

import time

from app.core.config import settings
from app.core.constants import (
    DEFAULT_NO_ANSWER,
    LOG_PROMPT,
)
from app.core.logger import logger
from app.llm.groq import GroqClient
from app.services.prompt_service import PromptService


class LLMService:
    """
    Enterprise LLM Service.

    Responsibilities
    ----------------
    - Validate LLM configuration.
    - Build prompts.
    - Invoke the configured LLM.
    - Return grounded answers.
    """

    def __init__(
        self,
        prompt_service: PromptService,
    ) -> None:

        if not settings.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is missing."
            )

        self.prompt_service = prompt_service

        self.engine = GroqClient()

        logger.info(
            "LLM Service initialized successfully."
        )

    async def generate_response(
        self,
        context_chunks: list[dict],
        question: str,
    ) -> str:
        """
        Generate grounded response.
        """

        logger.info("=" * 100)
        logger.info("LLM GENERATION")
        logger.info("=" * 100)

        logger.info(
            "Question: %s",
            question,
        )

        logger.info(
            "Context Chunks: %d",
            len(context_chunks),
        )

        if not context_chunks:

            logger.warning(
                "No context chunks supplied."
            )

            return DEFAULT_NO_ANSWER

        # -----------------------------------------------------
        # Build Prompt
        # -----------------------------------------------------

        system_prompt, user_prompt = (
            self.prompt_service.build(
                context_chunks=context_chunks,
                question=question,
            )
        )

        logger.info(
            "Prompt generated successfully."
        )

        logger.info(
            "System Prompt Length : %d",
            len(system_prompt),
        )

        logger.info(
            "User Prompt Length : %d",
            len(user_prompt),
        )

        logger.info(
            "Total Prompt Length : %d",
            len(system_prompt) + len(user_prompt),
        )

        if LOG_PROMPT:

            logger.debug("=" * 100)
            logger.debug("SYSTEM PROMPT")
            logger.debug("=" * 100)
            logger.debug(system_prompt)

            logger.debug("=" * 100)
            logger.debug("USER PROMPT")
            logger.debug("=" * 100)
            logger.debug(user_prompt)

        # -----------------------------------------------------
        # LLM Call
        # -----------------------------------------------------

        start = time.perf_counter()

        try:

            answer = await self.engine.generate_answer(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )

        except Exception:

            logger.exception(
                "LLM generation failed."
            )

            raise

        elapsed = time.perf_counter() - start

        logger.info(
            "LLM execution time: %.2f sec",
            elapsed,
        )

        # -----------------------------------------------------
        # Validate Response
        # -----------------------------------------------------

        if answer is None:

            logger.warning(
                "LLM returned None."
            )

            return DEFAULT_NO_ANSWER

        answer = answer.strip()

        if not answer:

            logger.warning(
                "LLM returned empty response."
            )

            return DEFAULT_NO_ANSWER

        logger.info(
            "Answer Length: %d characters",
            len(answer),
        )

        logger.info("=" * 100)
        logger.info("LLM RESPONSE")
        logger.info("=" * 100)

        logger.info("%s", answer)

        logger.info("=" * 100)

        return answer