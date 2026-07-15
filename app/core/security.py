import secrets
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def validate_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Optional security dependency guarding endpoints against unauthorized access.
    Can be used by adding `Depends(validate_api_key)` to your routes.
    """
    # If app env is development and a secret key is missing, bypass for local iterations
    if settings.APP_ENV == "development" and not api_key:
        return "development-bypass-user"
        
    if not api_key or not secrets.compare_digest(api_key, settings.SECRET_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-KEY security credential.",
        )
    return api_key