from __future__ import annotations

from groq import AsyncGroq
from groq import APIError
from groq import APITimeoutError
from groq import RateLimitError

from app.core.config import settings
from app.core.logger import logger


class GroqClient:
    """
    Enterprise Groq Client.

    Responsibilities
    ----------------
    - Connect to Groq.
    - Send chat completion requests.
    - Return generated responses.
    - Handle API errors.

    This class MUST NOT:
    - Build prompts.
    - Format context.
    - Know anything about RAG.
    """

    DEFAULT_FALLBACK = (
        "I cannot find the answer based on the provided document chunks."
    )

    def __init__(self) -> None:

        self.client = AsyncGroq(
            api_key=settings.GROQ_API_KEY,
        )

        self.model = getattr(
            settings,
            "GROQ_MODEL",
            "llama-3.3-70b-versatile",
        )

    async def generate_answer(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """
        Generate an answer using Groq.

        Parameters
        ----------
        system_prompt:
            System instructions.

        user_prompt:
            Final user prompt.

        Returns
        -------
        Generated answer.
        """

        logger.info(
            "Calling Groq model=%s",
            self.model,
        )

        logger.debug(
            "User prompt size=%d characters",
            len(user_prompt),
        )

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

                temperature=0.0,

                top_p=1.0,

                max_tokens=1024,

                frequency_penalty=0,

                presence_penalty=0,

                stream=False,
            )

            if (
                not response.choices
                or response.choices[0].message.content is None
            ):

                logger.warning(
                    "Groq returned an empty response."
                )

                return self.DEFAULT_FALLBACK

            answer = (
                response.choices[0]
                .message
                .content
                .strip()
            )

            logger.info(
                "Groq response generated successfully."
            )

            return answer

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