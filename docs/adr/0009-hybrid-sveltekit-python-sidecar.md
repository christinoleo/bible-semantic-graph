# Hybrid runtime: SvelteKit + Python sidecar

The deployed application runs **two long-lived processes** on the same host, sharing the SQLite database via filesystem:

1. **SvelteKit server** (Bun, `adapter-node`) — owns the user-facing surface: SSR of pages, route loaders, simple SQLite reads (Node lookups, edge expansion, tag/type lists, full-text search via FTS5), static assets, the graph viz bootstrap.
2. **Python ML service** (FastAPI on `granian` or Litestar) — owns ML-heavy endpoints: semantic query encoding (sentence-transformers in-memory), vector search execution (sqlite-vec queries), future LLM tool-use orchestration, NetworkX algorithms on demand (path finding, centrality, community detection), reranking with cross-encoders.

The SvelteKit server proxies ML requests to the Python service over `localhost` HTTP. SQLite is read by both processes; only the pipeline writes.

Both processes are supervised (in prod: systemd / docker-compose / single container with supervisord; in dev: process-compose or overmind starts SvelteKit, the Python service, and the pipeline watcher together).

## Why

- **Each language does what it's best at.** TypeScript/Svelte for UI and conventional web concerns; Python for ML/NLP/graph algorithms where the ecosystem is decisively stronger.
- **No early commitment to "we'll port Python to JS later"** or vice versa — the boundary is the HTTP API between them, which is the cheapest possible coupling.
- **Anticipated features make Python serve-time real**, not aspirational: LLM tool-use with NetworkX in the loop, embedding-based rerankers, possibly GraphRAG. Going hybrid day-1 avoids retrofitting under feature pressure.
- **SQLite handles the shared-state problem cleanly**: WAL mode supports multiple concurrent readers; a single writer (the pipeline) avoids contention. No message bus, no replication.

## Consequences

- **Deploy unit is the VM, not a static bundle.** Targets: Fly.io (~$3–5/mo), Hetzner CX11 (~€4/mo), or self-hosted. Single container or docker-compose with both processes; persistent volume for `.db/`.
- **Two processes to monitor.** In dev, a process manager is required, not optional. Some `justfile` / Procfile / `process-compose.yml` is part of the repo from day 1.
- **The contract between SvelteKit and Python is an internal HTTP API.** Schema it deliberately (typed in TS, typed in Python via Pydantic) to avoid drift. Localhost-only — no auth needed on the wire, but bind to `127.0.0.1` explicitly.
- **Embedding model choice is a coordination point.** The Python service uses one model for both ingestion (offline, in pipeline) and query encoding (online, in serve-time). Pipeline embeddings and live query embeddings must come from the exact same model.
- **Future graph database (FalkorDB / Neo4j), if ever added, would also be a sidecar** — same pattern.
