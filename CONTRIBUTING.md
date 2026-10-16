# Contributing to Search Engine

Thank you for considering a contribution to Search Engine. Contributions may include bug fixes, tests, documentation improvements, and focused improvements to indexing, query parsing, ranking, persistence, or the command-line interface.

## Before you start

Check existing issues and pull requests before starting work. For substantial changes to query syntax, ranking behavior, persistence formats, or the public API, discuss the proposed approach first.

## Development setup

Use Python 3.11 or newer. From the repository root, create and activate a virtual environment, then install the project with development dependencies:

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
```

Activate the environment before running commands. On Windows PowerShell, use `.venv\Scripts\Activate.ps1`; on macOS or Linux, use `source .venv/bin/activate`.

Run the test suite and lint check:

```bash
python -m pytest
python -m ruff check .
```

The README includes an example command for searching the sample document collection.

## Retrieval behavior and correctness

Changes to retrieval behavior should be covered by tests that describe the intended results.

- For tokenizer or normalization changes, test punctuation, casing, empty input, and relevant Unicode cases.
- For index changes, test term frequencies, document lengths, duplicate IDs, and empty collections where applicable.
- For query parsing, test AND and OR behavior, phrase queries, invalid syntax, and empty queries.
- For ranking changes, test score behavior and deterministic ordering, including ties.
- For persistence changes, test saving and loading documents and rebuilding the index. Document any compatibility impact.
- For CLI changes, test argument parsing and useful error behavior.

Keep documentation aligned with the implemented behavior. Do not describe the project as a replacement for production search platforms or claim ranking quality without evaluation evidence.

## Pull request expectations

A good pull request should:

- Explain the problem and the proposed solution.
- Stay focused and avoid unrelated refactoring.
- Include regression tests for bug fixes and tests for changed behavior.
- Pass the test suite and Ruff check, or clearly document a reproducible existing failure.
- Update the README when setup, query syntax, ranking, persistence, or limitations change.
- Avoid committing virtual environments, local indexes, private documents, credentials, or generated files.
- Respect the project's MIT License and the licenses of third-party code and data.

## Reporting bugs

Include a minimal reproducible example, the expected and actual results, and relevant sanitized error output. Do not include private documents or sensitive data in example corpora.

## License

By submitting a contribution, you agree that your contribution is provided under the project's [MIT License](LICENSE). You retain the copyright to your contribution, subject to the license terms.
