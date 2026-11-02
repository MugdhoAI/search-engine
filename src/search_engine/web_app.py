"""Streamlit interface for the Search Engine project."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import streamlit as st

from search_engine.engine import SearchEngine
from search_engine.ingestion import extract_text
from search_engine.storage import JsonStore
from search_engine import query_assist


PURPLE_THEME = """
<style>
:root {
    color-scheme: dark;
    --search-bg: #09080f;
    --search-sidebar: #15121e;
    --search-surface: #1b1726;
    --search-raised: #241c32;
    --search-border: #382a4b;
    --search-purple: #b86bff;
    --search-purple-bright: #d49aff;
    --search-text: #f7f3fc;
    --search-muted: #b8adc5;
}

.stApp {
    background:
        radial-gradient(ellipse at 50% 0%, rgba(91, 37, 132, 0.19), transparent 42%),
        var(--search-bg);
    color: var(--search-text);
}

[data-testid="stHeader"] {
    background: rgba(9, 8, 15, 0.78);
}

[data-testid="stSidebar"] {
    background: var(--search-sidebar);
    border-right: 1px solid rgba(184, 107, 255, 0.12);
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.85rem;
}

.block-container {
    max-width: 1180px;
    padding-top: 3.2rem;
    padding-bottom: 4rem;
}

.search-hero {
    max-width: 940px;
    margin: 0 auto 1.8rem;
    text-align: center;
}

.search-eyebrow {
    margin-bottom: 0.8rem;
    color: var(--search-purple-bright);
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.16em;
}

.search-hero h1 {
    margin: 0;
    color: var(--search-purple-bright);
    font-size: clamp(2rem, 4vw, 3.05rem);
    font-weight: 750;
    line-height: 1.12;
    letter-spacing: -0.045em;
}

.search-hero p {
    max-width: 700px;
    margin: 0.8rem auto 1.2rem;
    color: var(--search-muted);
    font-size: 1rem;
    line-height: 1.65;
}

.search-features {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 0.55rem;
    margin-top: 1.1rem;
}

.search-feature {
    padding: 0.38rem 0.72rem;
    border: 1px solid rgba(184, 107, 255, 0.28);
    border-radius: 999px;
    background: rgba(184, 107, 255, 0.07);
    color: #d7b4f4;
    font-size: 0.76rem;
    font-weight: 600;
}

[data-testid="stTextInput"] input {
    min-height: 3.65rem;
    border: 1px solid #5a3a78;
    border-radius: 14px;
    background: var(--search-raised);
    color: var(--search-text);
    font-size: 1rem;
    box-shadow: 0 0 0 1px rgba(184, 107, 255, 0.08),
                0 0 24px rgba(168, 85, 247, 0.13);
}

[data-testid="stTextInput"] input:focus {
    border-color: var(--search-purple);
    box-shadow: 0 0 0 1px var(--search-purple),
                0 0 25px rgba(168, 85, 247, 0.28);
}

[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    min-height: 3.1rem;
    border-color: var(--search-border);
    border-radius: 10px;
    background: var(--search-surface);
}

.stButton > button,
.stFormSubmitButton > button {
    min-height: 2.9rem;
    border: 1px solid #a65be8;
    border-radius: 10px;
    background: linear-gradient(135deg, #a855f7, #8b45cf);
    color: #fff;
    font-weight: 650;
    transition: filter 120ms ease, transform 120ms ease;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    border-color: #d49aff;
    background: linear-gradient(135deg, #b86bff, #9954df);
    color: #fff;
    filter: brightness(1.06);
}

.stButton > button:focus-visible,
.stFormSubmitButton > button:focus-visible {
    outline: 2px solid var(--search-purple-bright);
    outline-offset: 3px;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: var(--search-border);
    border-radius: 13px;
    background: rgba(27, 23, 38, 0.78);
}

[data-testid="stMetric"] {
    padding: 0.7rem 0.85rem;
    border: 1px solid var(--search-border);
    border-radius: 11px;
    background: rgba(27, 23, 38, 0.75);
}

[data-testid="stMetricValue"] {
    color: var(--search-purple-bright);
}

[data-testid="stCaptionContainer"] {
    color: var(--search-muted);
}

[data-testid="stExpander"] {
    border-color: var(--search-border);
    border-radius: 10px;
    background: rgba(20, 16, 29, 0.55);
}

.search-section-label {
    margin: 1.5rem 0 0.6rem;
    color: #e9ddf4;
    font-size: 1.08rem;
    font-weight: 700;
}

.search-empty-state {
    margin-top: 1.2rem;
    padding: 1rem 1.15rem;
    border: 1px solid var(--search-border);
    border-radius: 12px;
    background: rgba(27, 23, 38, 0.7);
    color: var(--search-muted);
    line-height: 1.6;
}

.search-empty-state strong {
    color: var(--search-text);
}

@media (max-width: 720px) {
    .block-container {
        padding: 2rem 1rem 3rem;
    }

    .search-hero {
        margin-bottom: 1.3rem;
        text-align: left;
    }

    .search-hero p {
        margin-left: 0;
        margin-right: 0;
    }

    .search-features {
        justify-content: flex-start;
    }
}

@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        scroll-behavior: auto !important;
        transition-duration: 0.01ms !important;
    }
}
</style>
"""


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


def _render_sidebar(engine: SearchEngine) -> None:
    with st.sidebar:
        st.markdown("### Document collection")
        st.caption(
            "Files stay in this app session and are not written to server storage. "
            "TXT and Markdown files use UTF-8. PDFs need extractable text."
        )
        uploads = st.file_uploader(
            "Add documents",
            type=["txt", "md", "pdf"],
            accept_multiple_files=True,
            help="Maximum 5 MiB per file, 100 pages per PDF, and 200,000 extracted characters.",
        )

        if st.button("Add selected files", type="primary", disabled=not uploads, use_container_width=True):
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
                    extracted = extract_text(uploaded.name, content)
                    suffix = Path(uploaded.name).suffix.casefold().lstrip(".")
                    engine.add(
                        next_id,
                        extracted,
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

        if st.button(
            "Clear collection",
            disabled=engine.count() == 0,
            use_container_width=True,
        ):
            st.session_state.engine = SearchEngine()
            st.session_state.last_search = None
            st.rerun()

        with st.expander("Search syntax", expanded=False):
            st.markdown(
                "- Bare terms use OR semantics\n"
                "- `AND` requires all terms\n"
                "- `OR` accepts either side\n"
                '- Use quotes for phrases, e.g. `"search systems"`'
            )


def _render_hero() -> None:
    st.markdown(
        """
        <section class="search-hero">
            <div class="search-eyebrow">MUGDHOAI / SEARCH</div>
            <h1>Find what matters in your documents.</h1>
            <p>
                Search your collection with an inspectable inverted index
                and deterministic TF-IDF ranking.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="MugdhoAI Search Engine",
        page_icon="⌕",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(PURPLE_THEME, unsafe_allow_html=True)

    if "engine" not in st.session_state:
        engine, load_error = _initial_engine()
        st.session_state.engine = engine
        st.session_state.sample_load_error = load_error
        st.session_state.last_search = None

    engine: SearchEngine = st.session_state.engine
    _render_sidebar(engine)

    _render_hero()
    if st.session_state.sample_load_error:
        st.warning(st.session_state.sample_load_error)

    query_assistant = query_assist.GeminiQueryAssistant()
    with st.form("search_form", clear_on_submit=False):
        query_col, limit_col, button_col = st.columns([7, 1.35, 1.15], vertical_alignment="bottom")
        with query_col:
            query = st.text_input(
                "Search your collection",
                placeholder='Search documents, concepts, or exact phrases...',
                label_visibility="visible",
            )
        with limit_col:
            limit = st.selectbox("Results", options=[5, 10, 20, 50], index=1)
        with button_col:
            submitted = st.form_submit_button("Search", type="primary", use_container_width=True)

    st.markdown(
        """
        <div class="search-features">
            <span class="search-feature">TF-IDF ranking</span>
            <span class="search-feature">Boolean search</span>
            <span class="search-feature">Phrase search</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    option_col, note_col = st.columns([1.25, 2.75], vertical_alignment="center")
    with option_col:
        improve_query = st.checkbox(
            "Improve query with Gemini",
            value=False,
            help=(
                "Sends the query text to Google's Gemini API for a rewrite. "
                "Search results still come only from your indexed documents."
            ),
        )
    with note_col:
        st.caption("AI assistance is optional. Your documents are searched locally in this app session.")

    if improve_query and not query_assistant.is_configured:
        st.info("Set GEMINI_API_KEY in the app environment to enable AI query assistance.")

    if submitted:
        if not query.strip():
            st.session_state.last_search = None
            st.info("Enter a query to search the collection.")
        else:
            effective_query = query
            assisted = False
            if improve_query:
                if not query_assistant.is_configured:
                    st.warning(
                        "AI assistance is not configured. Searching with the original query."
                    )
                elif not query_assist.is_simple_query(query):
                    st.info(
                        "Boolean and quoted phrase queries stay unchanged to preserve syntax."
                    )
                else:
                    try:
                        effective_query = query_assistant.rewrite(query)
                        assisted = effective_query.casefold() != query.strip().casefold()
                    except query_assist.QueryAssistantError as exc:
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
        st.markdown('<div class="search-section-label">Search results</div>', unsafe_allow_html=True)
        st.subheader(f'Results for: {search_state["query"]}')
        if (
            search_state["effective_query"].casefold()
            != search_state["query"].strip().casefold()
        ):
            st.caption(f'Search query used: {search_state["effective_query"]}')
        if (
            improve_query
            and not search_state["assisted"]
            and query_assist.is_simple_query(search_state["query"])
        ):
            st.caption("Results use the original query; AI assistance did not change it.")

        result_rows = search_state["results"]
        if not result_rows:
            st.info("No matching documents. Try different terms or add more documents.")
        else:
            st.caption(f"{len(result_rows)} result(s), ordered by TF-IDF score.")
            for document_id, score in result_rows:
                document = engine.document(document_id)
                metadata = document.metadata or {}
                title = metadata.get("filename", f"Document {document_id}")
                with st.container(border=True):
                    st.markdown(f"**{title}**")
                    st.caption(f"Document {document_id}  ·  TF-IDF score {score:.6f}")
                    st.write(_excerpt(document.text, tuple(search_state["terms"])))
                    with st.expander("View full extracted text"):
                        st.text(document.text)
    else:
        st.markdown(
            """
            <div class="search-empty-state">
                <strong>Your sample collection is ready.</strong>
                Add TXT, Markdown, or text-based PDF documents from the sidebar
                to search across more material.
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
