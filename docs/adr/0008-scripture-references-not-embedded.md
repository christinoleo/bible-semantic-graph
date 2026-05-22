# Scripture text is referenced, never embedded

Biblical (and any external) source text is **not** stored in the repository. Nodes refer to passages via the `sources:` frontmatter field using a citation reference (e.g., `"Gen 22:1-19"`), and the renderer expands these into external links to a public Bible reader (BibleGateway, Bible Online, Sefaria for Hebrew, etc.). The same convention applies to non-biblical primary sources (Enūma Eliš, Gilgamesh, Apocrypha, Church Fathers, etc.) — cite and link out, never paste.

## Why

- The project's value is the **commentary, connections, and arguments** — not the source text, which exists in many high-quality places online.
- Embedding scripture would inflate the repo, force a translation choice (or maintain parallels), and bring licensing concerns (KJV/WEB are public domain; ESV/NIV are not).
- Keeps Nodes focused: every Node represents original thought or curated relations, not transcribed primary text.

## Consequences

- The pipeline owns a citation parser + URL templater that turns `"Gen 22:1-19"` into one or more external reader links. Adding a new reader (e.g., Sefaria for Hebrew) is a config change, not a content migration.
- `Passage` as a Node type is allowed when the author wants to attach commentary to a specific perícope (`content/passages/binding-of-isaac.md`), but the body of that Node is the **commentary**, not the verse text. The `sources:` field carries the actual citation.
- If multilingual scholarly work (interlinear, lexical analysis) becomes a goal later, that's a separate decision — this ADR doesn't preclude it, but it's not in scope now.
