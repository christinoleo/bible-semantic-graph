"""Add `canon` field to the 66 already-existing Bible book Nodes.

Run once after the schema changed to accept `canon`. Idempotent — re-running
is safe and leaves already-correct files untouched.

Convention:
- All 39 OT books → [tanakh, protestant, catholic, orthodox-eastern, orthodox-ethiopian]
- All 27 NT books → [protestant, catholic, orthodox-eastern, orthodox-ethiopian]
- Apocryphal/deuterocanonical books carry their own `canon:` declarations
  (set by the agents writing them, not by this script).
"""

from __future__ import annotations

from pathlib import Path

import frontmatter

ROOT = Path(__file__).resolve().parents[2]
TEXTS = ROOT / "content" / "texts"

OT_SLUGS = {
    "genesis", "exodus", "leviticus", "numbers", "deuteronomy",
    "book-of-joshua", "judges", "book-of-ruth",
    "1-samuel", "2-samuel", "1-kings", "2-kings",
    "1-chronicles", "2-chronicles",
    "book-of-ezra", "book-of-nehemiah", "book-of-esther",
    "book-of-job", "psalms", "proverbs", "ecclesiastes", "song-of-songs",
    "book-of-isaiah", "book-of-jeremiah", "lamentations",
    "book-of-ezekiel", "book-of-daniel",
    "book-of-hosea", "book-of-joel", "book-of-amos", "book-of-obadiah",
    "book-of-jonah", "book-of-micah", "book-of-nahum", "book-of-habakkuk",
    "book-of-zephaniah", "book-of-haggai", "book-of-zechariah", "book-of-malachi",
}

NT_SLUGS = {
    "gospel-of-matthew", "gospel-of-mark", "gospel-of-luke", "gospel-of-john", "acts",
    "romans", "1-corinthians", "2-corinthians", "galatians", "ephesians",
    "philippians", "colossians", "1-thessalonians", "2-thessalonians",
    "1-timothy", "2-timothy", "titus", "philemon",
    "hebrews", "james", "1-peter", "2-peter",
    "1-john", "2-john", "3-john", "jude", "revelation",
}

OT_CANON = ["tanakh", "protestant", "catholic", "orthodox-eastern", "orthodox-ethiopian"]
NT_CANON = ["protestant", "catholic", "orthodox-eastern", "orthodox-ethiopian"]


def main() -> None:
    changed = 0
    for path in sorted(TEXTS.glob("*.md")):
        slug = path.stem
        if slug in OT_SLUGS:
            wanted = OT_CANON
        elif slug in NT_SLUGS:
            wanted = NT_CANON
        else:
            # Apocryphal etc. — written by agents, leave alone.
            continue

        post = frontmatter.load(path)
        if post.metadata.get("canon") == wanted:
            continue
        post.metadata["canon"] = wanted
        path.write_text(frontmatter.dumps(post) + "\n")
        print(f"  canon ← {wanted}  on {path.relative_to(ROOT)}")
        changed += 1

    print(f"\n{changed} files updated")


if __name__ == "__main__":
    main()
