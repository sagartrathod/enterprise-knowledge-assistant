from __future__ import annotations

from app.core.logger import logger
from app.services.context_service import ContextService
from app.services.history_service import HistoryService
from app.services.hybrid_search_service import HybridSearchService
from app.services.llm_service import LLMService
from app.services.reranker_service import RerankerService


class RAGService:
    """
    Enterprise Retrieval-Augmented Generation (RAG) Pipeline.

    Pipeline
    --------
        User Question
              │
              ▼
        Hybrid Search
              │
              ▼
           Reranker
              │
              ▼
        Context Builder
              │
              ▼
      Prompt + LLM (Groq)
              │
              ▼
        Save Conversation
    """

    DEFAULT_RESPONSE = (
        "I cannot find the answer based on the provided document chunks."
    )

    def __init__(
        self,
        hybrid_search_service: HybridSearchService,
        reranker_service: RerankerService,
        context_service: ContextService,
        llm_service: LLMService,
        history_service: HistoryService,
    ) -> None:

        self.hybrid_search_service = hybrid_search_service
        self.reranker_service = reranker_service
        self.context_service = context_service
        self.llm_service = llm_service
        self.history_service = history_service

    async def execute_rag_pipeline(
        self,
        session_id: str,
        document_id: str | None,
        question: str,
        top_k: int = 10,
    ) -> dict:
        """
        Execute the complete RAG pipeline.
        """

        logger.info(
            "Starting RAG pipeline | session=%s | document=%s",
            session_id,
            document_id,
        )

        try:

            # ======================================================
            # Step 1 : Hybrid Retrieval
            # ======================================================

            retrieved_chunks = await self.hybrid_search_service.search(
                question=question,
                top_k=top_k,
                document_id=document_id,
            )

            logger.info(
                "Hybrid search returned %d chunks.",
                len(retrieved_chunks),
            )

            # ======================================================
            # Step 2 : Rerank
            # ======================================================

            reranked_chunks = await self.reranker_service.rerank(
                question=question,
                chunks=retrieved_chunks,
                top_k=top_k,
            )

            logger.info(
                "Reranker returned %d chunks.",
                len(reranked_chunks),
            )

            # ======================================================
            # Step 3 : Prepare Context
            # ======================================================

            context, context_chunks = self.context_service.prepare_context(
                reranked_chunks
            )

            logger.debug("Context length: %d", len(context))

            if not context_chunks:

                logger.info("No relevant context found.")

                await self.history_service.save_conversation(
                    session_id=session_id,
                    question=question,
                    answer=self.DEFAULT_RESPONSE,
                    citations=[],
                )

                return {
                    "session_id": session_id,
                    "answer": self.DEFAULT_RESPONSE,
                    "total_chunks_used": 0,
                    "citations": [],
                }

            logger.info(
                "Prepared %d context chunks.",
                len(context_chunks),
            )

            # ======================================================
            # Step 4 : Generate Answer
            # ======================================================

            answer = await self.llm_service.generate_response(
                context_chunks=context_chunks,
                question=question,
            )

            # ======================================================
            # Step 5 : Build Citations
            # ======================================================

            citations = [
                {
                    "document_id": str(chunk["document_id"]),
                    "pdf_name": chunk["pdf_name"],
                    "chunk_number": chunk["chunk_number"],
                    "page_number": chunk["page_number"],
                    "line_start": chunk["line_start"],
                    "line_end": chunk["line_end"],
                    "similarity": round(
                        chunk.get("similarity", 0.0),
                        4,
                    ),
                    "chunk_text": chunk["chunk_text"],
                }
                for chunk in context_chunks
            ]

            if answer.strip() == self.DEFAULT_RESPONSE:
                citations = []

            # ======================================================
            # Step 6 : Save Conversation
            # ======================================================

            await self.history_service.save_conversation(
                session_id=session_id,
                question=question,
                answer=answer,
                citations=citations,
            )

            logger.info(
                "Conversation saved successfully."
            )

            logger.info(
                "RAG pipeline completed successfully."
            )

            return {
                "session_id": session_id,
                "answer": answer,
                "total_chunks_used": len(citations),
                "citations": citations,
            }

        except Exception:

            logger.exception(
                "RAG pipeline execution failed."
            )

            raise