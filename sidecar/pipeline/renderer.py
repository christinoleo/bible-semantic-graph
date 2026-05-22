"""Markdown rendering with wiki-link + citation expansion.

The renderer:
  1. Replaces `[[slug-or-name]]` with a link to the resolved Node's URL,
     or marks it as unresolved (rendered as a span the UI can highlight).
  2. Replaces `{{ref:Gen 22:1-19}}` (or bare `Gen 22:1-19` inside `sources:`)
     with a link to the configured external reader.
  3. Renders the rest as HTML via mistune.

Wiki-link resolution: the caller passes a slug → name map AND an
alias_normalized → slug map. The renderer's `WikiLinkResolver` looks both up.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

import mistune

from .slugify import slugify

WIKILINK_RE = re.compile(r"\[\[([^\]]+?)\]\]")


@dataclass
class WikiLinkHit:
    target_slug: str
    display: str


class WikiLinkResolver:
    """Resolves `[[X]]` to a slug using filename-first, then alias-normalized lookup."""

    def __init__(
        self,
        slugs: set[str],
        alias_norm_to_slug: dict[str, str],
    ) -> None:
        self.slugs = slugs
        self.aliases = alias_norm_to_slug

    def resolve(self, raw: str) -> WikiLinkHit | None:
        # Support [[slug|Display Text]]
        if "|" in raw:
            target_part, display = raw.split("|", 1)
        else:
            target_part, display = raw, raw
        normalized = slugify(target_part)
        if not normalized:
            return None
        if normalized in self.slugs:
            return WikiLinkHit(target_slug=normalized, display=display.strip())
        if normalized in self.aliases:
            return WikiLinkHit(target_slug=self.aliases[normalized], display=display.strip())
        return None


def render_body(
    md: str,
    resolver: WikiLinkResolver,
    on_unresolved: Callable[[str], None] | None = None,
) -> tuple[str, list[str]]:
    """Render markdown body to HTML, expanding `[[wiki-links]]`.

    Returns (html, list of resolved target slugs — for materializing mentions edges).
    """
    mentioned: list[str] = []

    def replace_wikilink(match: re.Match[str]) -> str:
        raw = match.group(1).strip()
        hit = resolver.resolve(raw)
        if hit is None:
            if on_unresolved:
                on_unresolved(raw)
            return f'<span class="wikilink-unresolved" data-target="{raw}">{raw}</span>'
        mentioned.append(hit.target_slug)
        return f'<a class="wikilink" href="/n/{hit.target_slug}">{hit.display}</a>'

    expanded = WIKILINK_RE.sub(replace_wikilink, md)
    html = mistune.html(expanded)
    return html, mentioned
