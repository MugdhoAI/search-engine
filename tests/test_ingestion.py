from io import BytesIO

import pytest
from pypdf import PdfWriter

from search_engine.ingestion import (
    MAX_UPLOAD_BYTES,
    extract_text,
)


def test_extracts_utf8_text_and_removes_bom() -> None:
    assert extract_text("notes.txt", b"\xef\xbb\xbfHello\nworld ") == "Hello\nworld"


def test_extracts_markdown() -> None:
    assert extract_text("guide.MD", b"# Search\n\nUse an inverted index.") == (
        "# Search\n\nUse an inverted index."
    )


@pytest.mark.parametrize("filename", ["notes.docx", "archive.zip", "no-extension"])
def test_rejects_unsupported_extensions(filename: str) -> None:
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_text(filename, b"content")


def test_rejects_empty_upload() -> None:
    with pytest.raises(ValueError, match="empty"):
        extract_text("notes.txt", b"")


def test_rejects_oversized_upload() -> None:
    with pytest.raises(ValueError, match="5 MiB"):
        extract_text("notes.txt", b"x" * (MAX_UPLOAD_BYTES + 1))


def test_rejects_non_utf8_text() -> None:
    with pytest.raises(ValueError, match="UTF-8"):
        extract_text("notes.txt", b"\xff\xfe")


def test_rejects_pdf_with_no_extractable_text() -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    output = BytesIO()
    writer.write(output)

    with pytest.raises(ValueError, match="No extractable text"):
        extract_text("blank.pdf", output.getvalue())


def test_rejects_invalid_pdf() -> None:
    with pytest.raises(ValueError, match="valid PDF"):
        extract_text("broken.pdf", b"not a PDF")
