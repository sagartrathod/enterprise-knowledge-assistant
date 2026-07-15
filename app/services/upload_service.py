# app/services/upload_service.py

from fastapi import UploadFile

from app.repositories.upload_repository import UploadRepository
from app.repositories.chunk_repository import ChunkRepository
from app.services.embedding_service import EmbeddingService

from app.utils.file_utils import save_temporary_file
from app.utils.pdf_parser import parse_pdf_layout
from app.utils.chunker import create_overlapping_chunks

from app.core.constants import CHUNK_MAX_WORDS, CHUNK_OVERLAP_WORDS


def clean_text(text: str) -> str:
    """
    Removes invalid characters before PostgreSQL insertion.
    """

    if not text:
        return ""

    return (
        text
        .replace("\x00", "")
        .replace("\ufeff", "")
        .encode("utf-8", errors="ignore")
        .decode("utf-8")
        .strip()
    )


class UploadService:

    def __init__(
        self,
        upload_repo: UploadRepository,
        chunk_repo: ChunkRepository,
        embedding_service: EmbeddingService
    ):
        self.upload_repo = upload_repo
        self.chunk_repo = chunk_repo
        self.embedding_service = embedding_service


    async def process_pdf_upload(self, file: UploadFile) -> dict:
        """
        Upload PDF -> Store locally -> Parse -> Chunk ->
        Generate embeddings -> Save metadata.
        """

        # Save permanently inside app/upload
        pdf_path = save_temporary_file(file)


        # 1. Create document record
        doc_record = await self.upload_repo.create_document(
            pdf_name=file.filename
        )

        if not doc_record:
            raise Exception(
                "Failed to create document record"
            )


        document_id = doc_record["document_id"]


        # 2. Parse PDF
        parsed_lines = parse_pdf_layout(
            pdf_path
        )

        if not parsed_lines:
            raise Exception(
                "No text extracted from PDF"
            )


        # 3. Generate chunks
        chunks = create_overlapping_chunks(
            parsed_lines,
            max_words=CHUNK_MAX_WORDS,
            overlap_words=CHUNK_OVERLAP_WORDS
        )


        processed_count = 0


        # 4. Generate embeddings and store
        for chunk in chunks:

            chunk_text = clean_text(
                chunk["chunk_text"]
            )

            chunk_text = chunk_text.replace(
                "\x00",
                ""
            ).strip()


            if not chunk_text:
                continue


            embedding = await self.embedding_service.get_embedding(
                chunk_text
            )


            await self.chunk_repo.save_chunk_metadata(
                document_id=document_id,
                chunk_number=chunk["chunk_number"],
                page_number=chunk["page_number"],
                line_start=chunk["line_start"],
                line_end=chunk["line_end"],
                chunk_text=chunk_text,
                embedding=embedding
            )


            processed_count += 1


        doc_record["total_chunks_processed"] = processed_count

        # Store local path in response
        doc_record["file_path"] = pdf_path


        return doc_record