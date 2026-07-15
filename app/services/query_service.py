from app.repositories.vector_repository import VectorRepository
from app.services.embedding_service import EmbeddingService


class QueryService:
    """
    Service responsible for semantic retrieval.
    """

    def __init__(
        self,
        vector_repo: VectorRepository,
        embedding_service: EmbeddingService,
    ):
        self.vector_repo = vector_repo
        self.embedding_service = embedding_service

    async def match_relevant_context(
        self,
        question: str,
        top_k: int,
        document_id=None,
    ):
        """
        Generate embedding for the user query and retrieve
        top-k matching chunks.
        """

        query_vector = await self.embedding_service.get_embedding(
            question
        )

        return await self.vector_repo.search_top_k(
            query_embedding=query_vector,
            top_k=top_k,
            document_id=document_id,
        )