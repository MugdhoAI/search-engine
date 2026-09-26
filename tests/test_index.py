import pytest

from search_engine.document import Document
from search_engine.index import InvertedIndex


def test_index_stores_term_frequencies() -> None:
    index = InvertedIndex()
    index.add(Document(1, "Python Python search"))
    assert index.postings("python") == {1: 2}
    assert index.term_frequency("search", 1) == 1
    assert index.document_frequency("python") == 1


def test_duplicate_document_ids_are_rejected() -> None:
    index = InvertedIndex()
    index.add(Document(1, "first"))
    with pytest.raises(ValueError):
        index.add(Document(1, "second"))


def test_document_length_counts_searchable_terms() -> None:
    index = InvertedIndex()
    index.add(Document(1, "the quick fox"))
    assert index.document_length(1) == 2
