from __future__ import annotations

import time
import logging
import os

from logging.handlers import RotatingFileHandler

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.logger import logger

os.makedirs("logs", exist_ok=True)

access_logger = logging.getLogger("access")

access_logger.setLevel(logging.INFO)

access_logger.handlers.clear()

formatter = logging.Formatter(
    "%(asctime)s | %(message)s"
)

handler = RotatingFileHandler(
    "logs/access.log",
    maxBytes=10 * 1024 * 1024,
    backupCount=10,
    encoding="utf-8",
)

handler.setFormatter(formatter)

access_logger.addHandler(handler)

access_logger.propagate = False


class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        start = time.perf_counter()

        logger.info("=" * 100)

        logger.info(
            "Incoming Request : %s %s",
            request.method,
            request.url.path,
        )

        try:

            response = await call_next(request)

            duration = (
                time.perf_counter() - start
            ) * 1000

            logger.info(
                "Completed %s %s -> %s (%.2f ms)",
                request.method,
                request.url.path,
                response.status_code,
                duration,
            )

            access_logger.info(
                "%s | %s | %s | %s | %.2f ms",
                request.client.host if request.client else "-",
                request.method,
                request.url.path,
                response.status_code,
                duration,
            )

            logger.info("=" * 100)

            return response

        except Exception:

            duration = (
                time.perf_counter() - start
            ) * 1000

            logger.exception(
                "Unhandled Exception %s %s (%.2f ms)",
                request.method,
                request.url.path,
                duration,
            )

            raise