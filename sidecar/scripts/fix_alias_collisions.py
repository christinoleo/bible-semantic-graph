"""One-shot fix for alias collisions introduced by the bulk-seed agents.

Strategy:
  1. **Book vs Person collisions** — when a book Node's `name` (or any alias)
     slugifies to a slug already owned by a person, the book always gets the
     "Book of X" / "Gospel of X" / "Letter to X" form, and any alias whose
     slugify-form collides is stripped.
  2. **Person-vs-Person ambiguous names** — short ambiguous aliases (Miriam,
     Saul, Yohanan, etc.) are stripped from all but the canonical claimant,
     OR from all of them (forcing explicit-slug wiki-links).

Matching is done by `slugify()` so it catches Greek, Hebrew, transliteration,
and diacritic variants automatically (e.g., `Ἀμώς`, `ʿĀmôs`, `Amos` all
slugify to `amos`).
"""

from __future__ import annotations

from pathlib import Path

import frontmatter

ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / "content"

import sys

sys.path.insert(0, str(ROOT / "sidecar"))
from pipeline.slugify import slugify  # noqa: E402

# slug → new `name` field (forces canonical title that doesn't collide)
RENAME_NAME: dict[str, str] = {
    # OT prophetic books
    "book-of-isaiah": "Book of Isaiah",
    "book-of-jeremiah": "Book of Jeremiah",
    "book-of-ezekiel": "Book of Ezekiel",
    "book-of-daniel": "Book of Daniel",
    "book-of-hosea": "Book of Hosea",
    "book-of-joel": "Book of Joel",
    "book-of-amos": "Book of Amos",
    "book-of-obadiah": "Book of Obadiah",
    "book-of-jonah": "Book of Jonah",
    "book-of-micah": "Book of Micah",
    "book-of-nahum": "Book of Nahum",
    "book-of-habakkuk": "Book of Habakkuk",
    "book-of-zephaniah": "Book of Zephaniah",
    "book-of-haggai": "Book of Haggai",
    "book-of-zechariah": "Book of Zechariah",
    "book-of-malachi": "Book of Malachi",
    # OT historical
    "book-of-joshua": "Book of Joshua",
    "book-of-ruth": "Book of Ruth",
    "book-of-esther": "Book of Esther",
    "book-of-ezra": "Book of Ezra",
    "book-of-nehemiah": "Book of Nehemiah",
    "book-of-job": "Book of Job",
    # Gospels
    "gospel-of-matthew": "Gospel of Matthew",
    "gospel-of-mark": "Gospel of Mark",
    "gospel-of-luke": "Gospel of Luke",
    "gospel-of-john": "Gospel of John",
    # NT epistles that collide with persons
    "james": "Letter of James",
    "jude": "Letter of Jude",
    "titus": "Letter to Titus",
    "philemon": "Letter to Philemon",
    "1-john": "First Letter of John",
    "2-john": "Second Letter of John",
    "3-john": "Third Letter of John",
    "1-peter": "First Letter of Peter",
    "2-peter": "Second Letter of Peter",
    "1-timothy": "First Letter to Timothy",
    "2-timothy": "Second Letter to Timothy",
    # Persons with disambiguating display names
    "joseph-of-nazareth": "Joseph of Nazareth",
    "titus-companion": "Titus, companion of Paul",
    # Phase 1 apocrypha
    "book-of-susanna": "Book of Susanna",
    "book-of-tobit": "Book of Tobit",
    "book-of-judith": "Book of Judith",
    "book-of-baruch": "Book of Baruch",
}

# slug → set of slug-forms to strip from this Node's aliases.
# (Matching is by slugify(alias) ∈ forbidden_slugs.)
STRIP_BY_SLUG: dict[str, set[str]] = {
    # ── Books colliding with their eponymous person ───────────────────
    "book-of-isaiah":    {"isaiah"},
    "book-of-jeremiah":  {"jeremiah"},
    "book-of-ezekiel":   {"ezekiel"},
    "book-of-daniel":    {"daniel"},
    "book-of-hosea":     {"hosea", "hoshea"},
    "book-of-joel":      {"joel", "yoel"},
    "book-of-amos":      {"amos"},
    "book-of-jonah":     {"jonah", "yonah"},
    "book-of-micah":     {"micah"},
    "book-of-habakkuk":  {"habakkuk"},
    "book-of-zechariah": {"zechariah"},
    "book-of-malachi":   {"malachi"},
    "book-of-joshua":    {"joshua", "yehoshua", "hoshea"},
    "book-of-ruth":      {"ruth", "rut"},
    "book-of-esther":    {"esther", "ester", "hadassah"},
    "book-of-ezra":      {"ezra"},
    "book-of-nehemiah":  {"nehemiah"},
    "book-of-job":       {"job"},
    # ── Gospels colliding with evangelists ────────────────────────────
    "gospel-of-matthew": {"matthew", "mattaios", "mattityahu"},
    "gospel-of-mark":    {"mark", "markos"},
    "gospel-of-luke":    {"luke", "loukas"},
    "gospel-of-john":    {"john", "yohanan", "ioannes"},
    # ── NT epistles colliding with persons ────────────────────────────
    "james":     {"james", "iakobos", "yaakov", "yaaqov"},
    "jude":      {"jude", "judas", "yehuda", "ioudas"},
    "titus":     {"titus", "titos"},
    "philemon":  {"philemon", "philemon"},
    "1-john":    {"john", "yohanan", "ioannes"},
    "2-john":    {"john", "yohanan", "ioannes"},
    "3-john":    {"john", "yohanan", "ioannes"},
    "1-peter":   {"peter", "petros", "kephas"},
    "2-peter":   {"peter", "petros", "kephas"},
    "1-timothy": {"timothy", "timotheos"},
    "2-timothy": {"timothy", "timotheos"},
    # ── Persons (each disambiguates against shared aliases) ───────────
    "mary-mother-of-jesus": {"miriam", "mary", "maria"},
    "mary-magdalene":       {"miriam", "mary", "maria"},
    "mary-of-bethany":      {"miriam", "mary", "maria"},
    "paul":                 {"saul"},
    "matthew":              {"levi"},
    "james-son-of-zebedee":   {"james", "iakobos", "yaakov", "yaaqov"},
    "james-son-of-alphaeus":  {"james", "iakobos", "yaakov", "yaaqov"},
    "james-brother-of-jesus": {"james", "iakobos", "yaakov", "yaaqov"},
    "john-apostle":           {"john", "yohanan", "ioannes"},
    "john-the-baptist":       {"john", "yohanan", "ioannes"},
    "judas-iscariot":         {"judas", "yehuda", "ioudas"},
    "jude-brother-of-jesus":  {"jude", "judas", "yehuda", "ioudas"},
    "joseph-of-nazareth":     {"joseph", "yosef", "iosef"},
    # ── Person collisions w/ other persons ────────────────────────────
    "hosea":   {"hoshea"},   # joshua keeps the alias "Hoshea" (Num 13:16)
    # ── Phase 1 (apocrypha) collisions ────────────────────────────────
    "book-of-susanna":   {"susanna"},
    "book-of-tobit":     {"tobit", "tobias"},
    "book-of-judith":    {"judith", "jud"},
    "book-of-baruch":    {"baruch"},
    "bel-and-the-dragon": {"bel"},     # marduk owns "Bel" alias
    "jeshua-ben-sira":   {"sirach", "bensira"},
}


def fix_file(path: Path) -> tuple[bool, list[str]]:
    """Returns (changed?, list-of-stripped-aliases)."""
    slug = path.stem
    post = frontmatter.load(path)
    changed = False
    stripped: list[str] = []

    if slug in RENAME_NAME and post.metadata.get("name") != RENAME_NAME[slug]:
        post.metadata["name"] = RENAME_NAME[slug]
        changed = True

    if slug in STRIP_BY_SLUG:
        forbidden = STRIP_BY_SLUG[slug]
        orig = post.metadata.get("aliases") or []
        new = []
        for a in orig:
            if slugify(str(a)) in forbidden:
                stripped.append(a)
            else:
                new.append(a)
        if stripped:
            post.metadata["aliases"] = new
            changed = True

    if changed:
        path.write_text(frontmatter.dumps(post) + "\n")
    return changed, stripped


def main() -> None:
    fixed = 0
    for path in sorted(CONTENT.rglob("*.md")):
        changed, stripped = fix_file(path)
        if changed:
            note = (
                f"  stripped {stripped!r}" if stripped else "  renamed"
            )
            print(f"  fixed {path.relative_to(ROOT)}{note}")
            fixed += 1
    print(f"\n{fixed} files modified")


if __name__ == "__main__":
    main()
