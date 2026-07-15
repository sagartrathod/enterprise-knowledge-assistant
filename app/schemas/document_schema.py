from uuid import UUID
from datetime import datetime
from typing import List
from .common_schema import BaseResponseSchema

class DocumentDetail(BaseResponseSchema):
    document_id: UUID
    pdf_name: str
    created_at: datetime

class DocumentListResponse(BaseResponseSchema):
    documents: List[DocumentDetail]