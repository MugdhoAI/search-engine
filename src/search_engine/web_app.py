"""Streamlit interface for the Search Engine project."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import streamlit as st

from search_engine.engine import SearchEngine
from search_engine.ingestion import extract_text
from search_engine.query_assist import (
    NebiusQueryAssistant,
    QueryAssistantError,
    is_simple_query,
)
from search_engine.storage import JsonStore


def _initial_engine() -> tuple[SearchEngine, str | None]:
    sample_path = Path(__file__).resolve().parents[2] / "examples" / "documents.json"
    try:
        return JsonStore().load(sample_path), None
    except (OSError, TypeError, ValueError) as exc:
        return SearchEngine(), f"The sample collection could not be loaded: {exc}"


def _next_document_id(engine: SearchEngine) -> int:
    ids = [document.document_id for document in engine.index.documents()]
    return max(ids, default=0) + 1


def _excerpt(text: str, terms: tuple[str, ...], max_chars: int = 260) -> str:
    if len(text) <= max_chars:
        return text

    folded = text.casefold()
    positions = [folded.find(term.casefold()) for term in terms if term]
    positions = [position for position in positions if position >= 0]
    match_at = min(positions, default=0)
    start = max(0, match_at - max_chars // 4)
    end = min(len(text), start + max_chars)
    excerpt = text[start:end].strip()
    if start:
        excerpt = "…" + excerpt
    if end < len(text):
        excerpt += "…"
    return excerpt


def _content_fingerprint(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def main() -> None:
    st.set_page_config(
        page_title="Search Engine",
        page_icon="🔎",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    if "engine" not in st.session_state:
        engine, load_error = _initial_engine()
        st.session_state.engine = engine
        st.session_state.sample_load_error = load_error
        st.session_state.last_search = None

    engine: SearchEngine = st.session_state.engine
    st.title("Search Engine")
    st.caption(
        "Search your documents with an inspectable inverted index and deterministic TF IDF ranking."
    )

    if st.session_state.sample_load_error:
        st.warning(st.session_state.sample_load_error)

    with st.sidebar:
        st.header("Document collection")
        st.caption(
            "Uploads are held in this app session and are not written to server storage. "
            "TXT and Markdown files use UTF-8. PDFs must contain extractable text."
        )
        uploads = st.file_uploader(
            "Add documents",
            type=["txt", "md", "pdf"],
            accept_multiple_files=True,
            help="Maximum 5 MiB per file, 100 pages per PDF, and 200,000 extracted characters.",
        )
        if st.button("Add selected files", type="primary", disabled=not uploads):
            added = 0
            skipped = 0
            errors: list[str] = []
            existing_hashes = {
                (document.metadata or {}).get("sha256")
                for document in engine.index.documents()
            }
            next_id = _next_document_id(engine)

            for uploaded in uploads or []:
                try:
                    content = uploaded.getvalue()
                    fingerprint = _content_fingerprint(content)
                    if fingerprint in existing_hashes:
                        skipped += 1
                        continue
                    text = extract_text(uploaded.name, content)
                    suffix = Path(uploaded.name).suffix.casefold().lstrip(".")
                    engine.add(
                        next_id,
                        text,
                        {
                            "filename": Path(uploaded.name).name,
                            "file_type": suffix,
                            "sha256": fingerprint,
                        },
                    )
                    existing_hashes.add(fingerprint)
                    next_id += 1
                    added += 1
                except (TypeError, ValueError) as exc:
                    errors.append(f"{uploaded.name}: {exc}")

            if added:
                st.session_state.last_search = None
                st.success(f"Added {added} document(s).")
            if skipped:
                st.info(f"Skipped {skipped} duplicate file(s).")
            for error in errors:
                st.error(error)

        st.metric("Documents indexed", engine.count())
        if st.button("Clear collection", disabled=engine.count() == 0):
            st.session_state.engine = SearchEngine()
            st.session_state.last_search = None
            st.rerun()

        st.divider()
        st.caption("Search behavior")
        st.markdown(
            "- Bare terms use OR semantics\n"
            "- `AND` requires all terms\n"
            "- `OR` accepts either side\n"
            '- Use quotes for phrases, e.g. `"search systems"`'
        )

    query_assistant = NebiusQueryAssistant()
    improve_query = st.checkbox(
        "Improve plain-text queries with NVIDIA Nemotron",
        value=False,
        help=(
            "Sends the query text to Nebius Token Factory for a rewrite. "
            "Search results still come only from your indexed documents."
        ),
    )
    if improve_query and not query_assistant.is_configured:
        st.info("Set NEBIUS_API_KEY in the app environment to enable AI query assistance.")

    query_col, limit_col = st.columns([5, 1])
    with st.form("search_form"):
        query = query_col.text_input(
            "Search documents",
            placeholder='Try "search systems" or python AND index',
        )
        limit = limit_col.selectbox("Results", options=[5, 10, 20, 50], index=1)
        submitted = st.form_submit_button("Search", type="primary")

    if submitted:
        if not query.strip():
            st.session_state.last_search = None
            st.info("Enter a query to search the collection.")
        else:
            effective_query = query
            assisted = False
            if improve_query:
                if not query_assistant.is_configured:
                    st.warning("AI assistance is not configured. Searching with the original query.")
                elif not is_simple_query(query):
                    st.info(
                        "Boolean and quoted phrase queries are kept unchanged to preserve their syntax."
                    )
                else:
                    try:
                        effective_query = query_assistant.rewrite(query)
                        assisted = effective_query.casefold() != query.strip().casefold()
                    except QueryAssistantError as exc:
                        st.warning(f"{exc} Searching with the original query.")

            try:
                parsed = engine.parser.parse(effective_query)
                results = engine.search(effective_query, limit=limit)
                st.session_state.last_search = {
                    "query": query,
                    "effective_query": effective_query,
                    "assisted": assisted,
                    "terms": parsed.terms,
                    "results": [(item.document_id, item.score) for item in results],
                }
            except (TypeError, ValueError) as exc:
                st.session_state.last_search = None
                st.error(f"Could not parse this query: {exc}")

    search_state: dict[str, Any] | None = st.session_state.last_search
    if search_state is not None:
        st.subheader(f'Results for: {search_state["query"]}')
        if (
            search_state["effective_query"].casefold()
            != search_state["query"].strip().casefold()
        ):
            st.caption(f'Search query used: {search_state["effective_query"]}')
        if (
            improve_query
            and not search_state["assisted"]
            and is_simple_query(search_state["query"])
        ):
            st.caption("Results use the original query; AI assistance did not change it.")
        result_rows = search_state["results"]
        if not result_rows:
            st.info("No matching documents. Try different terms or add more documents.")
        else:
            st.caption(f"{len(result_rows)} result(s), ordered by TF IDF score.")
            for document_id, score in result_rows:
                document = engine.document(document_id)
                metadata = document.metadata or {}
                title = metadata.get("filename", f"Document {document_id}")
                with st.container(border=True):
                    st.markdown(f"**{title}**")
                    st.caption(f"Document ID {document_id} · TF IDF score {score:.6f}")
                    st.write(_excerpt(document.text, tuple(search_state["terms"])))
                    with st.expander("View full extracted text"):
                        st.text(document.text)
    else:
        st.info(
            "The sample collection is ready to search. Add TXT, Markdown, or text-based PDF "
            "documents from the sidebar to extend it."
        )


if __name__ == "__main__":
    main()
