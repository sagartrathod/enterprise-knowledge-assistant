"""
API package.

Contains:
- Global API router
- Dependency injection
- Route modules
"""

from app.api.router import api_router

__all__ = [
    "api_router",
]