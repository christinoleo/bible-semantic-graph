# Edge expression in markdown

Edges are expressed two ways, merged by the pipeline:

1. **Frontmatter** — typed, structural edges: `edges: [{type, target, note?}]`.
2. **Inline wiki-links** — `[[slug]]` in the note body becomes a `mentions` edge automatically.

Reciprocity is **inferred by the pipeline**, never duplicated across files: declaring `father_of: isaac` in `abraham.md` causes the index to generate `son_of: abraham` on isaac. Inverse pairs (including symmetric ones like `parallels_with`, `contradicts`) live in `ontology.yaml`.

Edge types are **free-form strings**, but the pipeline emits a warning on the first use of each type and auto-maintains `ontology.yaml`, preventing typos from silently becoming new types.

## Why

- Frontmatter for structured types + inline wiki-links for natural mentions covers both uses without forcing formalism into the prose.
- Inferred reciprocity eliminates double-writing and the chronic risk of drift.
- Free types with warnings let the ontology grow organically without blocking the author; the minimal friction of the warning prevents silent typos.

## Consequences

- `ontology.yaml` becomes a maintained artifact: the canonical list of types, inverse pairs, and symmetry flags. Editing it is part of the workflow when a new type is introduced.
- The derived graph contains more edges than the files literally express (inferred reciprocity + implicit `mentions`). The canonical source remains the markdown; the index is always regenerable.
