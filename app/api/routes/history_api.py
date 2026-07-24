from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_history_service
from app.controllers.history_controller import get_session_history
from app.schemas import HistoryListResponse
from app.services import HistoryService

router = APIRouter(tags=["History"])


@router.get(
    "/history",
    response_model=HistoryListResponse,
)
async def history(
    session_id: str = Query(...),
    document_id: UUID = Query(...),
    history_service: HistoryService = Depends(get_history_service),
):
    return await get_session_history(
        session_id=session_id,
        document_id=document_id,
        history_service=history_service,
    )