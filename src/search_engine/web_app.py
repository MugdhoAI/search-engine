"""Streamlit interface for the Search Engine project."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import streamlit as st

from search_engine.engine import SearchEngine
from search_engine.ingestion import extract_text
from search_engine.query_assist import (
    GeminiQueryAssistant,
    QueryAssistantError,
    is_simple_query,
)
from search_engine.storage import JsonStore

PAGE_STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
:root {
  --ink: #f5f3fa;
  --muted: #a5a0b2;
  --violet: #a78bfa;
  --violet-bright: #c4b5fd;
  --surface: #111019;
  --line: rgba(210, 195, 255, .14);
}
.stApp {
  background:
    radial-gradient(ellipse at 50% -18%, rgba(110, 57, 184, .26), transparent 46%),
    radial-gradient(ellipse at 88% 20%, rgba(69, 38, 119, .12), transparent 30%),
    #08070c;
  color: var(--ink);
  font-family: 'Manrope', sans-serif;
}
.stApp, .stApp [data-testid="stMarkdownContainer"], .stApp label,
.stApp input, .stApp button, .stApp textarea, .stApp [data-testid="stMetricValue"] {
  font-family: 'Manrope', sans-serif;
}
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
.block-container { max-width: 1220px; padding: 1.2rem 2rem 5rem; }
[data-testid="stSidebar"] {
  background: #0e0c14;
  border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1.4rem; }
.stApp h1 { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; color:var(--ink); }
.stApp h2, .stApp h3 { color: var(--ink); letter-spacing: -.035em; }
.stApp p, .stApp li { color: #d0ccda; }
.stApp [data-testid="stCaptionContainer"] p { color: var(--muted); }
.topline {
  display:flex; align-items:center; justify-content:space-between; gap:16px;
  padding: 8px 0 42px; border-bottom: 1px solid rgba(210,195,255,.10);
}
.brand { display:flex; align-items:center; gap:11px; color:#f8f6ff; font-weight:800; font-size:15px; letter-spacing:-.03em; }
.brand-mark { width:30px; height:30px; display:grid; place-items:center; border:1px solid rgba(191,166,255,.38); border-radius:10px; background:linear-gradient(145deg,rgba(151,105,232,.28),rgba(89,57,136,.10)); color:#d2bdff; box-shadow:0 0 28px rgba(148,92,236,.16); }
.brand-sub { color:#938da2; font-size:11px; font-weight:500; letter-spacing:.02em; }
.hero { position:relative; overflow:hidden; padding:62px 24px 15px; text-align:center; }
.hero:before { content:""; position:absolute; z-index:0; width:min(800px,90vw); height:260px; left:50%; top:-225px; transform:translateX(-50%); border-radius:50%; border:1px solid rgba(190,144,255,.42); box-shadow:0 8px 50px rgba(146,80,237,.27),0 20px 95px rgba(97,46,154,.23),inset 0 -10px 38px rgba(171,111,255,.22); pointer-events:none; }
.hero:after { content:""; position:absolute; z-index:0; inset:0; background:radial-gradient(ellipse at 50% 0%,rgba(131,74,200,.12),transparent 52%); pointer-events:none; }
.hero > * { position:relative; z-index:1; }
.eyebrow { display:inline-flex; align-items:center; gap:9px; padding:7px 12px; border:1px solid rgba(198,174,248,.18); border-radius:999px; background:rgba(24,20,33,.72); color:#c9bddf; font:11px 'DM Mono',monospace; letter-spacing:.09em; text-transform:uppercase; }
.pulse { width:7px; height:7px; border-radius:50%; background:#b79af5; box-shadow:0 0 11px #a477f5; }
.hero h2 { margin:22px auto 13px; max-width:850px; color:#f7f4fc; font-size:clamp(42px,6.4vw,76px); line-height:1.02; font-weight:800; letter-spacing:-.075em; }
.hero h2 span { color:#c0a4ff; text-shadow:0 0 32px rgba(154,107,241,.33); }
.hero-copy { max-width:650px; margin:0 auto; color:#aaa5b6; font-size:15px; line-height:1.8; }
.hero-foot { display:flex; justify-content:center; align-items:center; gap:9px; flex-wrap:wrap; margin:23px auto 0; color:#8f899f; font-size:11px; }
.hero-foot code { padding:5px 8px; border:1px solid rgba(207,188,248,.13); border-radius:7px; color:#d2c1f5; background:rgba(255,255,255,.035); font:11px 'DM Mono',monospace; }
.hero-foot .separator { color:#605a6b; }
.stApp [data-testid="stForm"] { max-width:850px; margin:21px auto 0; padding:14px; border:1px solid rgba(179,143,242,.32); border-radius:18px; background:linear-gradient(150deg,rgba(24,20,33,.95),rgba(14,12,20,.96)); box-shadow:0 15px 65px rgba(98,56,155,.14),0 0 34px rgba(149,106,227,.09); }
.stApp [data-testid="stForm"] [data-testid="stHorizontalBlock"] { align-items:end; gap:12px; }
.stApp [data-testid="stTextInput"] input, .stApp [data-testid="stSelectbox"] > div > div {
  min-height:48px; border:1px solid rgba(206,192,231,.16); border-radius:11px; background:#0b0a10; color:#f5f1fc;
}
.stApp [data-testid="stTextInput"] input::placeholder { color:#756e80; }
.stApp [data-testid="stTextInput"] label, .stApp [data-testid="stSelectbox"] label { color:#a8a1b5; font-size:12px; }
.stApp [data-testid="stFormSubmitButton"] button, .stApp button[kind="primary"] {
  min-height:48px; border:1px solid rgba(207,183,255,.42); border-radius:11px;
  background:linear-gradient(135deg,#a785ef,#7951c7); color:#fff; font-weight:700;
  transition:transform .18s ease, box-shadow .18s ease, filter .18s ease;
  box-shadow:0 6px 24px rgba(132,84,211,.20);
}
.stApp [data-testid="stFormSubmitButton"] button:hover, .stApp button[kind="primary"]:hover { transform:translateY(-1px); filter:brightness(1.08); box-shadow:0 8px 28px rgba(142,91,226,.34); }
.stApp button:focus-visible, .stApp input:focus-visible, .stApp [role="combobox"]:focus-visible { outline:2px solid #c2a5ff !important; outline-offset:3px; }
.quick-label { margin:5px 0 0; color:#898395; font:10px 'DM Mono',monospace; letter-spacing:.1em; text-align:center; text-transform:uppercase; }
.proof-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; max-width:850px; margin:28px auto 44px; }
.proof-card { padding:14px 16px; text-align:left; border:1px solid rgba(211,195,241,.12); border-radius:13px; background:linear-gradient(140deg,rgba(29,25,38,.72),rgba(17,15,23,.80)); }
.proof-kicker { color:#898395; font:10px 'DM Mono',monospace; letter-spacing:.08em; text-transform:uppercase; }
.proof-value { margin-top:6px; color:#ece7f7; font-size:14px; font-weight:700; }
.section-rule { height:1px; margin:0 0 28px; background:linear-gradient(90deg,transparent,rgba(193,168,239,.22),transparent); }
.stApp [data-testid="stVerticalBlockBorderWrapper"] { border-color:rgba(202,184,232,.14); border-radius:14px; background:rgba(20,18,27,.68); }
.stApp [data-testid="stExpander"] { border-color:rgba(202,184,232,.16); border-radius:10px; background:rgba(9,8,13,.45); }
.stApp [data-testid="stAlert"] { background:rgba(27,23,36,.9); border-color:rgba(182,152,229,.22); color:#ddd7e9; }
.stApp [data-testid="stMetric"] { padding:12px; border:1px solid var(--line); border-radius:12px; background:#14111b; }
.stApp [data-testid="stMetricLabel"] { color:#aaa2b5; }
.stApp [data-testid="stMetricValue"] { color:#f1ebfc; }
.stApp [data-testid="stFileUploader"] section { border-color:rgba(202,184,232,.24); background:#14111b; }
.stApp [data-testid="stCheckbox"] label { color:#d0c9da; }
.stApp [data-testid="stMarkdownContainer"] code { color:#d4c3fa; background:rgba(161,125,221,.11); }
.mono { font-family:'DM Mono',monospace; }
@media (max-width: 760px) {
  .block-container { padding: .8rem 1rem 3rem; }
  .topline { padding-bottom:25px; }
  .brand-sub { display:none; }
  .hero { padding:48px 3px 10px; }
  .hero h2 { font-size:clamp(40px,11vw,60px); }
  .hero-copy { font-size:14px; }
  .stApp [data-testid="stForm"] { padding:11px; margin-top:20px; }
  .stApp [data-testid="stForm"] [data-testid="stHorizontalBlock"] { flex-direction:column; gap:7px; }
  .stApp [data-testid="stForm"] [data-testid="column"] { width:100% !important; flex:1 1 100% !important; }
  .proof-grid { grid-template-columns:1fr; gap:8px; margin:22px auto 32px; }
  .proof-card { display:flex; justify-content:space-between; align-items:center; gap:10px; }
  .proof-value { margin:0; text-align:right; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior:auto !important; animation-duration:.01ms !important; animation-iteration-count:1 !important; transition-duration:.01ms !important; }
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


def main() -> None:
    st.set_page_config(
        page_title="Search Engine — inspectable document search",
        page_icon="⌕",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(PAGE_STYLES, unsafe_allow_html=True)

    if "engine" not in st.session_state:
        engine, load_error = _initial_engine()
        st.session_state.engine = engine
        st.session_state.sample_load_error = load_error
        st.session_state.last_search = None

    engine: SearchEngine = st.session_state.engine
    st.markdown(
        """
        <div class="topline">
          <div class="brand"><span class="brand-mark" aria-hidden="true">⌕</span>
            <span>SEARCH ENGINE</span><span class="brand-sub">/ built from first principles</span>
          </div>
          <span class="brand-sub">OPEN SOURCE · PYTHON</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # Keep a native Streamlit title for page semantics and smoke-test compatibility.
    st.title("Search Engine")
    st.markdown(
        f"""
        <section class="hero" aria-label="Search the collection">
          <span class="eyebrow"><span class="pulse"></span> A small search engine, made inspectable</span>
          <h2>Find what matters.<br><span>See how it ranks.</span></h2>
          <p class="hero-copy">Search your documents with a transparent retrieval pipeline —
            from an inverted index to deterministic TF‑IDF ranking.</p>
          <div class="hero-foot"><code>{engine.count()} sample documents</code>
            <span class="separator">/</span><code>AND · OR · quoted phrases</code>
            <span class="separator">/</span><code>Python · no black box</code>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.sample_load_error:
        st.warning(st.session_state.sample_load_error)

    with st.sidebar:
        st.markdown("### Your collection")
        st.caption(
            "Add files to this session's index. Uploads are not written to server storage. "
            "TXT and Markdown use UTF-8; PDFs must contain extractable text."
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
        st.caption("QUERY SYNTAX")
        st.markdown(
            "Bare terms use OR semantics. `AND` requires every term; `OR` accepts either side. "
            'Use quotes for a phrase, for example `"search systems"`. '
            "The collection resets when your session ends."
        )

    query_assistant = GeminiQueryAssistant()
    with st.form("search_form"):
        query_col, limit_col = st.columns([5, 1])
        with query_col:
            query = st.text_input(
                "Search the collection",
                placeholder='Try “search systems” or python AND index',
            )
        with limit_col:
            limit = st.selectbox("Results", options=[5, 10, 20, 50], index=1)
        submitted = st.form_submit_button("Search", type="primary", use_container_width=True)
    st.markdown(
        '<p class="quick-label">Try a query &nbsp; · &nbsp; python &nbsp; · &nbsp; '
        'python AND search &nbsp; · &nbsp; "search systems"</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="proof-grid" aria-label="How search works">
          <div class="proof-card"><div class="proof-kicker">01 / Index</div><div class="proof-value">Inverted postings</div></div>
          <div class="proof-card"><div class="proof-kicker">02 / Match</div><div class="proof-value">Boolean + phrases</div></div>
          <div class="proof-card"><div class="proof-kicker">03 / Rank</div><div class="proof-value">TF‑IDF · stable ties</div></div>
        </div>
        <div class="section-rule"></div>
        """,
        unsafe_allow_html=True,
    )

    improve_query = st.checkbox(
        "Improve plain-text queries with Gemini",
        value=False,
        help=(
            "Sends the query text to Google's Gemini API for a rewrite. "
            "Search results still come only from your indexed documents."
        ),
    )
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
                    st.warning("AI assistance is not configured. Searching with the original query.")
                elif not is_simple_query(query):
                    st.info("Boolean and quoted phrase queries stay unchanged to preserve syntax.")
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
                    st.caption(f"Document ID {document_id} · TF‑IDF score {score:.6f}")
                    st.write(_excerpt(document.text, tuple(search_state["terms"])))
                    with st.expander("View full extracted text"):
                        st.text(document.text)
    else:
        st.caption(
            "The sample collection is ready. Search above, or open **Your collection** to add "
            "TXT, Markdown, or text-based PDF documents."
        )


if __name__ == "__main__":
    main()
