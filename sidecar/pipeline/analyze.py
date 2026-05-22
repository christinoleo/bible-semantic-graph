"""Quick argument-corpus analysis.

Reads `.db/index.sqlite` and prints distributions across the four
argumentation axes plus a few cross-cuts useful for finding gaps and
patterns. Run via `bun run analyze` (or `uv run python -m pipeline.analyze`).

What this answers at a glance:
  - How many Arguments do I have? Coverage by stance/tradition/method/subject?
  - Which stance × tradition combinations are over- or under-represented?
  - Which Arguments lack refuted_by / responds_to edges (one-sided positions)?
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .db import open_db
from . import paths

console = Console()


def main() -> None:
    if not paths.DB_PATH.exists():
        console.print("[red]No DB at {}. Run `bun run ingest` first.[/red]".format(paths.DB_PATH))
        sys.exit(1)
    conn = open_db(paths.DB_PATH)

    # --- Total Argument count and coverage ----------------------------
    total = list(conn.execute(
        "SELECT COUNT(*) FROM nodes WHERE type = 'Argument'"
    ))[0][0]
    console.print(f"\n[bold]Argument corpus: {total} Nodes[/bold]\n")

    if total == 0:
        console.print("[yellow]No Arguments yet. Add some Nodes with type: Argument.[/yellow]")
        return

    # Collect all argumentations from Argument-typed Nodes
    rows = list(conn.execute(
        "SELECT slug, name, argumentation_json FROM nodes "
        "WHERE type = 'Argument' AND argumentation_json IS NOT NULL"
    ))
    args = [(slug, name, json.loads(arg)) for slug, name, arg in rows]

    # --- Per-axis distribution ----------------------------------------
    for axis in ("stance", "tradition", "method", "subject"):
        counter: Counter[str] = Counter()
        for _, _, arg in args:
            for v in arg.get(axis, []):
                counter[v] += 1
        t = Table(title=f"{axis} distribution")
        t.add_column("value")
        t.add_column("count", justify="right")
        t.add_column("share", justify="right")
        for value, count in counter.most_common():
            share = f"{100 * count / total:.0f}%"
            t.add_row(value, str(count), share)
        console.print(t)

    # --- Stance × Tradition cross-tab ---------------------------------
    cross: dict[tuple[str, str], int] = defaultdict(int)
    stances: set[str] = set()
    traditions: set[str] = set()
    for _, _, arg in args:
        for s in arg.get("stance", []):
            stances.add(s)
            for tr in arg.get("tradition", []):
                traditions.add(tr)
                cross[(s, tr)] += 1
    if cross:
        t = Table(title="stance × tradition (counts)")
        t.add_column("stance \\ tradition")
        sorted_tr = sorted(traditions)
        for tr in sorted_tr:
            t.add_column(tr, justify="right")
        for s in sorted(stances):
            row = [s]
            for tr in sorted_tr:
                n = cross.get((s, tr), 0)
                row.append(str(n) if n else "·")
            t.add_row(*row)
        console.print(t)

    # --- One-sided arguments (no refuted_by) --------------------------
    one_sided = list(conn.execute(
        """
        SELECT n.slug, n.name FROM nodes n
        WHERE n.type = 'Argument'
          AND NOT EXISTS (
            SELECT 1 FROM edges e
            WHERE e.target = n.slug
              AND e.type IN ('refutes', 'refuted_by', 'responds_to')
          )
        """
    ))
    if one_sided:
        t = Table(title=f"Arguments with no recorded counter-response ({len(one_sided)})")
        t.add_column("slug")
        t.add_column("name")
        for slug, name in one_sided[:30]:
            t.add_row(slug, name)
        if len(one_sided) > 30:
            t.caption = f"… and {len(one_sided) - 30} more"
        console.print(t)


if __name__ == "__main__":
    main()
