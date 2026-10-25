from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Document:
    """A searchable document identified by a stable integer ID."""

    document_id: int
    text: str
    metadata: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        if isinstance(self.document_id, bool) or not isinstance(self.document_id, int):
            raise TypeError("document_id must be an integer")
        if self.document_id < 0:
            raise ValueError("document_id must be non negative")
        if not isinstance(self.text, str):
            raise TypeError("text must be a string")
        if self.metadata is not None:
            if not isinstance(self.metadata, Mapping):
                raise TypeError("metadata must be a mapping of strings to strings")
            if any(
                not isinstance(key, str) or not isinstance(value, str)
                for key, value in self.metadata.items()
            ):
                raise TypeError("metadata must be a mapping of strings to strings")
