# Search Engine UI Design

## Product direction

Build a focused document-search workspace for **MugdhoAI / Search Engine**. The visual reference is the supplied HyperGit screenshot: a dark interface, a centered purple headline, a wide search field with a restrained violet glow, and compact dark cards.

Use the reference as visual inspiration only. Do not copy HyperGit branding, repository cards, navigation, labels, or product-specific content.

The application is a working search tool, not a marketing site. Keep search immediately usable and keep all existing search behavior intact.

## Experience goals

1. Make the search field the visual center of the page.
2. Explain the product in one short headline and one supporting sentence.
3. Give the interface a coherent purple identity.
4. Make indexed documents, upload controls, and search options easy to find without competing with search.
5. Present results as readable, structured cards.
6. Preserve Streamlit's responsive behavior and accessibility.

## Brand and copy

- Product name: **Search Engine**
- Brand label: **MugdhoAI**
- Primary headline: **Find what matters in your documents.**
- Supporting copy: **Search your collection with an inspectable inverted index and deterministic TF-IDF ranking.**
- Search placeholder: **Search documents, concepts, or exact phrases...**
- Keep copy factual. Do not claim semantic search, instant results, enterprise readiness, cloud persistence, or capabilities the implementation does not provide.

## Visual system

### Color tokens

| Token | Value | Use |
|---|---|---|
| App background | `#09080F` | Main canvas |
| Sidebar background | `#15121E` | Collection panel |
| Surface | `#1B1726` | Cards and secondary panels |
| Elevated surface | `#241C32` | Search field and expanded areas |
| Border | `#382A4B` | Subtle outlines |
| Primary purple | `#B86BFF` | Main accent |
| Bright purple | `#D49AFF` | Headline and focus states |
| Glow | `rgba(168, 85, 247, 0.28)` | Search focus only |
| Main text | `#F7F3FC` | Headings and body |
| Muted text | `#B8AD C5` | Supporting text; normalize to `#B8ADC5` |
| Success | `#65D6A2` | Successful upload/status |
| Warning | `#F2C879` | Warnings |
| Error | `#FF8585` | Errors |

Use purple as the identifying accent, not as a fill for every control. Keep text contrast high. Avoid gradients except for a subtle hero glow or search focus treatment.

### Typography

- Use the system sans-serif stack already available in the browser.
- Hero headline: bold, approximately 2.4–3rem on desktop and 1.8–2.1rem on narrow screens.
- Supporting copy: 1rem, muted, comfortable line height.
- Section headings: 1.05–1.2rem, semibold.
- Metadata: 0.78–0.88rem, muted.
- Avoid decorative typefaces and excessive uppercase labels.

### Shape and spacing

- Main content max width: approximately 1120px, centered.
- Search field: full available content width, 64–72px tall on desktop, rounded 14–16px.
- Cards and panels: 12–16px radius, 1px border.
- Use consistent spacing in 8px increments.
- Use shadows sparingly. The search field may have a subtle purple focus ring; ordinary cards should rely on surface contrast and borders.

## Page structure

### 1. Hero and search

Keep the hero compact and centered in the main content area.

Order:
1. Small brand eyebrow: `MUGDHOAI / SEARCH`.
2. Headline: `Find what matters in your documents.`
3. One-line description of the retrieval approach.
4. Wide search input with a search icon if it can be added accessibly.
5. Search action aligned with the input on desktop; stack cleanly on mobile.
6. A compact row of capability labels: `TF-IDF ranking`, `Boolean search`, `Phrase search`.

The search input must be the first major interactive element. Do not place a large illustration, navigation menu, or marketing section above it.

### 2. Search options

Place secondary options directly below the search field:
- Results limit.
- Optional Gemini query assistance.
- Explain that Gemini rewrites only plain-text queries; it does not generate answers or search results.
- Keep the default AI assistance state off.
- Preserve the warning when the API key is not configured.

Do not hide core query behavior or make Gemini appear required.

### 3. Search results

When a search has been submitted:
- Show the submitted query as the section heading.
- Show the number of matches and explain that results are ordered by TF-IDF score.
- Each result is a compact card.
- Show filename as the primary label.
- Show document ID and TF-IDF score as quiet metadata.
- Show a readable excerpt.
- Keep full extracted text inside an expander.
- Preserve the existing no-results and query-error states.

Do not invent snippets, relevance percentages, highlighting, file previews, or ranking explanations that the backend does not provide.

### 4. Empty state

When no search has been submitted:
- Show a concise empty state below the search area.
- Explain that the sample collection is ready.
- Direct users to add TXT, Markdown, or text-based PDF files from the collection panel.
- Keep the empty state visually quiet; it should not look like an error banner.

### 5. Document collection sidebar

Keep Streamlit's sidebar for collection management. Restyle and organize it rather than moving upload state into a new subsystem.

Order:
1. `Document collection` heading.
2. Short privacy and file-format note.
3. File uploader.
4. `Add selected files` action.
5. Indexed document count.
6. `Clear collection` action, visually secondary and clearly destructive.
7. Search syntax help in a collapsed expander or a compact help section.

The privacy note must continue to state that uploads are session-scoped and are not written to server storage. Keep the actual upload constraints accurate: 5 MiB per file, 100 pages per PDF, and 200,000 extracted characters. Do not change the server upload limit without checking the current configuration and ingestion validation.

## Interaction and behavior requirements

The redesign is visual and structural. Preserve all current application behavior:

- Sample collection loading and its error state.
- TXT, Markdown, and text-based PDF uploads.
- Duplicate detection by SHA-256.
- Session-only upload handling.
- Upload success, duplicate, and per-file error messages.
- Clear collection behavior.
- Search results limit options: 5, 10, 20, and 50.
- OR behavior for bare terms.
- Explicit AND and OR query behavior.
- Quoted phrase search.
- Optional Gemini rewrite for simple plain-text queries only.
- Boolean and quoted phrase queries remain unchanged by Gemini.
- Original query fallback when Gemini is unavailable or fails.
- Deterministic TF-IDF ranking.
- Result excerpts and expandable full text.
- Existing error and empty-result states.

Do not alter engine, parser, ranking, storage, ingestion, or query-assistance semantics as part of this UI task.

## Responsive behavior

- Desktop: centered hero and wide search field; sidebar remains available.
- Tablet: reduce hero spacing and allow controls to wrap.
- Mobile: use the full content width, reduce horizontal padding, stack search controls, and avoid horizontal overflow.
- Keep the sidebar usable through Streamlit's native sidebar behavior.
- Never use fixed pixel widths for the main search area.

## Accessibility

- Keep visible labels for inputs; do not rely only on placeholders.
- Preserve keyboard navigation and native Streamlit form submission.
- Maintain sufficient contrast for body text, metadata, focus indicators, and buttons.
- Do not encode success, warning, or error using color alone.
- Avoid CSS that removes focus outlines or hides Streamlit controls from assistive technology.

## Implementation boundaries

- Continue using Streamlit; do not introduce React, a separate API, a database, or a new frontend build system.
- Use scoped CSS selectors and stable Streamlit-supported selectors where possible.
- Avoid brittle selectors tied to generated class names.
- Do not use JavaScript injection.
- Keep custom HTML limited to decorative, non-interactive elements. Inputs, buttons, uploaders, forms, expanders, and status messages must remain native Streamlit components.
- Keep the page usable if custom CSS fails to load.
- Do not add external font, icon, or CSS dependencies.
- Do not add fake branding or a new logo. Use a simple text brand mark unless a verified project logo already exists.

## Acceptance criteria

- The first screen clearly resembles the supplied dark-purple reference in tone and hierarchy.
- The hero is compact and does not push search below the initial viewport on common desktop screens.
- The search field is wide and visually dominant.
- The sidebar is quieter but still functional.
- Results are easier to scan and visually separated.
- Mobile layout has no horizontal overflow.
- All existing behaviors listed above remain unchanged.
- Existing tests pass and new UI tests cover any behavior changed by the implementation.
