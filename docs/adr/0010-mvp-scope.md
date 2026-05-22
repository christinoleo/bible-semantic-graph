# MVP scope

The MVP is a **wiki-style hyperlinked knowledge graph** — the graph exists as the data model but is **not** rendered as an interactive visualization. Users navigate through links, backlinks, and related-node suggestions. Visual graph rendering (Cytoscape or similar) is explicitly deferred to post-MVP.

## In scope

- **Pipeline (Python)**: walks `content/*.md`, validates frontmatter against the schema in ADR 0006, builds SQLite (`nodes`, `edges` with inferred reciprocity, FTS5 over name + aliases + body, sqlite-vec embeddings via sentence-transformers), maintains `ontology.yaml`. Runs in watch mode in dev, full rebuild in CI.
- **SvelteKit (Bun, `adapter-node`)**:
  - Node detail page: name, type(s), rendered body (mdsvex), outbound edges grouped by type, **backlinks** (inbound edges), expanded `sources:` as external Bible-reader links.
  - Global search bar: full-text (FTS5) + semantic (proxied to Python sidecar), unified ranked results.
  - Index routes: `/type/[type]`, `/tag/[tag]`, alphabetical listing.
  - Related-nodes block on each Node page (top-N by cosine similarity). **Exact UI placement TBD** — likely side-by-side or top, not footer.
- **Python sidecar (FastAPI / Litestar on `granian`)**:
  - Semantic search endpoint: encode query → vector search in SQLite → return ranked node IDs.
  - Embedding model loaded once at startup, kept in memory.
- **Seed content**: 10–30 Nodes exercising the schema end-to-end (a small genealogy, one event with multi-character involvement, one mythological parallel, one theological concept, one argument). Purpose: validate the pipeline and the rendering, not to be encyclopedic.
- **Process management**: a `justfile` (or `process-compose.yml`) that starts SvelteKit + Python sidecar + pipeline watcher with one command in dev.
- **Citation parser**: turns `"Gen 22:1-19"` into one or more external reader URLs (configurable template).

## Out of scope (deferred)

- Interactive graph visualization (Cytoscape, force-layout, etc.) — revisit once content volume justifies it.
- LLM chat-with-graph or any LLM-augmented retrieval.
- NetworkX algorithms exposed via the app (PageRank, community detection, etc.) — available in notebooks against the same SQLite.
- Multiple translations or interlinear readers for `sources:`.
- In-browser editing UI.
- Visual design polish (dark mode, custom typography, etc.) — minimal default styling for MVP.
- Authentication / multi-user.

## Why

- The user's stated value driver is "connecting knowledge I'm not picking up" — that's a hyperlinked navigation problem first, a visualization problem second.
- Deferring viz removes a substantial implementation chunk (~30–40% of frontend effort) from the critical path to first useful version.
- Everything in scope is small enough that a single focused session can stand it up end-to-end.

## Consequences

- The first usable version is text-and-link-driven, with semantic search as the main "smart" feature.
- Post-MVP work has a clear next milestone: graph viz on top of the existing SQLite + edges. No data model change required.
- "Related nodes" UI placement is intentionally unresolved — to be decided when the first version is actually being looked at.
