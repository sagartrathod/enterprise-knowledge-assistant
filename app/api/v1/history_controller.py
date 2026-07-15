# app/api/v1/history_controller.py

from pprint import pprint

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
        description="The structural storage session identifier tracking conversation threads.",
    ),
    history_service: HistoryService = Depends(
        get_history_service
    ),
):
    """
    Retrieves full conversation logs
    along with their source chunks.
    """

    history_records = await history_service.fetch_session_history(
        session_id
    )

    response = {
        "session_id": session_id,
        "history": history_records,
    }

    print("\n================ HISTORY API RESPONSE ================\n")
    pprint(response, sort_dicts=False)
    print("\n======================================================\n")

    return response