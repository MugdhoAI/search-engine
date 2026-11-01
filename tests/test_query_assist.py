import json
from unittest.mock import call as mock_call
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import pytest

from search_engine.query_assist import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    GeminiQueryAssistant,
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

    def read(self, amount: int = -1) -> bytes:
        payload = json.dumps(self.payload).encode("utf-8")
        return payload if amount < 0 else payload[:amount]


def _response(content: str) -> FakeResponse:
    return FakeResponse({"choices": [{"message": {"content": content}}]})


def _http_error(status_code: int) -> HTTPError:
    return HTTPError(
        "https://provider.example/private",
        status_code,
        "provider error",
        {"Authorization": "secret-header"},
        None,
    )


def test_provider_uses_configured_defaults_and_rewrites_query() -> None:
    assistant = GeminiQueryAssistant(api_key="test-key")
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


@pytest.mark.parametrize("status_code", [503, 429])
def test_provider_retries_retryable_status_then_succeeds(status_code: int) -> None:
    with (
        patch(
            "search_engine.query_assist.urlopen",
            side_effect=[_http_error(status_code), _response("search index")],
        ) as request,
        patch("search_engine.query_assist.time.sleep") as sleep,
    ):
        result = GeminiQueryAssistant(api_key="test-key").rewrite("search documents")

    assert result == "search index"
    assert request.call_count == 2
    assert all(call.kwargs["timeout"] == 12.0 for call in request.call_args_list)
    assert sleep.call_args_list == [mock_call(1.0)]


def test_provider_stops_after_three_retryable_failures() -> None:
    with (
        patch(
            "search_engine.query_assist.urlopen",
            side_effect=[_http_error(503), _http_error(429), _http_error(503)],
        ) as request,
        patch("search_engine.query_assist.time.sleep") as sleep,
        pytest.raises(QueryAssistantError, match="temporarily unavailable") as error,
    ):
        GeminiQueryAssistant(api_key="test-key").rewrite("search documents")

    assert request.call_count == 3
    assert sleep.call_args_list == [mock_call(1.0), mock_call(2.0)]
    assert "private" not in str(error.value)
    assert "secret-header" not in str(error.value)


def test_provider_does_not_retry_non_retryable_http_status() -> None:
    with (
        patch(
            "search_engine.query_assist.urlopen", side_effect=_http_error(401)
        ) as request,
        patch("search_engine.query_assist.time.sleep") as sleep,
        pytest.raises(QueryAssistantError, match="HTTP 401"),
    ):
        GeminiQueryAssistant(api_key="test-key").rewrite("search documents")

    request.assert_called_once()
    sleep.assert_not_called()


def test_provider_reads_environment_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "env-key")
    monkeypatch.setenv("GEMINI_BASE_URL", "https://example.test/v1/")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test")
    assistant = GeminiQueryAssistant()

    assert assistant.is_configured
    with patch(
        "search_engine.query_assist.urlopen", return_value=_response("search index")
    ) as call:
        assert assistant.rewrite("find search index") == "search index"
    assert call.call_args.args[0].full_url == "https://example.test/v1/chat/completions"
    assert json.loads(call.call_args.args[0].data.decode("utf-8"))["model"] == "gemini-test"


def test_provider_requires_key() -> None:
    with pytest.raises(QueryAssistantError, match="GEMINI_API_KEY"):
        GeminiQueryAssistant(api_key="").rewrite("search documents")


@pytest.mark.parametrize("query", ['"exact phrase"', "python AND search", "python OR search", ""])
def test_explicit_search_syntax_is_not_rewritten(query: str) -> None:
    assert not is_simple_query(query)
    with pytest.raises(QueryAssistantError):
        GeminiQueryAssistant(api_key="test-key").rewrite(query)


def test_transport_failure_has_safe_message() -> None:
    with (
        patch(
            "search_engine.query_assist.urlopen",
            side_effect=URLError("secret endpoint details"),
        ),
        pytest.raises(QueryAssistantError, match="temporarily unavailable") as error,
    ):
        GeminiQueryAssistant(api_key="test-key").rewrite("search documents")
    assert "secret endpoint details" not in str(error.value)


@pytest.mark.parametrize(
    "suggestion",
    ["", "  ", 'say "hello"', "search AND index", "x" * 241, None, ["not", "text"]],
)
def test_invalid_model_suggestions_are_rejected(suggestion: object) -> None:
    with pytest.raises(QueryAssistantError):
        _validate_suggestion(suggestion)


def test_model_response_shape_is_validated() -> None:
    assistant = GeminiQueryAssistant(api_key="test-key")
    with (
        patch(
            "search_engine.query_assist.urlopen", return_value=FakeResponse({"unexpected": []})
        ),
        pytest.raises(QueryAssistantError, match="unexpected response"),
    ):
        assistant.rewrite("search documents")


def test_provider_rejects_overlong_input_before_network_call() -> None:
    assistant = GeminiQueryAssistant(api_key="test-key")
    with (
        patch("search_engine.query_assist.urlopen") as call,
        pytest.raises(QueryAssistantError, match="1000 characters"),
    ):
        assistant.rewrite("x" * 1001)
    call.assert_not_called()


def test_provider_rejects_oversized_response() -> None:
    from search_engine.query_assist import MAX_RESPONSE_BYTES

    class LargeResponse(FakeResponse):
        def read(self, amount: int = -1) -> bytes:
            assert amount == MAX_RESPONSE_BYTES + 1
            return b"x" * amount

    with (
        patch("search_engine.query_assist.urlopen", return_value=LargeResponse({})),
        pytest.raises(QueryAssistantError, match="size limit"),
    ):
        GeminiQueryAssistant(api_key="test-key").rewrite("search documents")
