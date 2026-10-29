<p align="center">
  <img src="assets/search-engine-hero.svg" alt="Search Engine: an information retrieval pipeline from source documents through an inverted index to ranked results" width="100%">
</p>

<h1 align="center">MugdhoAI / <a href="https://github.com/MugdhoAI/search-engine">search-engine</a></h1>

<p align="center">
  <a href="https://github.com/MugdhoAI/search-engine/actions/workflows/ci.yml"><img src="https://github.com/MugdhoAI/search-engine/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI"></a>
  <a href="https://github.com/MugdhoAI/search-engine/releases/tag/v0.1.0"><img src="https://img.shields.io/badge/release-v0.1.0-blue" alt="Release v0.1.0"></a>
  <a href="https://github.com/MugdhoAI/search-engine/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-3776AB?logo=python&logoColor=white" alt="Python 3.11, 3.12, 3.13, and 3.14">
</p>

<p align="center">
  <strong>From raw text to ranked results.</strong><br>
  A Python search engine with an inspectable retrieval pipeline, a command-line interface, and a web app for searching uploaded documents.
</p>

<table>
  <tr>
    <td align="center" width="20%"><strong>Indexing</strong><br><sub>Tokenization and term frequencies</sub></td>
    <td align="center" width="20%"><strong>Inverted Index</strong><br><sub>Term to document postings</sub></td>
    <td align="center" width="20%"><strong>Query Support</strong><br><sub>AND, OR, quoted phrases</sub></td>
    <td align="center" width="20%"><strong>Ranking</strong><br><sub>TF IDF and deterministic order</sub></td>
    <td align="center" width="20%"><strong>Web App and CLI</strong><br><sub>Document uploads and terminal search</sub></td>
  </tr>
</table>

## Why this project exists

Search engines combine several steps that are easy to hide behind a library: converting text into terms, finding candidate documents efficiently, interpreting a query, and ordering results by relevance. This project keeps those steps small and inspectable so the retrieval process can be understood and tested end to end.

## Search pipeline

```mermaid
flowchart LR
    A[Source documents] --> B[Document model]
    B --> C[Tokenizer]
    C --> D[Inverted index]
    E[Search query] --> F[Query parser]
    F --> G[Candidate selection]
    D --> G
    G --> H[TF IDF ranker]
    D --> H
    H --> I[Ranked results]
```

An inverted index maps each term to the documents that contain it, along with its term frequency. This avoids scanning every document just to find candidate matches.

Example queries against the included collection:

```text
python
python AND search
python OR language
"search systems"
```

## Quick start

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it using the command for your shell.

macOS or Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the project and development tools:

```bash
python -m pip install -e ".[dev]"
```

Run the test suite and lint check:

```bash
python -m pytest
python -m ruff check src tests
```

Search the included collection:

```bash
search-engine examples/documents.json "python"
```

Example output:

```text
0.251804    1    Python is a programming language designed for readable software.
0.251804    4    Python can be used to build search systems.
```

The columns are score, document ID, and document text. Equal scores are ordered by ascending document ID. You can also run the CLI as a module:

```bash
python -m search_engine.cli examples/documents.json "python AND search"
```

## Web application

The Streamlit interface lets you search the sample collection, upload documents, inspect excerpts, and expand a result to read its extracted text. The original retrieval engine and CLI remain available.

Install the app dependencies and start the interface:

```bash
python -m pip install -e ".[app,dev]"
python -m streamlit run src/search_engine/web_app.py
```

The app accepts UTF-8 TXT files, Markdown files, and text-based PDFs. It enforces a 5 MiB upload limit, a 100-page PDF limit, and a 200,000-character extracted-text limit. Duplicate uploads are skipped by content hash.

Uploaded documents are held in the current Streamlit session and are not written to server storage. This avoids sharing private uploads between visitors, but it also means uploaded documents do not persist after the session ends. The app extracts embedded PDF text; it does not perform OCR on scanned pages. The included sample collection is loaded when a new session starts.

For deployment platforms that install dependencies from `requirements.txt`, the file installs the package with its app extra.

### Optional AI query assistance

The web app can optionally rewrite a plain-text query using Gemini through Google's Gemini API. The model may add useful search terms, but it does not generate answers or search results. The existing index and TF IDF ranker still determine which documents are returned.

To enable it, set `GEMINI_API_KEY` in the environment where Streamlit runs. Do not commit the key or put it in the source code. The default API endpoint is `https://generativelanguage.googleapis.com/v1beta/openai` and the default model ID is `gemini-3.8-flash`. You can override these with `GEMINI_BASE_URL` and `GEMINI_MODEL`.

PowerShell:

```powershell
$env:GEMINI_API_KEY = "your-key"
python -m streamlit run src/search_engine/web_app.py
```

macOS or Linux:

```bash
export GEMINI_API_KEY="your-key"
python -m streamlit run src/search_engine/web_app.py
```

AI assistance is off by default and must be selected in the interface. Provider requests time out after 12 seconds. Only the query text is sent to Google's Gemini API when the feature is selected. Do not include confidential information in a query you choose to send to the hosted model. Quoted phrase and Boolean queries are left unchanged so their syntax is preserved. If the provider is not configured or the request fails, the app searches with the original query. Tests mock the HTTP layer and do not require a key or make network calls.

## Query behavior

- Bare terms use OR semantics by default.
- `AND` requires all query terms to match; `OR` accepts matches from either side.
- Mixing `AND` and `OR` in the same query is rejected.
- Quoted phrases must appear as adjacent tokens after tokenization and stop word filtering.
- A phrase combined with unquoted terms uses AND semantics unless you explicitly use `OR`.

Phrase matching filters candidate documents. Results are ranked using the query terms, not phrase proximity or a learned relevance model.

## Architecture

The modules have distinct responsibilities:

- `document.py` defines the document record and validates its fields.
- `tokenizer.py` normalizes text into searchable terms and removes stop words.
- `index.py` builds the inverted index and stores term frequencies and document lengths.
- `query.py` parses Boolean and phrase queries and selects candidate documents.
- `ranking.py` calculates TF IDF scores and orders results deterministically.
- `engine.py` coordinates indexing, querying, and ranking through the public API.
- `storage.py` persists source documents as JSON and rebuilds the index when loading.
- `ingestion.py` extracts text from supported uploads with size and page limits.
- `web_app.py` provides the Streamlit interface.
- `query_assist.py` optionally rewrites plain-text queries through Google Gemini API with request and response size limits.
- `cli.py` exposes search through the command line.
- `scripts/evaluate_search.py` measures retrieval metrics and local query latency on a labeled synthetic corpus.

The implementation uses Python dictionaries and sets so the retrieval structures remain visible rather than hidden behind a search framework.

For each unique query term present in a document, the ranker adds:

```text
(term frequency / searchable document length)
    * (log((number of documents + 1) / (document frequency + 1)) + 1)
```

Results are sorted by descending score and then ascending document ID. Deduplicating query terms prevents repeated words from artificially increasing a document's score.

## Validation

The tests cover tokenization, index construction, duplicate IDs, document lengths, ranked retrieval, Boolean and phrase queries, empty queries, invalid input, JSON persistence, deterministic ties, repeated query terms, the CLI workflow, upload validation, AI provider failure cases, and evaluation metric calculations.

Run the fixed retrieval evaluation with:

```bash
python scripts/evaluate_search.py
```

The script reports Precision@5, Recall@5, Mean Reciprocal Rank, NDCG@5, and in-process p50/p95 query latency. Its relevance labels are manually assigned to a small synthetic corpus. It is intended as a reproducible regression check, not evidence of real-world relevance or large-corpus performance. Latency varies by machine and run.

CI installs the package, runs pytest, executes the evaluation script, and checks the source and tests with Ruff on Python 3.11, 3.12, 3.13, and 3.14.

## Scope and limitations

This project is a compact search engine and document search app, not a replacement for Lucene or Elasticsearch. Tokenization currently focuses on ASCII letters and digits, so multilingual text normalization is limited. Phrase matching operates on document text rather than a positional index, and the project has no benchmark results or claims about large-corpus performance. The web app uses optional model-assisted lexical query rewriting, not semantic vector retrieval. Query assistance requires a Google Gemini API key and sends selected query text to that external service.

Potential extensions include broader Unicode-aware tokenization, positional postings, reproducible benchmarks on a defined corpus, and experiments with larger collections.

## License

MIT
