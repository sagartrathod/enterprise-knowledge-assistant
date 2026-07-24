"""
API route modules.

Each route is responsible only for:
- URL registration
- Dependency injection
- Calling the controller

Business logic belongs in controllers/services.
"""

from app.api.routes.document_api import router as document_router
from app.api.routes.history_api import router as history_router
from app.api.routes.query_api import router as query_router
from app.api.routes.upload_api import router as upload_router

__all__ = [
    "upload_router",
    "query_router",
    "history_router",
    "document_router",
]