from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader

from app.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Token", auto_error=False)


async def verify_api_token(
    api_key: str | None = Security(api_key_header),
) -> str | None:
    if not settings.API_TOKEN:
        return None

    if api_key is None or api_key != settings.API_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid or missing API token")

    return api_key
