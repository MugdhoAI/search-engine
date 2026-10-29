from scripts.evaluate_search import (
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


def test_precision_at_k_counts_relevant_results_and_uses_k_denominator() -> None:
    assert precision_at_k([1, 2, 3], {2, 3}, 5) == 0.4


def test_recall_at_k_uses_all_relevant_documents() -> None:
    assert recall_at_k([1, 2, 3], {2, 3, 4}, 3) == 2 / 3


def test_reciprocal_rank_uses_first_relevant_result() -> None:
    assert reciprocal_rank([1, 2, 3], {2, 3}) == 0.5


def test_reciprocal_rank_is_zero_when_no_relevant_result() -> None:
    assert reciprocal_rank([1, 2, 3], {4}) == 0.0


def test_ndcg_rewards_relevant_results_earlier() -> None:
    relevant = {2, 3}
    assert ndcg_at_k([2, 3, 1], relevant, 3) == 1.0
    assert ndcg_at_k([1, 2, 3], relevant, 3) < 1.0


def test_ndcg_handles_empty_relevance_set() -> None:
    assert ndcg_at_k([1, 2], set(), 2) == 0.0
