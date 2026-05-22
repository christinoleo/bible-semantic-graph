"""Watch content/ and re-ingest on changes.

Uses `watchfiles` (Rust-backed, fast). Debounces tightly so a burst of
saves coalesces into one ingest.
"""

from __future__ import annotations

import sys
from rich.console import Console
from watchfiles import watch

from . import paths
from .ingest import IngestError, ingest_all

console = Console()


def main() -> None:
    console.print(f"[cyan]watch[/cyan] {paths.CONTENT_DIR}")
    # Initial ingest
    try:
        ingest_all()
    except IngestError as e:
        console.print(f"[red]✗ initial ingest failed:[/red] {e}")

    for changes in watch(paths.CONTENT_DIR, paths.ONTOLOGY_PATH, step=200):
        changed = ", ".join(sorted({str(p) for _, p in changes})[:3])
        suffix = f" (+{len(changes) - 3} more)" if len(changes) > 3 else ""
        console.print(f"[dim]changed: {changed}{suffix}[/dim]")
        try:
            ingest_all()
        except IngestError as e:
            console.print(f"[red]✗ ingest failed:[/red] {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
