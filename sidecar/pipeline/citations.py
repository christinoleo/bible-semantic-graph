"""Citation parser: turns a string like "Gen 22:1-19" into an external reader URL.

Configurable via `ontology.yaml::source_readers`. Reader URL templates use
placeholders: {book}, {chapter}, {verse_start}, {verse_end}.

We're intentionally permissive: anything we don't recognize becomes a
plain-text passthrough (the source string is rendered as-is in the UI).
The pipeline emits a warning when a citation can't be parsed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Common abbreviation → reader-friendly book name. Extend as needed.
BOOK_ALIASES: dict[str, str] = {
    "gen": "Genesis",
    "ex": "Exodus",
    "exod": "Exodus",
    "lev": "Leviticus",
    "num": "Numbers",
    "deut": "Deuteronomy",
    "josh": "Joshua",
    "judg": "Judges",
    "ruth": "Ruth",
    "1sam": "1 Samuel",
    "2sam": "2 Samuel",
    "1kgs": "1 Kings",
    "2kgs": "2 Kings",
    "ps": "Psalms",
    "psa": "Psalms",
    "prov": "Proverbs",
    "eccl": "Ecclesiastes",
    "isa": "Isaiah",
    "jer": "Jeremiah",
    "ezek": "Ezekiel",
    "dan": "Daniel",
    "matt": "Matthew",
    "mt": "Matthew",
    "mk": "Mark",
    "lk": "Luke",
    "jn": "John",
    "acts": "Acts",
    "rom": "Romans",
    "1cor": "1 Corinthians",
    "2cor": "2 Corinthians",
    "gal": "Galatians",
    "eph": "Ephesians",
    "phil": "Philippians",
    "col": "Colossians",
    "1thess": "1 Thessalonians",
    "2thess": "2 Thessalonians",
    "heb": "Hebrews",
    "jas": "James",
    "1pet": "1 Peter",
    "2pet": "2 Peter",
    "rev": "Revelation",
}

# Handles: "Gen 22", "Gen 21-26", "Gen 22:1", "Gen 22:1-19", "Gen 11:26-25:11"
CITATION_RE = re.compile(
    r"^\s*(?P<book>(?:\d\s*)?[A-Za-z]+)\s*"
    r"(?P<chapter>\d+)"
    r"(?::(?P<verse_start>\d+))?"
    r"(?:-(?:(?P<end_chapter>\d+):)?(?P<end_verse>\d+))?\s*$"
)


@dataclass(frozen=True)
class Citation:
    book: str
    chapter: int
    verse_start: int | None
    end_chapter: int | None
    end_verse: int | None
    raw: str

    @property
    def passage(self) -> str:
        """Render the chapter/verse portion (after the book name)."""
        out = str(self.chapter)
        if self.verse_start is not None:
            out += f":{self.verse_start}"
        if self.end_verse is not None:
            if self.end_chapter is not None:
                out += f"-{self.end_chapter}:{self.end_verse}"
            else:
                out += f"-{self.end_verse}"
        return out

    def render_url(self, template: str) -> str:
        return template.format(
            book=self.book.replace(" ", "+"),
            passage=self.passage,
        )


def parse_citation(s: str) -> Citation | None:
    """Parse a single citation string. Returns None if unparseable."""
    m = CITATION_RE.match(s)
    if not m:
        return None
    raw_book = re.sub(r"\s+", "", m["book"]).lower()
    book = BOOK_ALIASES.get(raw_book, m["book"].strip())
    return Citation(
        book=book,
        chapter=int(m["chapter"]),
        verse_start=int(m["verse_start"]) if m["verse_start"] else None,
        end_chapter=int(m["end_chapter"]) if m["end_chapter"] else None,
        end_verse=int(m["end_verse"]) if m["end_verse"] else None,
        raw=s.strip(),
    )


def render_reader_link(citation: Citation, reader_template: str) -> str:
    """Render a citation against a reader URL template."""
    return citation.render_url(reader_template)
