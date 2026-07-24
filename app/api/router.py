from fastapi import APIRouter

from app.api.routes.document_api import router as document_router
from app.api.routes.history_api import router as history_router
from app.api.routes.query_api import router as query_router
from app.api.routes.upload_api import router as upload_router

api_router = APIRouter(prefix="/v1")

api_router.include_router(upload_router)
api_router.include_router(query_router)
api_router.include_router(history_router)
api_router.include_router(document_router)