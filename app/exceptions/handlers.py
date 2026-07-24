# app/exceptions/handlers.py

from __future__ import annotations

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi.exceptions import RequestValidationError

from app.core.logger import logger
from app.exceptions.custom_exceptions import AppException
from app.exceptions.error_response import error_response


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register global exception handlers.

    Handles:
    - Custom application exceptions
    - FastAPI HTTP exceptions
    - Request validation errors
    - Unhandled exceptions
    """

    # ==========================================================
    # Custom Application Exception
    # ==========================================================

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException,
    ):

        request_id = getattr(
            request.state,
            "request_id",
            "N/A",
        )

        logger.error(
            "[%s] %s %s | %s",
            request_id,
            request.method,
            request.url.path,
            exc.message,
        )

        return error_response(
            status_code=exc.status_code,
            error=exc.__class__.__name__,
            message=exc.message,
            details=exc.details,
        )

    # ==========================================================
    # HTTP Exception
    # ==========================================================

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ):

        request_id = getattr(
            request.state,
            "request_id",
            "N/A",
        )

        logger.warning(
            "[%s] %s %s | HTTP %s | %s",
            request_id,
            request.method,
            request.url.path,
            exc.status_code,
            exc.detail,
        )

        return error_response(
            status_code=exc.status_code,
            error="HTTPException",
            message=str(exc.detail),
        )

    # ==========================================================
    # Validation Exception
    # ==========================================================

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):

        request_id = getattr(
            request.state,
            "request_id",
            "N/A",
        )

        logger.warning(
            "[%s] Validation Error | %s %s",
            request_id,
            request.method,
            request.url.path,
        )

        logger.warning(
            exc.errors(),
        )

        return error_response(
            status_code=422,
            error="ValidationError",
            message="Validation failed.",
            details=exc.errors(),
        )

    # ==========================================================
    # Unexpected Exception
    # ==========================================================

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception,
    ):

        request_id = getattr(
            request.state,
            "request_id",
            "N/A",
        )

        logger.exception(
            "[%s] Unhandled Exception | %s %s",
            request_id,
            request.method,
            request.url.path,
        )

        return error_response(
            status_code=500,
            error="InternalServerError",
            message="Internal server error.",
        )