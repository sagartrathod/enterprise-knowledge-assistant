from __future__ import annotations

import time

from app.core.constants import (
    DEFAULT_NO_ANSWER,
    DEFAULT_RAG_TOP_K,
)
from app.core.logger import logger
from app.services.context_service import ContextService
from app.services.guardrail_service import GuardrailService
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
        Guardrails
              │
              ▼
        Hybrid Search
              │
              ▼
        CrossEncoder Reranker
              │
              ▼
        Context Builder
              │
              ▼
        Prompt + LLM
              │
              ▼
        Output Guardrails
              │
              ▼
        Save Conversation
    """

    def __init__(
        self,
        hybrid_search_service: HybridSearchService,
        reranker_service: RerankerService,
        context_service: ContextService,
        llm_service: LLMService,
        history_service: HistoryService,
        guardrail_service: GuardrailService,
    ) -> None:

        self.hybrid_search_service = hybrid_search_service
        self.reranker_service = reranker_service
        self.context_service = context_service
        self.llm_service = llm_service
        self.history_service = history_service
        self.guardrail_service = guardrail_service

    def _empty_response(
        self,
        session_id: str,
        answer: str,
        level: str,
    ) -> dict:

        return {
            "session_id": session_id,
            "answer": answer,
            "confidence": 0.0,
            "confidence_level": level,
            "average_similarity": 0.0,
            "average_rerank_score": 0.0,
            "average_keyword_score": 0.0,
            "pipeline_time_seconds": 0.0,
            "search_time_seconds": 0.0,
            "rerank_time_seconds": 0.0,
            "context_time_seconds": 0.0,
            "llm_time_seconds": 0.0,
            "total_chunks_used": 0,
            "citations": [],
        }

    async def execute_rag_pipeline(
        self,
        session_id: str,
        document_id: str | None,
        question: str,
        top_k: int = DEFAULT_RAG_TOP_K,
    ) -> dict:

        start_time = time.perf_counter()

        logger.info("=" * 100)
        logger.info("STARTING RAG PIPELINE")
        logger.info("=" * 100)

        logger.info("Question : %s", question)
        logger.info(
            "Session=%s | Document=%s",
            session_id,
            document_id,
        )

        try:

            # =====================================================
            # Guardrail 1 : Rate Limiting
            # =====================================================

            if not self.guardrail_service.allow_request(session_id):

                logger.warning(
                    "AUDIT | Rate limit exceeded | Session=%s",
                    session_id,
                )

                return self._empty_response(
                    session_id=session_id,
                    answer="Too many requests. Please try again later.",
                    level="Blocked",
                )

            # =====================================================
            # Guardrail 2 : Question Validation
            # =====================================================

            valid, message = (
                self.guardrail_service.validate_question(
                    question
                )
            )

            if not valid:

                logger.warning(
                    "AUDIT | Invalid question blocked | "
                    "Session=%s | Reason=%s",
                    session_id,
                    message,
                )

                return self._empty_response(
                    session_id=session_id,
                    answer=message,
                    level="Rejected",
                )

            logger.info(
                "AUDIT | Question validation passed."
            )

            # =====================================================
            # Step 1 : Hybrid Search
            # =====================================================

            search_start = time.perf_counter()

            retrieved_chunks = (
                await self.hybrid_search_service.search(
                    question=question,
                    top_k=top_k,
                    document_id=document_id,
                )
            )

            search_time = (
                time.perf_counter() - search_start
            )

            logger.info(
                "Hybrid Search Time : %.2f sec",
                search_time,
            )

            logger.info(
                "AUDIT | Retrieved %d chunks",
                len(retrieved_chunks),
            )

            if not retrieved_chunks:

                logger.warning(
                    "AUDIT | No chunks retrieved."
                )

            else:

                primary = retrieved_chunks[0]

                logger.info(
                    (
                        "PRIMARY CHUNK | "
                        "Similarity=%.4f | "
                        "Pages=%s-%s | "
                        "Chunk=%s"
                    ),
                    float(
                        primary.get(
                            "similarity",
                            0.0,
                        )
                    ),
                    primary.get("page_start"),
                    primary.get("page_end"),
                    primary.get("chunk_number"),
                )

            # =====================================================
            # Step 2 : CrossEncoder Reranking
            # =====================================================

            rerank_start = time.perf_counter()

            reranked_chunks = (
                await self.reranker_service.rerank(
                    question=question,
                    chunks=retrieved_chunks,
                    top_k=top_k,
                )
            )

            rerank_time = (
                time.perf_counter() - rerank_start
            )

            logger.info(
                "Reranker Time : %.2f sec",
                rerank_time,
            )

            logger.info(
                "AUDIT | Reranked %d chunks",
                len(reranked_chunks),
            )

            if reranked_chunks:

                best = max(
                    reranked_chunks,
                    key=lambda x: float(
                        x.get(
                            "rerank_score",
                            0.0,
                        )
                    ),
                )

                logger.info(
                    (
                        "BEST RERANK CHUNK | "
                        "Score=%.4f | "
                        "Pages=%s-%s | "
                        "Chunk=%s"
                    ),
                    float(
                        best.get(
                            "rerank_score",
                            0.0,
                        )
                    ),
                    best.get("page_start"),
                    best.get("page_end"),
                    best.get("chunk_number"),
                )



            # =====================================================
            # Step 3 : Context Builder
            # =====================================================

            context_start = time.perf_counter()

            context, context_chunks = (
                self.context_service.prepare_context(
                    reranked_chunks
                )
            )

            context_time = (
                time.perf_counter() - context_start
            )

            # -----------------------------
            # Guardrail : Context Validation
            # -----------------------------

            valid, message = (
                self.guardrail_service.validate_context(
                    context_chunks,
                )
            )

            if not valid:

                logger.warning(
                    "AUDIT | Context validation failed | Session=%s | Reason=%s",
                    session_id,
                    message,
                )

                return self._empty_response(
                    session_id=session_id,
                    answer=message,
                    level="No Context",
                )

            logger.info(
                "Context Builder Time : %.2f sec",
                context_time,
            )

            logger.info(
                "LLM Context contains %d chunks.",
                len(context_chunks),
            )

            if not context_chunks:

                logger.warning(
                    "AUDIT | No context found | Session=%s",
                    session_id,
                )

                await self.history_service.save_conversation(
                    session_id=session_id,
                    question=question,
                    answer=DEFAULT_NO_ANSWER,
                    citations=[],
                )

                return self._empty_response(
                    session_id=session_id,
                    answer=DEFAULT_NO_ANSWER,
                    level="No Context",
                )

            # =====================================================
            # Confidence Calculation
            # =====================================================

            confidence = (
                self.context_service.calculate_confidence(
                    context_chunks
                )
            )

            logger.info(
                "Answer Confidence : %.2f%%",
                confidence,
            )

            # =====================================================
            # Step 4 : Generate Answer
            # =====================================================

            llm_start = time.perf_counter()

            answer = await self.llm_service.generate_response(
                context_chunks=context_chunks,
                question=question,
            )

            # -----------------------------
            # Guardrail : Output Validation
            # -----------------------------

            answer = (
                self.guardrail_service.validate_answer(
                    answer
                )
            )

            # -----------------------------
            # Guardrail : PII Detection
            # -----------------------------

            masked_answer = (
                self.guardrail_service.mask_pii(
                    answer
                )
            )

            if masked_answer != answer:

                logger.warning(
                    "AUDIT | PII detected and masked | Session=%s",
                    session_id,
                )

            answer = masked_answer

            # -----------------------------
            # Guardrail : Toxicity Detection
            # -----------------------------

            if self.guardrail_service.detect_toxicity(
                answer
            ):

                logger.warning(
                    "AUDIT | Toxic response blocked | Session=%s",
                    session_id,
                )

                answer = (
                    "The generated response contains unsafe content."
                )

            # -----------------------------
            # Guardrail : Secret Detection
            # -----------------------------

            if self.guardrail_service.detect_secrets(
                answer
            ):

                logger.warning(
                    "AUDIT | Secret detected in answer | Session=%s",
                    session_id,
                )

                answer = (
                    "Sensitive information has been removed."
                )

            # -----------------------------
            # Guardrail : Hallucination Check
            # -----------------------------

            if not self.guardrail_service.check_hallucination(
                answer,
                context_chunks,
            ):

                logger.warning(
                    "AUDIT | Hallucination detected | Session=%s",
                    session_id,
                )

                answer = DEFAULT_NO_ANSWER

            llm_time = (
                time.perf_counter() - llm_start
            )

            logger.info(
                "LLM Time : %.2f sec",
                llm_time,
            )

            logger.info(
                "Generated answer length : %d",
                len(answer),
            )

            logger.debug(
                "Generated Answer:\n%s",
                answer,
            )

            # =====================================================
            # Pipeline Timings
            # =====================================================

            search_time = (
                time.perf_counter() - search_start
            )

            rerank_time = (
                time.perf_counter() - rerank_start
            )

                        # =====================================================
            # Step 5 : Build Citations
            # =====================================================

            citations = []

            for chunk in context_chunks:

                chunk_confidence = (
                    (
                        float(chunk.get("similarity", 0.0)) * 0.50
                        + float(chunk.get("rerank_score", 0.0)) * 0.40
                        + float(chunk.get("keyword_score", 0.0)) * 0.10
                    )
                    * 100
                )

                citations.append(
                    {
                        "document_id": str(chunk["document_id"]),
                        "pdf_name": chunk["pdf_name"],
                        "page_start": chunk["page_start"],
                        "page_end": chunk["page_end"],
                        "chunk_number": chunk["chunk_number"],
                        "line_start": chunk["line_start"],
                        "line_end": chunk["line_end"],
                        "similarity": round(
                            float(chunk.get("similarity", 0.0)),
                            4,
                        ),
                        "rerank_score": round(
                            float(chunk.get("rerank_score", 0.0)),
                            4,
                        ),
                        "keyword_score": round(
                            float(chunk.get("keyword_score", 0.0)),
                            4,
                        ),
                        "rrf_score": round(
                            float(chunk.get("rrf_score", 0.0)),
                            4,
                        ),
                        "distance": round(
                            float(chunk.get("distance", 0.0)),
                            6,
                        ),
                        "chunk_confidence": round(
                            chunk_confidence,
                            2,
                        ),
                        "chunk_text": chunk["chunk_text"],
                    }
                )

            if answer.strip() == DEFAULT_NO_ANSWER:

                logger.warning(
                    "AUDIT | Citations removed because answer was rejected."
                )

                citations = []

            # =====================================================
            # Step 6 : Calculate Metrics
            # =====================================================

            chunk_count = len(context_chunks)

            average_similarity = (
                sum(
                    float(c.get("similarity", 0.0))
                    for c in context_chunks
                ) / chunk_count
                if chunk_count
                else 0.0
            )

            average_rerank_score = (
                sum(
                    float(c.get("rerank_score", 0.0))
                    for c in context_chunks
                ) / chunk_count
                if chunk_count
                else 0.0
            )

            average_keyword_score = (
                sum(
                    float(c.get("keyword_score", 0.0))
                    for c in context_chunks
                ) / chunk_count
                if chunk_count
                else 0.0
            )

            if confidence >= 90:
                confidence_level = "Excellent"
            elif confidence >= 75:
                confidence_level = "High"
            elif confidence >= 60:
                confidence_level = "Medium"
            elif confidence >= 40:
                confidence_level = "Low"
            else:
                confidence_level = "Very Low"

            # =====================================================
            # Step 7 : Save Conversation
            # =====================================================

            await self.history_service.save_conversation(
                session_id=session_id,
                question=question,
                answer=answer,
                citations=citations,
            )

            logger.info(
                "Conversation saved successfully."
            )

            elapsed = time.perf_counter() - start_time

            # =====================================================
            # Pipeline Statistics
            # =====================================================

            logger.info("=" * 100)
            logger.info("PIPELINE STATISTICS")
            logger.info("=" * 100)

            logger.info(
                "Hybrid Search Time : %.2f sec",
                search_time,
            )

            logger.info(
                "Reranker Time : %.2f sec",
                rerank_time,
            )

            logger.info(
                "Context Builder Time : %.2f sec",
                context_time,
            )

            logger.info(
                "LLM Time : %.2f sec",
                llm_time,
            )

            logger.info(
                "Total Pipeline Time : %.2f sec",
                elapsed,
            )

            logger.info(
                "Average Similarity : %.4f",
                average_similarity,
            )

            logger.info(
                "Average Rerank Score : %.4f",
                average_rerank_score,
            )

            logger.info(
                "Average Keyword Score : %.4f",
                average_keyword_score,
            )

            logger.info(
                "Answer Confidence : %.2f%%",
                confidence,
            )

            logger.info(
                "Confidence Level : %s",
                confidence_level,
            )

            logger.info(
                "Total Chunks Used : %d",
                chunk_count,
            )

            logger.info("=" * 100)
            logger.info("RAG PIPELINE COMPLETED")
            logger.info("=" * 100)

            # =====================================================
            # Response
            # =====================================================

            return {
                "session_id": session_id,
                "answer": answer,
                "confidence": round(confidence, 2),
                "confidence_level": confidence_level,
                "average_similarity": round(
                    average_similarity,
                    4,
                ),
                "average_rerank_score": round(
                    average_rerank_score,
                    4,
                ),
                "average_keyword_score": round(
                    average_keyword_score,
                    4,
                ),
                "pipeline_time_seconds": round(
                    elapsed,
                    2,
                ),
                "search_time_seconds": round(
                    search_time,
                    2,
                ),
                "rerank_time_seconds": round(
                    rerank_time,
                    2,
                ),
                "context_time_seconds": round(
                    context_time,
                    2,
                ),
                "llm_time_seconds": round(
                    llm_time,
                    2,
                ),
                "total_chunks_used": chunk_count,
                "citations": citations,
            }

        except Exception:

            logger.exception(
                "RAG pipeline execution failed."
            )

            raise

