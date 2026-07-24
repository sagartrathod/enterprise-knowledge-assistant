from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_doc_service
from app.controllers.document_controller import (
    delete_document,
    list_documents,
)
from app.schemas import (
    DocumentListResponse,
    MessageResponse,
)
from app.services import DocumentService

router = APIRouter(tags=["Documents"])


@router.get(
    "/documents",
    response_model=DocumentListResponse,
)
async def documents(
    doc_service: DocumentService = Depends(get_doc_service),
):
    return await list_documents(
        doc_service=doc_service,
    )


@router.delete(
    "/documents/{document_id}",
    response_model=MessageResponse,
)
async def delete(
    document_id: UUID,
    doc_service: DocumentService = Depends(get_doc_service),
):
    return await delete_document(
        document_id=document_id,
        doc_service=doc_service,
    )