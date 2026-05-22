# Bible Semantic Graph

Personal knowledge-graph CMS centered on the Bible. Connects biblical characters, events, places, texts, theological concepts, arguments, theories, and parallels with adjacent mythology. The graph is the product; pages are notes attached to each node.

> See [`CLAUDE.md`](./CLAUDE.md), [`CONTEXT.md`](./CONTEXT.md), and [`docs/adr/`](./docs/adr/) before touching anything.

## Quickstart

Prerequisites: [Bun](https://bun.sh) ≥ 1.3, [uv](https://github.com/astral-sh/uv) ≥ 0.11, Python ≥ 3.12.

```sh
bun install                    # installs concurrently at the root
cd app && bun install && cd ..  # SvelteKit deps
cd sidecar && uv sync && cd ..  # Python deps (slow first time — pulls torch + transformers)
bun run ingest                 # builds .db/index.sqlite from content/*.md
bun run dev                    # boots SvelteKit (7654) + Python sidecar (7655) + pipeline watcher
```

Open <http://localhost:7654>.

## Layout

```
content/            # markdown source of truth — one Node per .md file
ontology.yaml       # known node/edge types, inverse pairs, source readers
docs/adr/           # architectural decisions, numbered, append-only
app/                # SvelteKit (Bun, adapter-node)
sidecar/            # Python: pipeline (ingestion) + api (ML serving)
.db/                # generated SQLite — gitignored
```

## How a Node looks

```yaml
---
type: Person
name: Abraham
aliases: [Abram, Avraham, Ibrāhīm, אַבְרָהָם]
edges:
  - { type: father_of, target: isaac }
  - { type: lived_in, target: ur }
tags: [patriarch, genesis, covenant]
sources: ["Gen 11:26-25:11"]
---

Abraham was called by [[yhwh]] to leave [[ur]] for [[canaan]].
The [[sacrifice-of-isaac]] at [[moriah]] is central to the
[[abrahamic-covenant]].
```

The filename (`abraham.md`) IS the Node's ID. Type lives in frontmatter, not in the directory. Directories are cosmetic (`content/people/`, `content/events/`).
