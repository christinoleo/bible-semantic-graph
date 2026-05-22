# Markdown as the single source of truth

Each **Node** in the graph is a `.md` file versioned in Git, with frontmatter declaring its type and edges. Everything else (SQLite + vectors for the site, NetworkX for analysis/ML, the generated `graph.json`, any graph database introduced later) is a **derived index**, rebuilt from the markdown by an ingestion pipeline and disposable at any time.

## Why

The choice between FalkorDB, Postgres, Neo4j, etc. was blocking the project because each is good for one job (graph queries / text / ML) and bad for the others — none "wins" in isolation. By making markdown canonical, the decision stops being religious: each derived index serves a specific job and can be swapped without migrating content. Bonus: editing via Claude Code and Obsidian/VS Code stays trivial, and Git provides history, diff, and backup for free.

## Consequences

- Cost: must maintain an ingestion pipeline (markdown → SQLite / NetworkX / etc.). Estimated in hundreds of lines of Python, not thousands.
- Frontmatter becomes a critical contract — its schema must evolve carefully.
- A dedicated graph database (FalkorDB / Neo4j) remains a future option as **another** derived index, never as a replacement for markdown.
