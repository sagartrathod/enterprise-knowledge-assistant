from fastapi import APIRouter, Depends

from app.api.deps import get_rag_service
from app.controllers.query_controller import query_assistant
from app.schemas import QueryRequest, QueryResponse
from app.services import RAGService

router = APIRouter(
    tags=["Query"],
)


@router.post(
    "/query",
    response_model=QueryResponse,
    summary="Query Enterprise Knowledge Base",
    description=(
        "Search the selected document using Hybrid Search, "
        "CrossEncoder Reranking, and LLM to generate an answer."
    ),
)
async def query(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> QueryResponse:
    """
    Query the Enterprise AI Knowledge Assistant.

    Pipeline
    --------
    1. Hybrid Search
    2. CrossEncoder Reranking
    3. Context Building
    4. LLM Answer Generation
    5. Save Conversation History

    Returns
    -------
    - Answer
    - Confidence
    - Pipeline timings
    - Retrieval metrics
    - Citations
    """

    return await query_assistant(
        request=request,
        rag_service=rag_service,
    )