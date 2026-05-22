# Monorepo layout, pipeline in watch + CI

A single repository contains `content/` (markdown source of truth), `app/` (SvelteKit on Bun), `sidecar/` (Python ML service + ingestion pipeline), `docs/adr/`, and `CONTEXT.md`. The pipeline runs in **watch mode during dev** (re-indexes on each `.md` save, writing to a shared `.db/index.sqlite`) and from scratch in **CI / deploy**. No pre-commit hook, no manual invocation. See [ADR 0009](./0009-hybrid-sveltekit-python-sidecar.md) for the SvelteKit / Python split.

## Why

- **Monorepo**: solo project, single mental model. Changes that cross content + schema + rendering go in one commit. Splitting into separate repos later is trivial (`git filter-repo`); going the other way is not.
- **Watch in dev**: the author wants to see the graph update while editing. Pre-commit is slow (commits are frequent in a personal project); on-demand gets forgotten.
- **Rebuild in CI**: guarantees the public site always derives from the canonical markdown, never from a stale index.

## Consequences

- Three processes in dev: `bun --cwd app dev` (SvelteKit), the Python ML sidecar, and the pipeline watcher. Justifies a `justfile` / `process-compose.yml` from day 1.
- Generated artifacts (`.db/`, any encoder model caches) live in `.gitignore` — only markdown, `ontology.yaml`, and source code are versioned.
