# Search Engine

A lightweight search engine built from scratch in Python.

The project implements the core retrieval pipeline without depending on an external search engine library:

document text -> tokenization -> inverted index -> query parsing -> TF IDF ranking -> results

What problem it solves

Scanning every document for every query becomes increasingly expensive as a collection grows.

This project builds an inverted index once, so a query can jump directly to documents containing its terms instead of scanning the full collection.

With the included corpus, "python" returns documents 1 and 4. "python AND search" returns document 4. "python OR language" returns documents containing either term. Quoted phrases such as "search systems" require the terms to occur next to each other.

Results are ranked with TF IDF so terms that are more representative of a document contribute more to its score.

Features

Tokenization and normalization

Stop word filtering

Inverted index with term frequencies

AND and OR queries

Quoted phrase queries

TF IDF relevance scoring

Deterministic result ordering

JSON persistence

Command line search

Unit and integration tests

Continuous integration

Quick start

Create an environment and install the project with development dependencies:

    python -m venv .venv
    python -m pip install -e ".[dev]"

Run the tests:

    pytest

Search the example collection:

    search-engine examples/documents.json "python"

You can also run the module directly:

    python -m search_engine.cli examples/documents.json "python AND search"

Architecture

document.py defines the immutable document model.

tokenizer.py converts text into normalized searchable terms.

index.py builds the inverted index and stores term frequencies.

query.py parses boolean and phrase queries and selects candidate documents.

ranking.py calculates TF IDF scores and produces deterministic rankings.

engine.py provides the public search API.

storage.py persists source documents to JSON and rebuilds the index.

cli.py exposes the engine from the command line.

Design

The core retrieval structures use Python dictionaries and sets so their behavior remains visible instead of being hidden behind a search framework.

The index stores source documents separately from postings. This keeps retrieval data simple and makes persistence portable.

The ranker uses normalized term frequency and smoothed inverse document frequency. Query terms are deduplicated before scoring so repeated words do not artificially inflate relevance.

The query language intentionally stays small. AND and OR provide boolean retrieval while quoted phrases add positional matching without introducing a large query parser.

Validation

The test suite covers tokenization, indexing, duplicate IDs, document lengths, ranked retrieval, boolean queries, phrase queries, empty queries, invalid input, persistence, deterministic ordering, repeated query terms, and CLI parsing.

CI runs the same tests on Python 3.11, 3.12, and 3.13 and checks the source with Ruff.

Scope

This is a from scratch educational search engine, not a replacement for Lucene or Elasticsearch. It is intentionally small enough to understand end to end.

Future work can extend the same foundation with better text normalization, persistent postings, benchmarks, and larger corpus experiments.
