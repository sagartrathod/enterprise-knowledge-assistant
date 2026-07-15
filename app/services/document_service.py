# app/services/document_service.py
from app.repositories.document_repository import DocumentRepository

class DocumentService:
    def __init__(self, doc_repo: DocumentRepository):
        self.doc_repo = doc_repo

    async def list_all_documents(self) -> list[dict]:
        return await self.doc_repo.get_all()

    async def purge_document(self, document_id: str) -> bool:
        return await self.doc_repo.delete_by_id(document_id)