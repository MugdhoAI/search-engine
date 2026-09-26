import pytest

from search_engine.engine import SearchEngine
from search_engine.query import QueryMode, QueryParser


@pytest.fixture
def engine() -> SearchEngine:
    result = SearchEngine()
    result.add(1, "Python programming language")
    result.add(2, "Python search engine implementation")
    result.add(3, "C programming language")
    result.add(4, "Search systems use an inverted index")
    return result


def test_search_returns_matching_documents(engine: SearchEngine) -> None:
    results = engine.search("python")
    assert {result.document_id for result in results} == {1, 2}


def test_search_is_ranked(engine: SearchEngine) -> None:
    results = engine.search("search")
    assert results[0].document_id == 2


def test_and_query_requires_all_terms(engine: SearchEngine) -> None:
    assert [r.document_id for r in engine.search("python AND search")] == [2]


def test_lowercase_and_is_supported(engine: SearchEngine) -> None:
    assert [r.document_id for r in engine.search("python and search")] == [2]


def test_or_query_returns_union(engine: SearchEngine) -> None:
    assert {r.document_id for r in engine.search("python OR language")} == {1, 2, 3}


def test_lowercase_or_is_supported(engine: SearchEngine) -> None:
    assert {r.document_id for r in engine.search("python or language")} == {1, 2, 3}


def test_phrase_query_requires_adjacent_terms(engine: SearchEngine) -> None:
    results = engine.search('"search engine"')
    assert [r.document_id for r in results] == [2]


def test_phrase_query_can_be_combined_with_terms(engine: SearchEngine) -> None:
    results = engine.search('"programming language" python')
    assert [r.document_id for r in results] == [1]


def test_unmatched_quote_is_rejected() -> None:
    with pytest.raises(ValueError):
        QueryParser().parse('"python search')


def test_empty_query_returns_no_results(engine: SearchEngine) -> None:
    assert engine.search("") == []


def test_limit_must_be_positive(engine: SearchEngine) -> None:
    with pytest.raises(ValueError):
        engine.search("python", 0)


def test_mixed_boolean_operators_are_rejected() -> None:
    with pytest.raises(ValueError):
        QueryParser().parse("python AND search OR engine")


def test_query_parser_exposes_mode() -> None:
    assert QueryParser().parse("python AND search").mode is QueryMode.ALL
