from search_engine.cli import build_parser


def test_cli_parser() -> None:
    args = build_parser().parse_args(["documents.json", "python", "--limit", "3"])
    assert args.index == "documents.json"
    assert args.query == "python"
    assert args.limit == 3
