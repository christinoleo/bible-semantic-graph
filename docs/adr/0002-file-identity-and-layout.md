# File identity and layout for Nodes

Each **Node** is exactly one `.md` file. The **filename** (kebab-case ASCII slug) **is** the ID — globally unique across the repository, with no redundant `id:` field in frontmatter. The **type** of the Node comes from frontmatter (`type: Person`), not from the directory; **directories are purely cosmetic** (they organize files for the human's editor navigation, the system ignores them).

## Why

- **One Node per file** — sub-nodes via anchors break on refactor; if a concept warrants its own edges, it warrants its own file.
- **Filename as ID** — a unique slug forces descriptive names (`abrahamic-covenant.md` vs `davidic-covenant.md`), avoids ambiguity, and renaming is `git mv` + a link-rewrite script. No duality of filename/ID drifting out of sync.
- **Type in frontmatter, dirs cosmetic** — some Nodes have multiple natures (Babel is a Place AND an Event). Directories force a false choice; frontmatter accepts `type: Place` + `also: [Event]`. Bonus: reorganizing folders never breaks links.

## Consequences

- Filename collision = a build-time error the pipeline catches early.
- Renaming a Node requires updating every `[[link]]` and frontmatter `target:` reference — needs a rename script.
- The author can drag files between folders freely without fear of breaking anything.
