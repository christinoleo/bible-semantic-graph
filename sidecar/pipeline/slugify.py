"""Single canonical slug normalization.

Used both at ingestion (validating filenames) and at link resolution
(matching `[[Whatever Was Written]]` to an existing slug). Keep this
function the only source of truth for the rule defined in ADR 0006.
"""

import re
import unicodedata

_NON_SLUG = re.compile(r"[^a-z0-9]+")
_TRIM = re.compile(r"^-+|-+$")


def slugify(text: str) -> str:
    """NFKD-normalize, strip combining marks, lowercase, kebab-case ASCII.

    >>> slugify("Abraham")
    'abraham'
    >>> slugify("Sacrifice of Isaac")
    'sacrifice-of-isaac'
    >>> slugify("Enūma Eliš")
    'enuma-elis'
    >>> slugify("  Abrahamic   Covenant!  ")
    'abrahamic-covenant'
    >>> slugify("אַבְרָהָם")
    ''
    """
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_only = nfkd.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_only.lower()
    hyphenated = _NON_SLUG.sub("-", lowered)
    return _TRIM.sub("", hyphenated)


def is_valid_slug(slug: str) -> bool:
    """A slug is valid iff it's already in canonical form."""
    return bool(slug) and slug == slugify(slug)
