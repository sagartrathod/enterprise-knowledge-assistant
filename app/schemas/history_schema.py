from uuid import UUID
from datetime import datetime
from typing import List

from .common_schema import BaseResponseSchema
from .query_schema import ChunkCitation


class HistorySessionRecord(BaseResponseSchema):

    id: UUID

    session_id: str

    question: str

    answer: str

    total_chunks_used: int

    created_at: datetime

    citations: List[ChunkCitation]


class HistoryListResponse(BaseResponseSchema):

    session_id: str

    history: List[HistorySessionRecord]