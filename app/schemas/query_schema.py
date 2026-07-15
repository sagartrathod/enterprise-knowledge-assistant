from uuid import UUID
from typing import List, Optional
import uuid

from pydantic import BaseModel

from .common_schema import BaseResponseSchema


class QueryRequest(BaseModel):

    document_id: Optional[UUID] = None

    session_id: Optional[str] = None

    question: str

    top_k: int = 5

    def get_session_id(self):

        return self.session_id or str(uuid.uuid4())


class ChunkCitation(BaseResponseSchema):

    document_id: UUID

    pdf_name: str

    chunk_number: int

    page_number: int

    line_start: int

    line_end: int

    # Required for history and Streamlit UI
    similarity: float = 0.0

    chunk_text: str


class QueryResponse(BaseResponseSchema):

    session_id: str

    answer: str

    total_chunks_used: int

    citations: List[ChunkCitation]