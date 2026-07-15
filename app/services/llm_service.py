# app/services/llm_service.py

from __future__ import annotations

from app.core.config import settings
from app.core.logger import logger
from app.llm.groq import GroqClient
from app.services.prompt_service import PromptService


class LLMService:
    """
    Enterprise LLM Service.

    Responsibilities
    ----------------
    - Validate LLM configuration.
    - Build prompts using PromptService.
    - Call the configured LLM provider.
    - Return grounded responses.

    This service is provider-agnostic. Prompt construction and model
    invocation are delegated to dedicated components.
    """

    def __init__(
        self,
        prompt_service: PromptService,
    ) -> None:
        """
        Initialize the LLM service.

        Args:
            prompt_service:
                Service responsible for prompt construction.
        """

        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is missing.")

        self.prompt_service = prompt_service
        self.engine = GroqClient()

    async def generate_response(
        self,
        context_chunks: list[dict],
        question: str,
    ) -> str:
        """
        Generate a grounded answer from retrieved document chunks.

        Args:
            context_chunks:
                Retrieved chunks selected for the prompt.

            question:
                User question.

        Returns:
            Generated answer from the LLM.
        """

        logger.info(
            "Generating LLM response using %d context chunks.",
            len(context_chunks),
        )

        system_prompt, user_prompt = self.prompt_service.build(
            context_chunks=context_chunks,
            question=question,
        )

        answer = await self.engine.generate_answer(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        logger.info("LLM response generated successfully.")

        return answer