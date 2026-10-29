import json
from urllib.error import URLError
from unittest.mock import patch

import pytest

from search_engine.query_assist import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    NebiusQueryAssistant,
    QueryAssistantError,
    _validate_suggestion,
    is_simple_query,
)


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def _response(content: str) -> FakeResponse:
    return FakeResponse({"choices": [{"message": {"content": content}}]})


def test_provider_uses_configured_defaults_and_rewrites_query() -> None:
    assistant = NebiusQueryAssistant(api_key="test-key")
    with patch(
        "search_engine.query_assist.urlopen",
        return_value=_response("  python indexing inverted index  "),
    ) as call:
        result = assistant.rewrite("how does python search work")

    assert result == "python indexing inverted index"
    request = call.call_args.args[0]
    payload = json.loads(request.data.decode("utf-8"))
    assert request.full_url == f"{DEFAULT_BASE_URL}/chat/completions"
    assert request.get_header("Authorization") == "Bearer test-key"
    assert payload["model"] == DEFAULT_MODEL
    assert payload["temperature"] == 0
    assert payload["max_tokens"] == 96


def test_provider_reads_environment_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NEBIUS_API_KEY", "env-key")
    monkeypatch.setenv("NEBIUS_BASE_URL", "https://example.test/v1/")
    monkeypatch.setenv("NEBIUS_MODEL", "nvidia/example")
    assistant = NebiusQueryAssistant()

    assert assistant.is_configured
    with patch(
        "search_engine.query_assist.urlopen", return_value=_response("search index")
    ) as call:
        assert assistant.rewrite("find search index") == "search index"
    assert call.call_args.args[0].full_url == "https://example.test/v1/chat/completions"
    assert json.loads(call.call_args.args[0].data.decode("utf-8"))["model"] == "nvidia/example"


def test_provider_requires_key() -> None:
    with pytest.raises(QueryAssistantError, match="NEBIUS_API_KEY"):
        NebiusQueryAssistant(api_key="").rewrite("search documents")


@pytest.mark.parametrize("query", ['"exact phrase"', "python AND search", "python OR search", ""])
def test_explicit_search_syntax_is_not_rewritten(query: str) -> None:
    assert not is_simple_query(query)
    with pytest.raises(QueryAssistantError):
        NebiusQueryAssistant(api_key="test-key").rewrite(query)


def test_transport_failure_has_safe_message() -> None:
    with patch(
        "search_engine.query_assist.urlopen",
        side_effect=URLError("secret endpoint details"),
    ):
        with pytest.raises(QueryAssistantError, match="temporarily unavailable") as error:
            NebiusQueryAssistant(api_key="test-key").rewrite("search documents")
    assert "secret endpoint details" not in str(error.value)


@pytest.mark.parametrize(
    "suggestion",
    ["", "  ", 'say "hello"', "search AND index", "x" * 241, None, ["not", "text"]],
)
def test_invalid_model_suggestions_are_rejected(suggestion: object) -> None:
    with pytest.raises(QueryAssistantError):
        _validate_suggestion(suggestion)


def test_model_response_shape_is_validated() -> None:
    assistant = NebiusQueryAssistant(api_key="test-key")
    with patch(
        "search_engine.query_assist.urlopen", return_value=FakeResponse({"unexpected": []})
    ):
        with pytest.raises(QueryAssistantError, match="unexpected response"):
            assistant.rewrite("search documents")
