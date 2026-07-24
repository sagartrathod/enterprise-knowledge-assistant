from __future__ import annotations

import uuid

from fastapi import Depends

from app.api.deps import get_rag_service
from app.core.logger import logger
from app.schemas import (
    QueryRequest,
    QueryResponse,
)
from app.services.rag_service import RAGService


async def query_assistant(
    request: QueryRequest,
    rag_service: RAGService = Depends(
        get_rag_service,
    ),
) -> QueryResponse:
    """
    Execute the Enterprise RAG pipeline.

    Exceptions are propagated to the
    global exception handlers.
    """

    session_id = request.session_id or str(
        uuid.uuid4()
    )

    logger.info(
        "Query Request | Session=%s | Document=%s",
        session_id,
        request.document_id,
    )

    logger.info(
        "Question: %s",
        request.question,
    )

    result = await rag_service.execute_rag_pipeline(
        session_id=session_id,
        document_id=request.document_id,
        question=request.question,
        top_k=request.top_k,
    )

    logger.info(
        "RAG pipeline completed successfully."
    )

    return QueryResponse(**result)