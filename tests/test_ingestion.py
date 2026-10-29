from io import BytesIO

import pytest
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from search_engine.ingestion import (
    MAX_EXTRACTED_CHARS,
    MAX_UPLOAD_BYTES,
    extract_text,
)


def _pdf_with_text(text: str) -> bytes:
    writer = PdfWriter()
    page = writer.add_blank_page(width=300, height=300)
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    font_ref = writer._add_object(font)
    page[NameObject("/Resources")] = DictionaryObject(
        {
            NameObject("/Font"): DictionaryObject({NameObject("/F1"): font_ref}),
        }
    )
    stream = DecodedStreamObject()
    stream.set_data(f"BT /F1 12 Tf 50 250 Td ({text}) Tj ET".encode("ascii"))
    page[NameObject("/Contents")] = writer._add_object(stream)
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def test_extracts_utf8_text_and_removes_bom() -> None:
    assert extract_text("notes.txt", b"\xef\xbb\xbfHello\nworld ") == "Hello\nworld"


def test_extracts_markdown() -> None:
    assert extract_text("guide.MD", b"# Search\n\nUse an inverted index.") == (
        "# Search\n\nUse an inverted index."
    )


def test_extracts_text_from_pdf() -> None:
    assert extract_text("notes.pdf", _pdf_with_text("Search works")) == "Search works"


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


def test_rejects_excessive_extracted_text() -> None:
    with pytest.raises(ValueError, match="200,000 character"):
        extract_text("notes.txt", b"x" * (MAX_EXTRACTED_CHARS + 1))


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


def test_rejects_pdf_over_page_limit() -> None:
    writer = PdfWriter()
    for _ in range(101):
        writer.add_blank_page(width=72, height=72)
    output = BytesIO()
    writer.write(output)

    with pytest.raises(ValueError, match="limited to 100 pages"):
        extract_text("large.pdf", output.getvalue())


def test_rejects_invalid_pdf() -> None:
    with pytest.raises(ValueError, match="valid PDF"):
        extract_text("broken.pdf", b"not a PDF")
