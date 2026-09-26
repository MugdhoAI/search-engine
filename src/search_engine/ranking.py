from dataclasses import dataclass
from math import log
from collections.abc import Iterable

from .index import InvertedIndex


@dataclass(frozen=True, slots=True)
class SearchResult:
    document_id: int
    score: float


class TfIdfRanker:
    """Rank documents with normalized TF IDF scores."""

    def score(self, query_terms: Iterable[str], document_id: int, index: InvertedIndex) -> float:
        terms = list(dict.fromkeys(query_terms))
        if not terms or index.document_count() == 0:
            return 0.0

        document_length = index.document_length(document_id)
        if document_length == 0:
            return 0.0

        score = 0.0
        total_documents = index.document_count()

        for term in terms:
            frequency = index.term_frequency(term, document_id)
            if frequency == 0:
                continue
            document_frequency = index.document_frequency(term)
            if document_frequency == 0:
                continue
            tf = frequency / document_length
            idf = log((total_documents + 1) / (document_frequency + 1)) + 1.0
            score += tf * idf

        return score

    def rank(
        self,
        query_terms: Iterable[str],
        candidates: Iterable[int],
        index: InvertedIndex,
    ) -> list[SearchResult]:
        results = [
            SearchResult(document_id, self.score(query_terms, document_id, index))
            for document_id in candidates
        ]
        results = [result for result in results if result.score > 0.0]
        return sorted(results, key=lambda result: (-result.score, result.document_id))
