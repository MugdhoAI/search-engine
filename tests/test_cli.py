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


def test_cli_example_output_matches_readme(monkeypatch, capsys) -> None:
    from pathlib import Path

    collection = Path(__file__).resolve().parents[1] / "examples" / "documents.json"
    monkeypatch.setattr("sys.argv", ["search-engine", str(collection), "python"])

    main()

    assert capsys.readouterr().out.splitlines() == [
        "0.251804\t1\tPython is a programming language designed for readable software.",
        "0.251804\t4\tPython can be used to build search systems.",
    ]
