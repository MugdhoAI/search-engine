from search_engine.cli import build_parser, main
from search_engine.engine import SearchEngine
from search_engine.storage import JsonStore


def test_cli_parser() -> None:
    args = build_parser().parse_args(["documents.json", "python", "--limit", "3"])
    assert args.index == "documents.json"
    assert args.query == "python"
    assert args.limit == 3


def test_cli_searches_a_json_collection(tmp_path, monkeypatch, capsys) -> None:
    engine = SearchEngine()
    engine.add(7, "Python search engine")
    path = tmp_path / "documents.json"
    JsonStore().save(engine, path)
    monkeypatch.setattr("sys.argv", ["search-engine", str(path), "python"])

    main()

    assert "\t7\tPython search engine\n" in capsys.readouterr().out
