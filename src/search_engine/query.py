import re
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
    phrases: tuple[tuple[str, ...], ...] = ()


class QueryParser:
    """Parse simple boolean and quoted phrase queries."""

    _PHRASE_PATTERN = re.compile(r'"([^"]+)"')

    def __init__(self, tokenizer: Tokenizer | None = None) -> None:
        self.tokenizer = tokenizer or Tokenizer()

    def parse(self, raw_query: str) -> Query:
        if not isinstance(raw_query, str):
            raise TypeError("query must be a string")

        if raw_query.count('"') % 2:
            raise ValueError("unmatched quote in query")

        has_and = bool(re.search(r"\bAND\b", raw_query, re.IGNORECASE))
        has_or = bool(re.search(r"\bOR\b", raw_query, re.IGNORECASE))
        if has_and and has_or:
            raise ValueError("mixing AND and OR is not supported")

        phrases = tuple(
            tuple(self.tokenizer.tokenize(match.group(1)))
            for match in self._PHRASE_PATTERN.finditer(raw_query)
        )
        cleaned = self._PHRASE_PATTERN.sub(" ", raw_query)
        cleaned = re.sub(r"\b(?:AND|OR)\b", " ", cleaned, flags=re.IGNORECASE)
        terms = tuple(dict.fromkeys(self.tokenizer.normalize_query(cleaned)))
        phrase_terms = tuple(term for phrase in phrases for term in phrase)
        all_terms = tuple(dict.fromkeys((*terms, *phrase_terms)))

        mode = QueryMode.ALL if has_and or (phrases and terms and not has_or) else QueryMode.ANY
        return Query(terms=all_terms, mode=mode, phrases=phrases)

    def candidates(self, query: Query, index: InvertedIndex) -> set[int]:
        if not query.terms:
            return set()

        posting_sets = [set(index.postings(term)) for term in query.terms]
        if query.mode is QueryMode.ALL:
            candidates = set.intersection(*posting_sets)
        else:
            candidates = set.union(*posting_sets)

        for phrase in query.phrases:
            if phrase:
                candidates = {
                    document_id
                    for document_id in candidates
                    if self._contains_phrase(
                        self.tokenizer.tokenize(index.document(document_id).text),
                        phrase,
                    )
                }
        return candidates

    @staticmethod
    def _contains_phrase(tokens: list[str], phrase: tuple[str, ...]) -> bool:
        size = len(phrase)
        return any(tokens[i : i + size] == list(phrase) for i in range(len(tokens) - size + 1))
