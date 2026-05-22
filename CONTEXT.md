# Bible Semantic Graph

A personal knowledge-graph CMS centered on the Bible. Connects biblical characters, events, places, texts, theological concepts, arguments, theories, and parallels with adjacent mythology and culture. The graph is the product; pages are notes attached to each node.

## Language

**Node**:
Anything nameable that warrants its own connections in the graph. Carries a `type` (Person, Event, Place, Text, Concept, Argument, Theory, Mythological, etc.) as a property, not as a constraint on what may exist. Arguments and theories are first-class Nodes, not separate pages that reference Nodes.
_Avoid_: Entity, Page, Item

**Note**:
The textual content (markdown) attached to a Node. Each Node has zero or one Note. A Note does not exist without its Node — the Node is the unit of identity.
_Avoid_: Page, Article, Content

**Edge**:
A directed relation between two Nodes, with a type (`mentions`, `occurs_at`, `contradicts`, `parallels_with`, `fulfills`, `descendant_of`, etc.) and optionally a short justifying note.
_Avoid_: Link, Relation (ambiguous), Connection

**Slug**:
The kebab-case ASCII filename of a Node (without the `.md` extension). Serves as the Node's global ID. Diacritics and non-Latin scripts live in `name` and `aliases`, never in the slug.
_Avoid_: ID, Path, Name

**Ontology**:
The evolving registry (`ontology.yaml`) of known Node types and Edge types, plus inverse pairs and symmetry flags. Auto-maintained by the pipeline; the author edits it when promoting a new type from "seen" to "canonical".
_Avoid_: Schema, Taxonomy

## Relationships

- A **Node** has zero or one **Note**
- A **Node** may have many **Edges** entering or leaving
- An **Edge** connects exactly two **Nodes** and carries a type
- An **Edge** type may have an inverse type registered in the **Ontology**

## Flagged ambiguities

- "Page" was used early on as if it were separate from the Node — resolved: textual content is a **Note** attached to a **Node**, not an independent entity.
- "ID" and "Slug" are the same thing: the filename of the Node's markdown file. There is no separate `id:` field in frontmatter.
