"""Validation entry point.

Re-uses `ingest_all` in dry-run + strict mode. Used by `bun run validate`
to catch broken content (invalid frontmatter, unresolved links, drift
from the ontology) before commit.
"""

from __future__ import annotations

import sys

from rich.console import Console

from .ingest import IngestError, ingest_all

console = Console()


def main() -> None:
    try:
        ingest_all(dry_run=True, strict=True, skip_embeddings=True)
    except IngestError as e:
        console.print(f"[red]✗ validate failed:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
