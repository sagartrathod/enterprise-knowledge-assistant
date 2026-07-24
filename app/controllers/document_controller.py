from uuid import UUID

from fastapi import Depends

from app.api.deps import get_doc_service
from app.schemas import (
    DocumentListResponse,
    MessageResponse,
)
from app.services.document_service import DocumentService


async def list_documents(
    doc_service: DocumentService = Depends(get_doc_service),
) -> DocumentListResponse:
    """
    Retrieve all uploaded documents.
    """

    documents = await doc_service.list_all_documents()

    return DocumentListResponse(
        documents=documents,
    )


async def delete_document(
    document_id: UUID,
    doc_service: DocumentService = Depends(get_doc_service),
) -> MessageResponse:
    """
    Delete a document.

    Exceptions are handled globally.
    """

    await doc_service.delete_document(
        document_id=document_id,
    )

    return MessageResponse(
        status="success",
        message="Document deleted successfully.",
    )