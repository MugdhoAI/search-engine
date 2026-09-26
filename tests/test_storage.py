from pathlib import Path

import pytest

from search_engine.engine import SearchEngine
from search_engine.storage import JsonStore


def test_json_store_round_trip(tmp_path: Path) -> None:
    engine = SearchEngine()
    engine.add(7, "Python indexing", {"source": "example"})

    path = tmp_path / "documents.json"
    JsonStore().save(engine, path)

    restored = JsonStore().load(path)
    assert restored.count() == 1
    assert restored.document(7).metadata == {"source": "example"}
    assert [item.document_id for item in restored.search("python")] == [7]


def test_invalid_stored_shape_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError):
        JsonStore().load(path)
