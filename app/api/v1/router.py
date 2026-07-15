# app/api/router.py
from fastapi import APIRouter
from app.api.v1.upload_controller import router as upload_router
from app.api.v1.document_controller import router as document_router
from app.api.v1.query_controller import router as query_router
from app.api.v1.history_controller import router as history_router

api_router = APIRouter(prefix="/v1")

# Route attachments
api_router.include_router(upload_router, tags=["Ingestion Pipeline"])
api_router.include_router(document_router, tags=["Document Management"])
api_router.include_router(query_router, tags=["RAG Interface Engine"])
api_router.include_router(history_router, tags=["Conversation Memory Tracking"])