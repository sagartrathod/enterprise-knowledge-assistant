from __future__ import annotations

import time

from groq import (
    APIError,
    APITimeoutError,
    AsyncGroq,
    AuthenticationError,
    RateLimitError,
)

from app.core.config import settings
from app.core.constants import (
    DEFAULT_NO_ANSWER,
    GROQ_MODEL,
    LLM_FREQUENCY_PENALTY,
    LLM_MAX_TOKENS,
    LLM_PRESENCE_PENALTY,
    LLM_TEMPERATURE,
    LLM_TOP_P,
)
from app.core.logger import logger


class GroqClient:
    """
    Enterprise Groq Client.

    Responsibilities
    ----------------
    - Connect to Groq
    - Execute chat completion requests
    - Return generated responses
    - Handle API failures
    - Log request statistics

    This class MUST NOT know anything about:
    - RAG
    - Context retrieval
    - Prompt engineering
    """

    def __init__(self) -> None:

        self.client = AsyncGroq(
            api_key=settings.GROQ_API_KEY,
        )

        self.model = GROQ_MODEL

        logger.info(
            "GroqClient initialized | Model=%s",
            self.model,
        )

    async def generate_answer(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """
        Generate answer using Groq.
        """

        if not system_prompt.strip():

            logger.warning(
                "System prompt is empty."
            )

            return DEFAULT_NO_ANSWER

        if not user_prompt.strip():

            logger.warning(
                "User prompt is empty."
            )

            return DEFAULT_NO_ANSWER

        logger.info("=" * 100)
        logger.info("GROQ REQUEST")
        logger.info("=" * 100)

        logger.info("Model : %s", self.model)

        logger.info(
            "Temperature : %.2f",
            LLM_TEMPERATURE,
        )

        logger.info(
            "Top P : %.2f",
            LLM_TOP_P,
        )

        logger.info(
            "Max Tokens : %d",
            LLM_MAX_TOKENS,
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

        start = time.perf_counter()

        try:

            response = await self.client.chat.completions.create(

                model=self.model,

                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],

                temperature=LLM_TEMPERATURE,
                top_p=LLM_TOP_P,
                max_tokens=LLM_MAX_TOKENS,
                frequency_penalty=LLM_FREQUENCY_PENALTY,
                presence_penalty=LLM_PRESENCE_PENALTY,
                stream=False,
            )

            elapsed = time.perf_counter() - start

            if (
                not response.choices
                or response.choices[0].message.content is None
            ):

                logger.warning(
                    "Groq returned an empty response."
                )

                return DEFAULT_NO_ANSWER

            answer = (
                response.choices[0]
                .message
                .content
                .strip()
            )

            logger.info(
                "Groq completed successfully."
            )

            logger.info(
                "Response Time : %.2f sec",
                elapsed,
            )

            logger.info(
                "Answer Length : %d characters",
                len(answer),
            )

            logger.info("=" * 100)

            return answer

        except AuthenticationError:

            logger.exception(
                "Groq authentication failed."
            )

            raise

        except RateLimitError:

            logger.exception(
                "Groq rate limit exceeded."
            )

            raise

        except APITimeoutError:

            logger.exception(
                "Groq request timed out."
            )

            raise

        except APIError:

            logger.exception(
                "Groq API error."
            )

            raise

        except Exception:

            logger.exception(
                "Unexpected Groq error."
            )

            raise