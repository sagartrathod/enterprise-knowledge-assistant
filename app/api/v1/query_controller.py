from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import QueryRequest, QueryResponse
from app.services import RAGService
from app.api.deps import get_rag_service
import uuid


router = APIRouter()


@router.post(
    "/query",
    response_model=QueryResponse
)
async def query_assistant(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service)
):

    try:

        session_id = request.session_id or str(uuid.uuid4())


        result = await rag_service.execute_rag_pipeline(

            session_id=session_id,

            document_id=request.document_id,

            question=request.question,

            top_k=request.top_k

        )


        return result


    except Exception as e:

        raise HTTPException(

            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=f"RAG Pipeline execution failure: {str(e)}"

        )