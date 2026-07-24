from __future__ import annotations

import time
import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


# ==========================================================
# Context Variables
# ==========================================================

request_id_ctx: ContextVar[str] = ContextVar(
    "request_id",
    default="-",
)

request_start_time_ctx: ContextVar[float] = ContextVar(
    "request_start_time",
    default=0.0,
)

session_id_ctx: ContextVar[str] = ContextVar(
    "session_id",
    default="-",
)


# ==========================================================
# Middleware
# ==========================================================

class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Stores request-specific values in ContextVars.

    Available globally during the request lifecycle.
    """

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):

        request_id = str(uuid.uuid4())

        request_id_ctx.set(request_id)

        request_start_time_ctx.set(
            time.perf_counter()
        )

        session_id = (
            request.headers.get("X-Session-Id")
            or request.query_params.get("session_id")
            or "-"
        )

        session_id_ctx.set(session_id)

        response = await call_next(request)

        response.headers["X-Request-ID"] = request_id

        return response


# ==========================================================
# Helper Functions
# ==========================================================

def get_request_id() -> str:
    return request_id_ctx.get()


def get_session_id() -> str:
    return session_id_ctx.get()


def get_request_start_time() -> float:
    return request_start_time_ctx.get()