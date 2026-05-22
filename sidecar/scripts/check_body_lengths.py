"""Walk content/, report which Nodes violate the CLAUDE.md body-length caps.

Caps (per writing-style section of CLAUDE.md):
  - Argument:                          ≤ 5 body lines (1-3 sentences)
  - Concept, Theory, Event:            ≤ 12 body lines (1 short paragraph)
  - Person, Place, Text, Manuscript, Council, Deity, Mythological:
                                       ≤ 25 body lines (1-2 short paragraphs)

Exit code:
  0  — every Node within cap
  1  — at least one Node exceeds cap; details on stdout

`bun run check-bodies` is the convenient invocation.
"""

from __future__ import annotations

import sys
from pathlib import Path

import frontmatter

ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / "content"

CAPS: dict[str, int] = {
    "Argument": 5,
    "Concept": 12,
    "Theory": 12,
    "Event": 12,
    "Person": 25,
    "Place": 25,
    "Text": 25,
    "Manuscript": 25,
    "Council": 25,
    "Deity": 25,
    "Mythological": 25,
    "Tradition": 25,
    "Passage": 25,
}
DEFAULT_CAP = 25


def body_lines(body: str) -> int:
    """Non-empty content lines in the markdown body."""
    return sum(1 for line in body.splitlines() if line.strip())


def main() -> int:
    violators: list[tuple[Path, str, int, int]] = []
    total = 0
    for path in sorted(CONTENT.rglob("*.md")):
        post = frontmatter.load(path)
        node_type = (post.metadata or {}).get("type", "Concept")
        cap = CAPS.get(node_type, DEFAULT_CAP)
        n = body_lines(post.content)
        total += 1
        if n > cap:
            violators.append((path.relative_to(ROOT), node_type, n, cap))

    if not violators:
        print(f"✓ all {total} Nodes within body-length caps")
        return 0

    print(f"✗ {len(violators)}/{total} Nodes exceed body-length cap:\n")
    print(f"  {'TYPE':14s}  {'LINES':>5s}  {'CAP':>4s}  PATH")
    for path, t, n, cap in violators:
        print(f"  {t:14s}  {n:>5d}  {cap:>4d}  {path}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
