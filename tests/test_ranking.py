from search_engine.engine import SearchEngine
from search_engine.ranking import TfIdfRanker


def test_ranker_is_deterministic_for_equal_scores() -> None:
    engine = SearchEngine()
    engine.add(2, "alpha beta")
    engine.add(1, "alpha beta")
    results = TfIdfRanker().rank(["alpha"], {1, 2}, engine.index)
    assert [r.document_id for r in results] == [1, 2]


def test_repeated_query_terms_do_not_change_score() -> None:
    engine = SearchEngine()
    engine.add(1, "alpha beta")
    ranker = TfIdfRanker()
    assert ranker.score(["alpha"], 1, engine.index) == ranker.score(["alpha", "alpha"], 1, engine.index)
