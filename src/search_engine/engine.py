from collections.abc import Iterable, Mapping

from .document import Document
from .index import InvertedIndex
from .query import QueryParser
from .ranking import SearchResult, TfIdfRanker
from .tokenizer import Tokenizer


class SearchEngine:
    """Coordinate indexing, query parsing, and ranked retrieval."""

    def __init__(
        self,
        tokenizer: Tokenizer | None = None,
        ranker: TfIdfRanker | None = None,
    ) -> None:
        tokenizer = tokenizer or Tokenizer()
        self.index = InvertedIndex(tokenizer)
        self.parser = QueryParser(tokenizer)
        self.ranker = ranker or TfIdfRanker()

    def add(self, document_id: int, text: str, metadata: Mapping[str, str] | None = None) -> None:
        self.index.add(Document(document_id, text, metadata))

    def add_documents(self, documents: Iterable[Document]) -> None:
        self.index.add_many(documents)

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        if limit < 1:
            raise ValueError("limit must be positive")

        parsed = self.parser.parse(query)
        candidates = self.parser.candidates(parsed, self.index)
        return self.ranker.rank(parsed.terms, candidates, self.index)[:limit]

    def document(self, document_id: int) -> Document:
        return self.index.document(document_id)

    def count(self) -> int:
        return self.index.document_count()
