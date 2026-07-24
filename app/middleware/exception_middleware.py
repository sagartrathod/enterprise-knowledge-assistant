from __future__ import annotations

import traceback

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.exceptions import AppException
from app.core.logger import logger
from app.core.responses import error_response


class ExceptionMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):

        try:

            return await call_next(request)

        except AppException as exc:

            logger.error("=" * 100)
            logger.error("APPLICATION EXCEPTION")
            logger.error("URL      : %s", request.url.path)
            logger.error("METHOD   : %s", request.method)
            logger.error("ERROR    : %s", exc.error)
            logger.error("MESSAGE  : %s", exc.message)
            logger.error("=" * 100)

            return JSONResponse(
                status_code=exc.status_code,
                content=error_response(
                    status="failed",
                    error=exc.error,
                    message=exc.message,
                    details=exc.details,
                ),
            )

        except Exception as exc:

            logger.exception("=" * 100)
            logger.exception("UNHANDLED EXCEPTION")
            logger.exception("URL      : %s", request.url.path)
            logger.exception("METHOD   : %s", request.method)
            logger.exception(traceback.format_exc())
            logger.exception("=" * 100)

            return JSONResponse(
                status_code=500,
                content=error_response(
                    status="failed",
                    error="Internal Server Error",
                    message=str(exc),
                ),
            )