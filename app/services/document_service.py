# app/services/document_service.py

from __future__ import annotations

from app.core.logger import logger
from app.exceptions.custom_exceptions import NotFoundException
from app.repositories.document_repository import DocumentRepository


class DocumentService:
    """
    Service responsible for document operations.

    Responsibilities
    ----------------
    - Retrieve documents
    - Delete documents
    - Business validations
    - Repository orchestration
    """

    def __init__(
        self,
        doc_repo: DocumentRepository,
    ) -> None:

        self.doc_repo = doc_repo

    # ==========================================================
    # List Documents
    # ==========================================================

    async def list_all_documents(
        self,
    ) -> list[dict]:
        """
        Retrieve all indexed documents.
        """

        logger.info("=" * 100)
        logger.info("LIST DOCUMENTS")
        logger.info("=" * 100)

        documents = await self.doc_repo.get_all()

        logger.info(
            "Retrieved %d document(s).",
            len(documents),
        )

        return documents

    # ==========================================================
    # Delete Document
    # ==========================================================

    async def delete_document(
        self,
        document_id: str,
    ) -> None:
        """
        Delete document.
        """

        logger.info("=" * 100)
        logger.info("DELETE DOCUMENT")
        logger.info("=" * 100)

        logger.info(
            "Document ID : %s",
            document_id,
        )

        deleted = await self.doc_repo.delete_by_id(
            document_id=document_id,
        )

        if not deleted:

            logger.warning(
                "Document not found : %s",
                document_id,
            )

            raise NotFoundException(
                "Document not found."
            )

        logger.info(
            "Document deleted successfully."
        )