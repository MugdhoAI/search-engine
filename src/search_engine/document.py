from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class Document:
    """A searchable document identified by a stable integer ID."""

    document_id: int
    text: str
    metadata: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        if self.document_id < 0:
            raise ValueError("document_id must be non negative")
