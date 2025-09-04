from fastapi import HTTPException, Request, Security
from fastapi.security.api_key import APIKeyHeader

from broadie.config import settings

API_KEY_NAME = "Authorization"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def check_credentials(request: Request, api_key: str = Security(api_key_header)):
    # Todo: Improve this with more robust auth (OAuth, JWT, etc.) and for reuse in A2A comms
    if request.client.host in ("0.0.0.0", "localhost", "::1"):
        return True
    if api_key == f"Bearer {settings.API_KEY}":
        return True
    raise HTTPException(status_code=403, detail="Invalid or missing API key, you must provide it in the 'Authorization")
