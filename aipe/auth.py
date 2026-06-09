from __future__ import annotations

from typing import Optional

from fastapi import Header, HTTPException

from .config import expected_api_key, require_api_key


def verify_api_key(x_aipe_api_key: Optional[str] = Header(default=None)) -> None:
    """FastAPI dependency for optional local API-key auth."""
    if not require_api_key():
        return
    expected = expected_api_key()
    if not expected:
        raise HTTPException(status_code=500, detail="AIPE_API_KEY is not configured.")
    if x_aipe_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing AIPE API key.")
