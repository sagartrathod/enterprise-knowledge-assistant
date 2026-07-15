from uuid import UUID
from datetime import datetime
from .common_schema import BaseResponseSchema

class UploadResponse(BaseResponseSchema):
    document_id: UUID
    pdf_name: str
    total_chunks_processed: int
    created_at: datetime