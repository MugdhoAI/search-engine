"""Extract searchable text from supported document uploads."""

from io import BytesIO
from pathlib import PurePath

from pypdf import PdfReader

SUPPORTED_EXTENSIONS = frozenset({".txt", ".md", ".pdf"})
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_PDF_PAGES = 100
MAX_EXTRACTED_CHARS = 200_000


def extract_text(filename: str, content: bytes) -> str:
    """Extract UTF-8 text or PDF text with explicit resource limits.

    The caller owns the uploaded bytes. This function never writes uploads to disk.
    """
    if not isinstance(filename, str) or not filename.strip():
        raise ValueError("A filename is required.")
    if not isinstance(content, bytes):
        raise TypeError("Document content must be bytes.")

    suffix = PurePath(filename).suffix.casefold()
    if suffix not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"Unsupported file type. Supported types: {supported}.")
    if not content:
        raise ValueError("The uploaded file is empty.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise ValueError("The file exceeds the 5 MiB upload limit.")

    if suffix in {".txt", ".md"}:
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("Text files must use UTF-8 encoding.") from exc
    else:
        text = _extract_pdf_text(content)

    text = text.strip()
    if not text:
        raise ValueError("No extractable text was found in this file.")
    if len(text) > MAX_EXTRACTED_CHARS:
        raise ValueError("Extracted text exceeds the 200,000 character limit.")
    return text


def _extract_pdf_text(content: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(content), strict=False)
        if len(reader.pages) > MAX_PDF_PAGES:
            raise ValueError("PDF files are limited to 100 pages.")

        parts: list[str] = []
        total_chars = 0
        for page in reader.pages:
            part = page.extract_text() or ""
            total_chars += len(part)
            if total_chars > MAX_EXTRACTED_CHARS:
                raise ValueError("Extracted text exceeds the 200,000 character limit.")
            parts.append(part)
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("The PDF could not be read. Check that it is a valid PDF.") from exc
    return "\n".join(parts)
