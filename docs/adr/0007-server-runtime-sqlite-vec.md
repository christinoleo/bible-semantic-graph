# Server runtime: SvelteKit on Bun + SQLite with sqlite-vec

**Supersedes [ADR 0005](./0005-static-runtime.md).**

The SvelteKit app uses `adapter-node` and runs on Bun. The primary derived index is a single SQLite database (`app/.db/index.sqlite`) with the **sqlite-vec** extension loaded, holding:

- Node metadata (id/slug, type, name, aliases, tags, sources)
- Edge table (typed, with inferred reciprocity materialized)
- FTS5 virtual table over Note bodies + names + aliases
- Vector table (sqlite-vec) of Note embeddings

The Python pipeline (`pipeline/`) is the only writer: it walks `content/*.md`, generates embeddings via sentence-transformers, and writes to SQLite. In dev it runs in watch mode, re-indexing on save. In CI/deploy the pipeline runs once against the markdown, the resulting SQLite file is built fresh from canonical markdown and shipped as part of the release artifact.

The SvelteKit server reads SQLite at runtime (via Bun's native `bun:sqlite` or `better-sqlite3`) for page rendering and simple endpoints. **ML-heavy work (query encoding, vector search execution, NetworkX algorithms, future LLM tool-use) lives in a Python sidecar service** — see [ADR 0009](./0009-hybrid-sveltekit-python-sidecar.md) for the split.

## Why

- ML and semantic search both fit naturally server-side: query encoding happens on the server with a single shared model in memory, not 50–150MB shipped to every browser.
- Anticipated future features (saved queries, LLM tool-use, exposed API for notebooks) are server-shaped, not client-shaped.
- SQLite + sqlite-vec is the right embedded store for this scale: zero ops, single-file, transactional, supports FTS5 and vector search in one place. No Redis, no Postgres, no separate vector DB.
- The "markdown is source of truth, indices are derived" principle (ADR 0001) is preserved: SQLite is regenerated from markdown by the pipeline; losing the DB means a single rebuild.
- Bun is the runtime (matches the JS tooling default and gives fast SQLite + low cold-start).

## Consequences

- Deploy target shifts from static host to a small VM or managed Node host (Fly.io, Railway, Render, or self-host). Cost: ~$0–5/mo on Fly.io free tier, or free on self-hosted hardware.
- The deploy unit includes the prebuilt SQLite file. No live-reindex on the production server — production SQLite is replaced atomically on each deploy. (Future: webhook-triggered rebuild on `content/` push.)
- Notebooks open the same SQLite file (or a synced copy / parquet export). No need for a separate analysis store.
- A graph database like FalkorDB/Neo4j remains an option only if a specific query pattern proves intolerably slow on SQLite — not anticipated within the next scale tier.
- The original static-site benefits (free hosting, zero ops, no cold start) are explicitly traded for capability. We accept this.
