from uuid import UUID
from datetime import datetime
from typing import List

from .common_schema import BaseResponseSchema
from .query_schema import ChunkCitation


class HistorySessionRecord(BaseResponseSchema):
    """
    Single conversation record within a chat session.
    """

    id: UUID

    session_id: str

    question: str

    answer: str

    total_chunks_used: int

    created_at: datetime

    citations: List[ChunkCitation]


class HistoryListResponse(BaseResponseSchema):
    """
    History response for a selected document.
    """

    session_id: str

    document_id: UUID

    history: List[HistorySessionRecord]