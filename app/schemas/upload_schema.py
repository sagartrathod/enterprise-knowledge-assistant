from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from .common_schema import BaseResponseSchema


class UploadResponse(BaseResponseSchema):
    document_id: UUID
    pdf_name: str
    total_chunks_processed: int
    created_at: datetime


class UploadErrorResponse(BaseModel):
    filename: str
    error: str


class MultiUploadResponse(BaseModel):
    total_files: int
    uploaded: int
    failed: int
    documents: list[UploadResponse]
    errors: list[UploadErrorResponse]