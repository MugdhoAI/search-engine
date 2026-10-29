"""Evaluate retrieval quality and latency on a small, labeled synthetic corpus.

Run with: python scripts/evaluate_search.py
The dataset is intentionally small and synthetic; its scores are not a general benchmark.
"""

from __future__ import annotations

import json
import statistics
import time
from collections.abc import Sequence
from math import log2
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from search_engine.engine import SearchEngine  # noqa: E402


DOCUMENTS = (
    (1, "Python programming language syntax functions modules and packages"),
    (2, "Inverted index maps terms to documents for efficient information retrieval"),
    (3, "TF IDF ranks search documents using term frequency and inverse document frequency"),
    (4, "Boolean search supports AND OR queries and exact quoted phrase matching"),
    (5, "PDF document ingestion extracts text from uploaded files"),
    (6, "Streamlit web application uploads text markdown and PDF documents"),
    (7, "API security includes request timeouts input validation and safe error handling"),
    (8, "Evaluation measures precision recall reciprocal rank and normalized discounted gain"),
    (9, "Python testing uses pytest fixtures parameterized cases and deterministic results"),
    (10, "Search indexing tokenization removes stop words and normalizes text"),
)

# Relevant document IDs are manually assigned for this fixed, synthetic dataset.
QUERIES = (
    ("python language", {1, 9}),
    ("inverted index retrieval", {2, 10}),
    ("tf idf ranking", {3}),
    ("boolean phrase query", {4}),
    ("PDF upload document", {5, 6}),
    ("input validation timeout security", {7}),
    ("precision recall evaluation", {8}),
    ("tokenization stop words", {10}),
)

K = 5
LATENCY_REPEATS = 40


def precision_at_k(results: Sequence[int], relevant: set[int], k: int) -> float:
    return sum(document_id in relevant for document_id in results[:k]) / k


def recall_at_k(results: Sequence[int], relevant: set[int], k: int) -> float:
    if not relevant:
        return 0.0
    return sum(document_id in relevant for document_id in results[:k]) / len(relevant)


def reciprocal_rank(results: Sequence[int], relevant: set[int]) -> float:
    for rank, document_id in enumerate(results, start=1):
        if document_id in relevant:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(results: Sequence[int], relevant: set[int], k: int) -> float:
    dcg = sum(
        1.0 / log2(rank + 1)
        for rank, document_id in enumerate(results[:k], start=1)
        if document_id in relevant
    )
    ideal_relevant = min(len(relevant), k)
    ideal_dcg = sum(1.0 / log2(rank + 1) for rank in range(1, ideal_relevant + 1))
    return dcg / ideal_dcg if ideal_dcg else 0.0


def percentile(values: list[float], percentage: float) -> float:
    ordered = sorted(values)
    index = round((len(ordered) - 1) * percentage)
    return ordered[index]


def evaluate() -> dict[str, object]:
    engine = SearchEngine()
    for document_id, text in DOCUMENTS:
        engine.add(document_id, text)

    per_query: list[dict[str, object]] = []
    precisions: list[float] = []
    recalls: list[float] = []
    reciprocal_ranks: list[float] = []
    ndcgs: list[float] = []
    latencies_ms: list[float] = []

    for query, relevant in QUERIES:
        results = [item.document_id for item in engine.search(query, limit=K)]
        precision = precision_at_k(results, relevant, K)
        recall = recall_at_k(results, relevant, K)
        rr = reciprocal_rank(results, relevant)
        ndcg = ndcg_at_k(results, relevant, K)
        precisions.append(precision)
        recalls.append(recall)
        reciprocal_ranks.append(rr)
        ndcgs.append(ndcg)

        for _ in range(LATENCY_REPEATS):
            started = time.perf_counter()
            engine.search(query, limit=K)
            latencies_ms.append((time.perf_counter() - started) * 1000)

        per_query.append(
            {
                "query": query,
                "relevant_document_ids": sorted(relevant),
                "returned_document_ids": results,
                "precision_at_5": round(precision, 4),
                "recall_at_5": round(recall, 4),
                "reciprocal_rank": round(rr, 4),
                "ndcg_at_5": round(ndcg, 4),
            }
        )

    return {
        "dataset": {
            "type": "synthetic",
            "document_count": len(DOCUMENTS),
            "query_count": len(QUERIES),
            "relevance_labels": "manually assigned in scripts/evaluate_search.py",
        },
        "metrics": {
            "mean_precision_at_5": round(statistics.mean(precisions), 4),
            "mean_recall_at_5": round(statistics.mean(recalls), 4),
            "mean_reciprocal_rank": round(statistics.mean(reciprocal_ranks), 4),
            "mean_ndcg_at_5": round(statistics.mean(ndcgs), 4),
        },
        "latency": {
            "measurement": "in-process search() calls; includes query parsing and ranking",
            "repeats_per_query": LATENCY_REPEATS,
            "samples": len(latencies_ms),
            "p50_ms": round(percentile(latencies_ms, 0.50), 4),
            "p95_ms": round(percentile(latencies_ms, 0.95), 4),
            "note": "Single-run local measurements; not a cross-machine or production benchmark.",
        },
        "queries": per_query,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
