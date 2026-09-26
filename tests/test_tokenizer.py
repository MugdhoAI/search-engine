import pytest

from search_engine.tokenizer import Tokenizer


def test_tokenizer_normalizes_and_removes_stop_words() -> None:
    assert Tokenizer().tokenize("The Quick, brown fox!") == ["quick", "brown", "fox"]


def test_tokenizer_keeps_apostrophes() -> None:
    assert Tokenizer().tokenize("Python's search") == ["python's", "search"]


def test_tokenizer_rejects_non_strings() -> None:
    with pytest.raises(TypeError):
        Tokenizer().tokenize(None)  # type: ignore[arg-type]
