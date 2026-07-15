# app/api/v1/document_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from app.schemas import DocumentListResponse, MessageResponse
from app.services import DocumentService
from app.api.deps import get_doc_service

router = APIRouter()

@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(doc_service: DocumentService = Depends(get_doc_service)):
    """Fetches metadata profiles for all currently parsed and indexed enterprise PDFs."""
    documents = await doc_service.list_all_documents()
    return {"documents": documents}

@router.delete("/documents/{document_id}", response_model=MessageResponse)
async def delete_document(
    document_id: UUID,
    doc_service: DocumentService = Depends(get_doc_service)
):
    """
    Purges a document profile from the master record. All relational elements 
    (chunks, vectors, citations) cascade delete automatically.
    """
    purged = await doc_service.purge_document(str(document_id))
    if not purged:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No document tracking signature found matching ID: {document_id}"
        )
    return {"status": "success", "message": f"Document {document_id} cleared successfully."}