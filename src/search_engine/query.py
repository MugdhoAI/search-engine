from dataclasses import dataclass
from enum import Enum

from .index import InvertedIndex
from .tokenizer import Tokenizer


class QueryMode(str, Enum):
    ANY = "any"
    ALL = "all"


@dataclass(frozen=True, slots=True)
class Query:
    terms: tuple[str, ...]
    mode: QueryMode = QueryMode.ANY


class QueryParser:
    """Parse simple AND and OR query syntax."""

    def __init__(self, tokenizer: Tokenizer | None = None) -> None:
        self.tokenizer = tokenizer or Tokenizer()

    def parse(self, raw_query: str) -> Query:
        if not isinstance(raw_query, str):
            raise TypeError("query must be a string")

        upper = raw_query.upper()
        if " AND " in upper and " OR " in upper:
            raise ValueError("mixing AND and OR is not supported")

        mode = QueryMode.ALL if " AND " in upper else QueryMode.ANY
        cleaned = raw_query.replace(" AND ", " ").replace(" OR ", " ")
        terms = tuple(dict.fromkeys(self.tokenizer.normalize_query(cleaned)))
        return Query(terms=terms, mode=mode)

    def candidates(self, query: Query, index: InvertedIndex) -> set[int]:
        if not query.terms:
            return set()

        posting_sets = [set(index.postings(term)) for term in query.terms]
        if query.mode is QueryMode.ALL:
            return set.intersection(*posting_sets)
        return set.union(*posting_sets)
