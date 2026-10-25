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


@pytest.mark.parametrize("document_id", [True, 1.5, "1"])
def test_document_rejects_non_integer_ids(document_id: object) -> None:
    with pytest.raises(TypeError, match="document_id must be an integer"):
        Document(document_id, "text")  # type: ignore[arg-type]


def test_document_rejects_non_string_text() -> None:
    with pytest.raises(TypeError, match="text must be a string"):
        Document(1, None)  # type: ignore[arg-type]


@pytest.mark.parametrize("metadata", [{"source": 1}, ["source"], "source"])
def test_document_rejects_invalid_metadata(metadata: object) -> None:
    with pytest.raises(TypeError, match="metadata must be a mapping of strings to strings"):
        Document(1, "text", metadata)  # type: ignore[arg-type]


def test_document_length_counts_searchable_terms() -> None:
    index = InvertedIndex()
    index.add(Document(1, "the quick fox"))
    assert index.document_length(1) == 2
