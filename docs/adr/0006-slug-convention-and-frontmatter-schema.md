# Slug convention and frontmatter schema

## Slug

Slugs are **kebab-case ASCII English**. No diacritics, no non-Latin scripts, no spaces, no uppercase: `abraham.md`, `sacrifice-of-isaac.md`, `abrahamic-covenant.md`, `enuma-elish.md`.

The pipeline normalizes a string to a slug via `NFKD → strip combining marks → lowercase → replace non-[a-z0-9] with hyphens → collapse → trim`. This normalization applies **only** to slugs — `name`, `aliases`, and body text preserve their original script and diacritics verbatim.

## Frontmatter schema

```yaml
---
type: Person                          # REQUIRED — primary type, from ontology.yaml
also: [Patriarch]                     # optional — secondary types for multi-nature Nodes
name: Abraham                         # REQUIRED — canonical display name
aliases: [Abram, Avraham, Ibrāhīm, אַבְרָהָם]   # optional — alternative names for search + wiki-link resolution
edges:                                # optional — typed structural edges
  - {type: father_of, target: isaac}
  - {type: lived_in, target: ur}
  - {type: parallels_with, target: enuma-elish, note: "creation myth"}
tags: [patriarch, genesis, covenant]  # optional — flat tag list
sources:                              # optional — primary-source citations
  - "Gen 11:26-25:11"
canon: [tanakh, protestant, catholic, # optional — for Text Nodes: which canonical traditions include this book
        orthodox-eastern, orthodox-ethiopian]
---
```

### `canon` field

Optional. Applies primarily to `type: Text` Nodes (Bible books, deuterocanonicals, pseudepigrapha). Lists the canonical traditions that recognize the text as scripture. Allowed values:

- `tanakh` — Hebrew Bible (Jewish canon, 24 books in Jewish numbering / 39 in Christian numbering)
- `protestant` — Protestant Old + New Testament (66 books)
- `catholic` — Roman Catholic (73 books: Protestant + 7 deuterocanonical)
- `orthodox-eastern` — Eastern Orthodox (Catholic + 1 Esdras, Prayer of Manasseh, Psalm 151, 3 Maccabees; 4 Maccabees as Greek appendix)
- `orthodox-ethiopian` — Ethiopian Orthodox Tewahedo (broader; includes 1 Enoch, Jubilees, Meqabyan, etc.)

A pseudepigraphal text not in any canon should have `canon: []` (or omit the field). Use the `tags` field to mark category (`deuterocanonical`, `pseudepigraphal`, `nt-apocrypha`, `church-document`).

## Validation rules

- `type` and `name` missing → **error** (build fails).
- `type` not seen before → **warning**, append to `ontology.yaml` as `status: seen`.
- Edge `type` not seen before → **warning**, append to `ontology.yaml`.
- Edge `target` slug does not match any file or alias → **warning** (allows forward references and intentional stubs).
- Wiki-link `[[X]]` resolution order: filename slug match → alias match (case- and diacritic-insensitive on normalized form) → error if ambiguous, warning if unresolved.

## Why

- **ASCII English slugs**: clean URLs, terminal-friendly, grep-friendly. Diacritics in filenames work technically but poison every tool that touches them. The display layer (`name`, `aliases`) carries the visually correct forms.
- **Multilingual aliases**: Bible studies inherently span Hebrew, Greek, Aramaic, Latin, and scholarly transliterations. Storing them in `aliases` lets `[[אֲשֵׁרָה]]` in body text resolve correctly while keeping the slug as `asherah`.
- **Minimal required fields**: only `type` and `name`. Everything else accrues organically as the Node matures.
- **Warnings over errors** for ontology drift: lets the author introduce new types fluidly while still surfacing typos.

## Consequences

- The pipeline must own slug normalization as a single canonical function, reused by both ingestion and link resolution.
- Alias collisions across Nodes (two Nodes both claiming `Abram` as an alias) → **error** at build time, force the author to disambiguate.
- `ontology.yaml` accumulates a `status: seen | canonical` field per type — author promotes to canonical when satisfied.
