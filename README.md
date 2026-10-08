# Search Engine

A lightweight search engine built from scratch in Python.

This project implements the core retrieval pipeline without relying on an external search engine library. It is intentionally small enough to inspect from input documents to ranked results.

## What it does

The search pipeline is:

```text
Documents
   ↓
Tokenization
   ↓
Inverted index
   ↓
Query parsing
   ↓
TF IDF ranking
   ↓
Results
```

An inverted index lets a query jump directly to documents containing its terms instead of scanning the entire collection every time.

The included corpus supports queries such as:

```text
python
python AND search
python OR language
"search systems"
```

Results are ranked with TF IDF so terms that are more representative of a document contribute more to its score.

## Features

* Text tokenization and normalization
* Stop word filtering
* Inverted index with term frequencies
* AND and OR queries
* Quoted phrase queries
* TF IDF relevance scoring
* Deterministic result ordering
* JSON persistence
* Command line search
* Unit and integration tests
* Continuous integration

## Quick start

Create an environment and install the project with development dependencies:

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
```

Run the tests:

```bash
pytest
```

Search the example collection:

```bash
search-engine examples/documents.json "python"
```

You can also run the module directly:

```bash
python -m search_engine.cli examples/documents.json "python AND search"
```

## Architecture

The main components are deliberately small:

* `document.py` defines the immutable document model.
* `tokenizer.py` converts text into normalized searchable terms.
* `index.py` builds the inverted index and stores term frequencies.
* `query.py` parses Boolean and phrase queries.
* `ranking.py` calculates TF IDF scores and produces deterministic rankings.
* `engine.py` provides the public search API.
* `storage.py` persists source documents to JSON and rebuilds the index.
* `cli.py` exposes the engine from the command line.

The retrieval structures use Python dictionaries and sets so the core behavior remains visible instead of being hidden behind a search framework.

The index keeps source documents separate from postings. The ranker uses normalized term frequency and smoothed inverse document frequency. Query terms are deduplicated before scoring so repeated words do not artificially inflate relevance.

## Validation

The test suite covers:

* Tokenization and normalization
* Index construction
* Duplicate IDs
* Document lengths
* Ranked retrieval
* Boolean queries
* Phrase queries
* Empty queries
* Invalid input
* Persistence
* Deterministic ordering
* Repeated query terms
* CLI parsing

CI runs the tests on Python 3.11, 3.12, and 3.13 and checks the source with Ruff.

## Scope

This is an educational search engine, not a replacement for Lucene or Elasticsearch. The project stays deliberately small so the full retrieval process can be understood end to end.

Future work can extend the same foundation with better text normalization, persistent postings, benchmarks, and larger corpus experiments.

## License

MIT
