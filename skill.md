# Search Engine UI Implementation Skill

## Purpose

Implement the interface defined in [design.md](design.md) for the existing Streamlit application. Treat `design.md` as the binding visual and interaction specification. If an implementation detail conflicts with it, follow `design.md` unless doing so would break an existing feature or Streamlit compatibility.

This is a repository-specific implementation guide, not a general UI framework.

## Source of truth

Before editing:
1. Read `design.md` completely.
2. Read `src/search_engine/web_app.py` completely.
3. Read the ingestion, query-assistance, engine, and storage modules that the UI calls.
4. Read relevant tests and the current Streamlit configuration.
5. Confirm the current branch and working tree before making changes.

Do not assume behavior from labels or README prose. Verify it in code and tests.

## Target files

Primary:
- `src/search_engine/web_app.py`

Possible supporting files:
- `.streamlit/config.toml` for supported theme defaults only.
- `tests/` for focused UI behavior tests.
- `assets/` only if a real, useful project asset is needed.

Do not create a separate frontend application or add a frontend framework.

## Visual implementation

Implement the dark purple workspace from `design.md`:

- Deep near-black purple page background.
- Slightly lighter purple sidebar and card surfaces.
- Violet headline and restrained purple accents.
- Centered, compact hero.
- Wide search input as the dominant control.
- Compact capability labels.
- Quiet secondary search options.
- Structured result cards with readable metadata.
- A subdued empty state.

Use the exact color tokens and hierarchy in `design.md`. Do not introduce a second accent palette or drift back to the current blue theme.

The HyperGit screenshot is a visual reference only. Do not reuse its name, logo, copy, repository cards, or navigation.

## Functional invariants

The following are non-negotiable. Preserve them unless a separate, explicitly approved issue requires a behavior change:

1. Sample documents load into a new session.
2. Sample collection load failures remain visible.
3. TXT, Markdown, and text-based PDF uploads remain supported.
4. Uploads remain session-scoped and are not persisted to server storage.
5. Duplicate files remain detected by SHA-256.
6. Existing upload limits and validation remain enforced.
7. Upload success, duplicate, and per-file errors remain visible.
8. Clearing the collection resets the engine and last search.
9. Search limits remain 5, 10, 20, and 50.
10. Bare terms retain OR semantics.
11. Explicit AND and OR queries retain their current parser behavior.
12. Quoted phrase queries retain their current behavior.
13. Gemini query assistance remains optional and off by default.
14. Gemini only rewrites eligible plain-text queries.
15. Boolean and quoted phrase queries are not rewritten.
16. Missing configuration and provider errors fall back to the original query.
17. Results remain ordered by the engine's deterministic TF-IDF ranking.
18. Result excerpts and expandable full extracted text remain available.
19. Empty, invalid-query, and no-match states remain clear.

Do not move search logic into presentation code. Keep calls to `SearchEngine`, `extract_text`, `GeminiQueryAssistant`, and `JsonStore` consistent with their existing contracts.

## Streamlit implementation rules

- Use native Streamlit widgets for every interactive control.
- Keep the search input and submit button inside a Streamlit form.
- Keep visible labels for form controls.
- Keep the Gemini help text accurate about what is sent to Google.
- Use native sidebar, uploader, button, metric, expander, and status components.
- Use CSS only for presentation.
- Prefer scoped selectors and stable attributes; avoid generated class names and fragile DOM assumptions.
- Do not inject JavaScript.
- Do not replace native controls with decorative HTML.
- Do not add external CSS, JavaScript, font, or icon dependencies.
- Avoid global styling that breaks Streamlit menus, dialogs, tooltips, forms, or accessibility.
- Keep a functional baseline if custom CSS is unavailable.
- Check that CSS does not hide controls or remove keyboard focus indicators.

## Code quality

- Keep the implementation readable and modular.
- Extract CSS into a clearly named constant or helper if that makes the page function easier to maintain.
- Avoid unnecessary dependencies and broad refactors.
- Avoid changing engine modules, parser semantics, ranking, ingestion, or storage for cosmetic reasons.
- Preserve existing type annotations and error handling.
- Do not swallow exceptions or replace useful messages with generic ones.
- Keep copy concise, factual, and consistent with `design.md`.

## Verification

After implementation:

1. Run the full test suite with `python -m pytest`.
2. Run lint with `python -m ruff check src tests`.
3. Run the existing evaluation script if the environment permits.
4. Run a Streamlit startup or app smoke test if the environment permits.
5. Inspect the diff for accidental changes to search semantics, upload constraints, privacy behavior, and query assistance.
6. Verify the initial state, successful search, no-result state, upload state, and sidebar controls through an actual browser preview when available.
7. Check a narrow viewport for horizontal overflow when browser preview is available.

If browser preview or deployment access is unavailable, state that visual verification was not performed. Do not claim to have visually tested the hosted app based only on source inspection.

## Completion criteria

The task is complete only when:
- The implementation follows `design.md`.
- All functional invariants are preserved.
- Tests and lint pass, or any environment limitation is reported precisely.
- The final diff is reviewed.
- The implementation is committed on the feature branch and presented for review through a pull request.

Do not merge the pull request without the user's explicit approval.
