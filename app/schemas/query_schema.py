from __future__ import annotations

import uuid
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from .common_schema import BaseResponseSchema


class QueryRequest(BaseModel):
    document_id: Optional[UUID] = None

    session_id: Optional[str] = None

    question: str

    top_k: int = 5

    def get_session_id(self) -> str:
        return self.session_id or str(uuid.uuid4())


class ChunkCitation(BaseResponseSchema):
    document_id: UUID

    pdf_name: str

    chunk_number: int

    page_start: int

    page_end: int

    line_start: int

    line_end: int

    similarity: float = 0.0

    rerank_score: float = 0.0

    keyword_score: float = 0.0

    rrf_score: float = 0.0

    distance: float = 0.0

    chunk_confidence: float = 0.0

    chunk_text: str


class QueryResponse(BaseResponseSchema):
    session_id: str

    answer: str

    confidence: float

    confidence_level: str

    average_similarity: float

    average_rerank_score: float

    average_keyword_score: float

    search_time_seconds: float

    rerank_time_seconds: float

    context_time_seconds: float

    llm_time_seconds: float

    pipeline_time_seconds: float

    total_chunks_used: int

    citations: List[ChunkCitation]