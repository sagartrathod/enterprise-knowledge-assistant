# app/services/history_service.py

from __future__ import annotations

from app.core.logger import logger
from app.repositories.history_repository import HistoryRepository


class HistoryService:
    """
    Service responsible for conversation history operations.

    Responsibilities
    ----------------
    - Save conversations
    - Retrieve session history
    - Encapsulate history repository operations
    """

    def __init__(
        self,
        history_repo: HistoryRepository,
    ) -> None:

        self.history_repo = history_repo

    async def save_conversation(
        self,
        session_id: str,
        question: str,
        answer: str,
        citations: list[dict],
    ) -> str:
        """
        Persist a conversation and its citations.

        Args:
            session_id:
                Chat session identifier.

            question:
                User question.

            answer:
                LLM generated answer.

            citations:
                Retrieved chunks used for answering.

        Returns:
            History record ID.
        """

        logger.info(
            "Saving conversation | session=%s | citations=%d",
            session_id,
            len(citations),
        )

        history_id = await self.history_repo.save_conversation(
            session_id=session_id,
            question=question,
            answer=answer,
            citations=citations,
        )

        logger.info(
            "Conversation saved successfully | history_id=%s",
            history_id,
        )

        return history_id

    async def fetch_session_history(
        self,
        session_id: str,
    ) -> list[dict]:
        """
        Retrieve complete conversation history for a session.

        Args:
            session_id:
                Chat session identifier.

        Returns:
            List of conversations.
        """

        logger.info(
            "Fetching conversation history | session=%s",
            session_id,
        )

        history = await self.history_repo.get_session_history(
            session_id=session_id,
        )

        logger.info(
            "Retrieved %d conversation(s).",
            len(history),
        )

        return history