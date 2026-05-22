# Static public site (adapter-static)

> **Status: superseded by [ADR 0007](./0007-server-runtime-sqlite-vec.md)** — server runtime adopted to support backend ML, semantic search, and richer interactive queries. Retained for context on why the static path was first considered and what costs the move accepts.

The SvelteKit site is generated as pure static output (HTML + JS + JSON), with no server. The derived graph is pre-built into `graph.json` loaded by the client; Cytoscape renders it; search, filters, and exploration all run in the browser. Hosting on Cloudflare Pages / Vercel / GitHub Pages, zero cost.

## Why

- Personal project, public read-only, single editor — no requirement demands a server.
- Zero operational cost, zero downtime, no ops to maintain.
- Estimated scale (5–15k Nodes, 50–100k Edges) fits comfortably in gzipped JSON + Cytoscape on the client.
- Future migration to `adapter-node` is mechanical (swap adapter, expose queries as `+server.ts`), not structural — not worth paying the complexity now.

## Consequences

- Arbitrary graph queries run client-side. Single user, modern browser, fine.
- Semantic search via embeddings, when added, will either embed vectors into the JSON (heavy) or require migrating to a server runtime — accepted as deferred cost.
- The generated JSON should be splittable (load metadata + edges on init, load Note bodies on demand) once the graph grows — but not pre-optimized now.
