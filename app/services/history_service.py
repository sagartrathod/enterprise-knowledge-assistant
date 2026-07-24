# app/services/history_service.py

from __future__ import annotations

from app.core.logger import logger
from app.exceptions.custom_exceptions import DatabaseException
from app.repositories.history_repository import HistoryRepository


class HistoryService:
    """
    Service responsible for conversation history operations.

    Responsibilities
    ----------------
    - Save conversations
    - Retrieve session history
    - Business validations
    - Repository orchestration
    """

    def __init__(
        self,
        history_repo: HistoryRepository,
    ) -> None:

        self.history_repo = history_repo

    # ==========================================================
    # Save Conversation
    # ==========================================================

    async def save_conversation(
        self,
        session_id: str,
        question: str,
        answer: str,
        citations: list[dict],
    ) -> str:
        """
        Save conversation with citations.
        """

        logger.info("=" * 100)
        logger.info("SAVE CONVERSATION")
        logger.info("=" * 100)

        logger.info(
            "Session=%s | Citations=%d",
            session_id,
            len(citations),
        )

        try:

            history_id = await self.history_repo.save_conversation(
                session_id=session_id,
                question=question,
                answer=answer,
                citations=citations,
            )

            logger.info(
                "Conversation saved successfully | History=%s",
                history_id,
            )

            return history_id

        except Exception as exc:

            logger.exception(
                "Failed to save conversation."
            )

            raise DatabaseException(
                "Failed to save conversation."
            ) from exc

    # ==========================================================
    # Fetch Session History
    # ==========================================================

    async def fetch_session_history(
        self,
        session_id: str,
        document_id: str,
    ) -> list[dict]:
        """
        Retrieve conversation history for a document.
        """

        logger.info("=" * 100)
        logger.info("FETCH SESSION HISTORY")
        logger.info("=" * 100)

        logger.info(
            "Session=%s | Document=%s",
            session_id,
            document_id,
        )

        try:

            history = await self.history_repo.get_session_history(
                session_id=session_id,
                document_id=document_id,
            )

            logger.info(
                "Retrieved %d conversation(s).",
                len(history),
            )

            return history

        except Exception as exc:

            logger.exception(
                "Failed to fetch session history."
            )

            raise DatabaseException(
                "Unable to retrieve conversation history."
            ) from exc