from __future__ import annotations

from uuid import UUID

from fastapi import Depends, Query

from app.api.deps import get_history_service
from app.schemas import HistoryListResponse
from app.services.history_service import HistoryService
from app.core.logger import logger


async def get_session_history(
    session_id: str = Query(
        ...,
        description="Chat session identifier.",
    ),
    document_id: UUID = Query(
        ...,
        description="Selected document identifier.",
    ),
    history_service: HistoryService = Depends(
        get_history_service,
    ),
) -> HistoryListResponse:
    """
    Retrieve conversation history for the selected document.
    """

    logger.info(
        "History request | Session=%s | Document=%s",
        session_id,
        document_id,
    )

    history = await history_service.fetch_session_history(
        session_id=session_id,
        document_id=str(document_id),
    )

    logger.info(
        "History retrieved successfully. Conversations=%d",
        len(history),
    )

    return HistoryListResponse(
        session_id=session_id,
        document_id=document_id,
        history=history,
    )