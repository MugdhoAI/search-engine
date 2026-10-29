"""Optional query rewriting through the Nebius Token Factory chat completions API.

The model may suggest a better lexical query; it never supplies search results.
"""

from __future__ import annotations

import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen



DEFAULT_BASE_URL = "https://api.tokenfactory.nebius.com/v1"
DEFAULT_MODEL = "nvidia/Nemotron-3.5-Super-VL"
MAX_QUERY_CHARS = 240
DEFAULT_TIMEOUT_SECONDS = 12.0


class QueryAssistantError(RuntimeError):
    """Raised when query assistance cannot return a safe query."""


def is_simple_query(query: str) -> bool:
    """Return whether the query is plain text rather than explicit search syntax."""
    if not isinstance(query, str) or not query.strip():
        return False
    return not any(mark in query for mark in ('"', "'")) and not re.search(
        r"\b(?:AND|OR)\b", query, flags=re.IGNORECASE
    )


def _validate_suggestion(suggestion: object) -> str:
    if not isinstance(suggestion, str):
        raise QueryAssistantError("The model did not return a text query.")

    cleaned = " ".join(suggestion.strip().strip('"').split())
    if not cleaned:
        raise QueryAssistantError("The model returned an empty query.")
    if len(cleaned) > MAX_QUERY_CHARS:
        raise QueryAssistantError("The suggested query is longer than the allowed limit.")
    if any(mark in cleaned for mark in ('"', "'", "\n", "\r")):
        raise QueryAssistantError("The suggested query contains unsupported syntax.")
    if re.search(r"\b(?:AND|OR)\b", cleaned, flags=re.IGNORECASE):
        raise QueryAssistantError("The suggested query contains Boolean operators.")
    return cleaned


class NebiusQueryAssistant:
    """Rewrite a plain-language query using an OpenAI-compatible hosted model."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.api_key = api_key if api_key is not None else os.getenv("NEBIUS_API_KEY", "")
        self.base_url = (base_url or os.getenv("NEBIUS_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.model = model or os.getenv("NEBIUS_MODEL") or DEFAULT_MODEL
        self.timeout = timeout

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key.strip())

    def rewrite(self, query: str) -> str:
        if not self.is_configured:
            raise QueryAssistantError(
                "Set NEBIUS_API_KEY in the app environment to enable AI query assistance."
            )
        if not is_simple_query(query):
            raise QueryAssistantError(
                "AI assistance is available for plain-text queries only. "
                "Boolean and quoted phrase queries are left unchanged."
            )

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Rewrite the user's search query into a concise lexical search query. "
                        "Use useful synonyms and specific terms when supported by the request. "
                        "Return only the query text, with no explanation, quotes, or Boolean "
                        "operators. Do not answer the question and do not invent documents."
                    ),
                },
                {"role": "user", "content": query.strip()},
            ],
            "temperature": 0,
            "max_tokens": 96,
        }
        request = Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise QueryAssistantError(
                f"Query assistance service returned HTTP {exc.code}."
            ) from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise QueryAssistantError(
                "Query assistance is temporarily unavailable. Try the original query."
            ) from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise QueryAssistantError("Query assistance returned an invalid response.") from exc

        try:
            suggestion = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise QueryAssistantError("Query assistance returned an unexpected response.") from exc

        return _validate_suggestion(suggestion)
