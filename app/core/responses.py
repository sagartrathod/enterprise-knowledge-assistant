from datetime import datetime


def error_response(
    *,
    status: str,
    error: str,
    message: str,
    details=None,
):

    return {
        "status": status,
        "error": error,
        "message": message,
        "details": details,
        "timestamp": datetime.utcnow().isoformat(),
    }