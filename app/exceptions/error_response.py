from datetime import datetime
from typing import Any

from fastapi.responses import JSONResponse


def error_response(
    *,
    status_code: int,
    error: str,
    message: str,
    details: Any = None,
) -> JSONResponse:

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": error,
            "message": message,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )