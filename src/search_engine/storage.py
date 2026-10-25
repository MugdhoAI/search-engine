import json
from pathlib import Path

from .engine import SearchEngine


class JsonStore:
    """Persist source documents as portable JSON."""

    def save(self, engine: SearchEngine, path: str | Path) -> None:
        target = Path(path)
        payload = [
            {
                "document_id": document.document_id,
                "text": document.text,
                "metadata": dict(document.metadata or {}),
            }
            for document in engine.index.documents()
        ]
        target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def load(self, path: str | Path) -> SearchEngine:
        source = Path(path)
        try:
            payload = json.loads(source.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"stored documents do not exist: {source}") from exc

        if not isinstance(payload, list):
            raise TypeError("stored documents must be a list")

        engine = SearchEngine()
        for item in payload:
            if not isinstance(item, dict):
                raise TypeError("each stored document must be an object")

            document_id = item.get("document_id")
            text = item.get("text")
            metadata = item.get("metadata", {})
            if isinstance(document_id, bool) or not isinstance(document_id, int):
                raise TypeError("stored document_id must be an integer")
            if not isinstance(text, str):
                raise TypeError("stored document text must be a string")
            if metadata is not None and not isinstance(metadata, dict):
                raise TypeError("stored document metadata must be an object or null")

            engine.add(document_id, text, metadata)
        return engine
