# app/api/v1/history_controller.py

from __future__ import annotations

from pprint import pprint
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_history_service
from app.schemas import HistoryListResponse
from app.services import HistoryService

router = APIRouter()


@router.get(
    "/history",
    response_model=HistoryListResponse,
)
async def get_session_history(
    session_id: str = Query(
        ...,
        description="The chat session identifier.",
    ),
    document_id: UUID = Query(
        ...,
        description="The currently selected document identifier.",
    ),
    history_service: HistoryService = Depends(
        get_history_service,
    ),
):
    """
    Retrieve conversation history for the selected document.

    Returns only the conversations whose citations belong to the
    specified document.
    """

    history_records = await history_service.fetch_session_history(
        session_id=session_id,
        document_id=str(document_id),
    )

    response = {
        "session_id": session_id,
        "document_id": str(document_id),
        "history": history_records,
    }

    print("\n" + "=" * 80)
    print("HISTORY API RESPONSE")
    print("=" * 80)
    pprint(response, sort_dicts=False)
    print("=" * 80 + "\n")

    return response