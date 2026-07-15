from fastapi import Depends
from asyncpg import Pool

from app.core.database import get_db_pool

from app.repositories import (
    DocumentRepository,
    UploadRepository,
    ChunkRepository,
    VectorRepository,
    HistoryRepository,
)

from app.services import (
    EmbeddingService,
    PromptService,
    LLMService,
    UploadService,
    DocumentService,
    HistoryService,
    ContextService,
    SemanticSearchService,
    BM25SearchService,
    HybridSearchService,
    RerankerService,
    RAGService,
)


# ==========================================================
# Repository Providers
# ==========================================================

def get_doc_repo(
    pool: Pool = Depends(get_db_pool),
) -> DocumentRepository:
    return DocumentRepository(pool)


def get_upload_repo(
    pool: Pool = Depends(get_db_pool),
) -> UploadRepository:
    return UploadRepository(pool)


def get_chunk_repo(
    pool: Pool = Depends(get_db_pool),
) -> ChunkRepository:
    return ChunkRepository(pool)


def get_vector_repo(
    pool: Pool = Depends(get_db_pool),
) -> VectorRepository:
    return VectorRepository(pool)


def get_history_repo(
    pool: Pool = Depends(get_db_pool),
) -> HistoryRepository:
    return HistoryRepository(pool)


# ==========================================================
# Core Services
# ==========================================================

def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()


def get_prompt_service() -> PromptService:
    return PromptService()


def get_context_service() -> ContextService:
    return ContextService()


def get_reranker_service() -> RerankerService:
    return RerankerService()


def get_llm_service(
    prompt_service: PromptService = Depends(
        get_prompt_service
    ),
) -> LLMService:

    return LLMService(
        prompt_service=prompt_service,
    )


# ==========================================================
# Search Services
# ==========================================================

def get_semantic_search_service(
    vector_repo: VectorRepository = Depends(
        get_vector_repo
    ),
    embedding_service: EmbeddingService = Depends(
        get_embedding_service
    ),
) -> SemanticSearchService:

    return SemanticSearchService(
        vector_repo=vector_repo,
        embedding_service=embedding_service,
    )


def get_bm25_service(
    vector_repo: VectorRepository = Depends(
        get_vector_repo
    ),
) -> BM25SearchService:

    return BM25SearchService(
        vector_repo=vector_repo,
    )


def get_hybrid_search_service(
    semantic_service: SemanticSearchService = Depends(
        get_semantic_search_service
    ),
    bm25_service: BM25SearchService = Depends(
        get_bm25_service
    ),
) -> HybridSearchService:

    return HybridSearchService(
        semantic_service=semantic_service,
        bm25_service=bm25_service,
    )


# ==========================================================
# Business Services
# ==========================================================

def get_upload_service(
    upload_repo: UploadRepository = Depends(
        get_upload_repo
    ),
    chunk_repo: ChunkRepository = Depends(
        get_chunk_repo
    ),
    embedding_service: EmbeddingService = Depends(
        get_embedding_service
    ),
) -> UploadService:

    return UploadService(
        upload_repo=upload_repo,
        chunk_repo=chunk_repo,
        embedding_service=embedding_service,
    )


def get_doc_service(
    doc_repo: DocumentRepository = Depends(
        get_doc_repo
    ),
) -> DocumentService:

    return DocumentService(doc_repo)


def get_history_service(
    history_repo: HistoryRepository = Depends(
        get_history_repo
    ),
) -> HistoryService:

    return HistoryService(
        history_repo=history_repo,
    )

# ==========================================================
# RAG Pipeline
# ==========================================================

def get_rag_service(
    hybrid_search_service: HybridSearchService = Depends(
        get_hybrid_search_service
    ),
    reranker_service: RerankerService = Depends(
        get_reranker_service
    ),
    context_service: ContextService = Depends(
        get_context_service
    ),
    llm_service: LLMService = Depends(
        get_llm_service
    ),
    history_service: HistoryService = Depends(
        get_history_service
    ),
) -> RAGService:

    return RAGService(
        hybrid_search_service=hybrid_search_service,
        reranker_service=reranker_service,
        context_service=context_service,
        llm_service=llm_service,
        history_service=history_service,
    )