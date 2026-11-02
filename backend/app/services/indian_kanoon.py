"""HTTP client for the official Indian Kanoon API."""

from dataclasses import dataclass
from typing import Any

import httpx

from app.config import get_settings


class IndianKanoonError(Exception):
    """A safe, user-facing error from the Indian Kanoon integration."""


@dataclass
class IndianKanoonClient:
    """Small API client; credentials stay on the backend."""

    timeout_seconds: float = 20.0

    def _headers(self) -> dict[str, str]:
        token = get_settings().indian_kanoon_api_token
        if not token:
            raise IndianKanoonError("Indian Kanoon API credentials are not configured.")
        return {"Authorization": f"Token {token}", "Accept": "application/json"}

    async def _post(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        base_url = get_settings().indian_kanoon_base_url.rstrip("/")
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    f"{base_url}{path}", headers=self._headers(), params=params
                )
                response.raise_for_status()
                payload = response.json()
        except IndianKanoonError:
            raise
        except httpx.TimeoutException as exc:
            raise IndianKanoonError("Indian Kanoon request timed out.") from exc
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in (401, 403):
                raise IndianKanoonError("Indian Kanoon rejected the configured credentials.") from exc
            raise IndianKanoonError(
                f"Indian Kanoon returned HTTP {exc.response.status_code}."
            ) from exc
        except (httpx.HTTPError, ValueError) as exc:
            raise IndianKanoonError("Could not read a valid response from Indian Kanoon.") from exc

        if not isinstance(payload, dict):
            raise IndianKanoonError("Indian Kanoon returned an unexpected response format.")
        return payload

    async def search(self, query: str, page: int) -> dict[str, Any]:
        """Search using Indian Kanoon's documented formInput and zero-based page."""
        return await self._post("/search/", {"formInput": query, "pagenum": page})

    async def get_document(self, document_id: str) -> dict[str, Any]:
        """Retrieve a full document by its Indian Kanoon document ID."""
        return await self._post(f"/doc/{document_id}/")
