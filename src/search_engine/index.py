from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping

from .document import Document
from .tokenizer import Tokenizer


class InvertedIndex:
    """Map terms to documents and term frequencies."""

    def __init__(self, tokenizer: Tokenizer | None = None) -> None:
        self.tokenizer = tokenizer or Tokenizer()
        self._postings: dict[str, dict[int, int]] = defaultdict(dict)
        self._documents: dict[int, Document] = {}
        self._lengths: dict[int, int] = {}

    def add(self, document: Document) -> None:
        if document.document_id in self._documents:
            raise ValueError(f"document {document.document_id} already exists")
        terms = self.tokenizer.tokenize(document.text)
        frequencies = Counter(terms)
        self._documents[document.document_id] = document
        self._lengths[document.document_id] = len(terms)
        for term, frequency in frequencies.items():
            self._postings[term][document.document_id] = frequency

    def add_many(self, documents: Iterable[Document]) -> None:
        for document in documents:
            self.add(document)

    def postings(self, term: str) -> Mapping[int, int]:
        return dict(self._postings.get(term.casefold(), {}))

    def terms(self) -> list[str]:
        return sorted(self._postings)

    def document(self, document_id: int) -> Document:
        return self._documents[document_id]

    def documents(self) -> list[Document]:
        return list(self._documents.values())

    def document_count(self) -> int:
        return len(self._documents)

    def document_frequency(self, term: str) -> int:
        return len(self._postings.get(term.casefold(), {}))

    def term_frequency(self, term: str, document_id: int) -> int:
        return self._postings.get(term.casefold(), {}).get(document_id, 0)

    def document_length(self, document_id: int) -> int:
        return self._lengths[document_id]
