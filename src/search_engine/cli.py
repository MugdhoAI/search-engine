import argparse

from .storage import JsonStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search a JSON document collection.")
    parser.add_argument("index", help="Path to a JSON document collection")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", type=int, default=10)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    engine = JsonStore().load(args.index)
    for result in engine.search(args.query, args.limit):
        document = engine.document(result.document_id)
        print(f"{result.score:.6f}\t{result.document_id}\t{document.text}")


if __name__ == "__main__":
    main()
