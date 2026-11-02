"""Provider-neutral case analysis through an OpenAI-compatible chat endpoint."""

import json
from typing import Any

import httpx

from app.config import get_settings
from app.schemas.analysis import CaseAnalysis


class CaseAnalysisError(Exception):
    """Safe error raised when case analysis cannot be completed."""


SYSTEM_PROMPT = """You extract research inputs from a lawyer's case description.
Do not give legal advice, decide the merits, state what current Indian law is,
or add facts that the user did not provide. Return only a JSON object with
exactly these keys: case_category, facts, legal_issues, legal_terminology,
search_queries. Use concise strings. Facts must be traceable to the description.
Frame legal issues as questions or neutral issue labels. Search queries should
be short phrases suitable for searching judgments. If a category or issue is
unclear, use \"Information unavailable\" for that field rather than guessing.
The output must be valid JSON and contain no markdown fences."""


class CaseAnalyzer:
    """Calls a configured OpenAI-compatible provider and validates its JSON."""

    async def analyze(self, description: str) -> CaseAnalysis:
        settings = get_settings()
        if not settings.llm_api_base_url or not settings.llm_api_key or not settings.llm_model:
            raise CaseAnalysisError("LLM provider is not configured.")

        endpoint = settings.llm_api_base_url.rstrip("/")
        if not endpoint.endswith("/chat/completions"):
            endpoint += "/chat/completions"
        headers = {"Authorization": f"Bearer {settings.llm_api_key}"}
        body = {
            "model": settings.llm_model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": description},
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
                response = await client.post(endpoint, headers=headers, json=body)
                response.raise_for_status()
                payload = response.json()
            content = self._response_content(payload)
            parsed = json.loads(content)
            return CaseAnalysis.model_validate(parsed)
        except httpx.TimeoutException as exc:
            raise CaseAnalysisError("LLM request timed out.") from exc
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in (401, 403):
                raise CaseAnalysisError("LLM provider rejected the configured credentials.") from exc
            raise CaseAnalysisError("LLM provider could not complete case analysis.") from exc
        except httpx.HTTPError as exc:
            raise CaseAnalysisError("Could not connect to the configured LLM provider.") from exc
        except (ValueError, KeyError, TypeError) as exc:
            raise CaseAnalysisError("LLM provider returned an invalid analysis format.") from exc

    @staticmethod
    def _response_content(payload: Any) -> str:
        """Extract the standard chat-completion message content safely."""
        try:
            content = payload["choices"][0]["message"]["content"]
        except (TypeError, KeyError, IndexError) as exc:
            raise ValueError("Missing chat completion content") from exc
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Empty chat completion content")
        return content.strip()
