# Bible Semantic Graph — Project Instructions

## Language

**All files in this repository MUST be written in English.** This includes:

- Content files (markdown notes for Nodes — names, aliases, bodies, frontmatter)
- Documentation (`CONTEXT.md`, ADRs in `docs/adr/`, READMEs, comments)
- Code (variable names, function names, comments, log messages)
- Commit messages, issue descriptions, PR descriptions

The repository is public-facing. Content must be accessible to a global audience. The only exception is non-English names, transliterations, and quoted source material inside `aliases:` arrays or body text — those preserve their original script and diacritics (e.g., `אַבְרָהָם`, `Ašerah`, `Yēšūaʿ`).

Conversation with the user happens in Portuguese — that's fine. The moment a file is written, it switches to English.

## Writing style for Node content — **the body is a label, the graph is the substance**

The bodies of `content/*.md` Nodes are **tiny labels in a graph of millions**, not blog posts, not encyclopedia entries, not essays. The graph's value comes from the **connections** between Nodes — edges, sub-claims, counter-arguments, deepening chains — not from prose embedded in any one Node.

**The strict rule:**

- **Body length cap by type:**
  - `Argument`: **1–3 sentences**. State the claim and (if structural) the key presupposition. That is it. Sub-claims, evidence, refutations, counter-readings, sources — **all live as edges to other Nodes**, NEVER as paragraphs of supporting text.
  - `Concept`, `Theory`, `Event`: **1 short paragraph** (~3–5 sentences). Define the thing; defer everything else to edges.
  - `Person`, `Place`, `Text`, `Manuscript`, `Council`, `Deity`: **1–2 short paragraphs**. Identify; orient; do NOT narrate.
- **If you find yourself writing a numbered list of points inside the body, STOP.** Each numbered point is supposed to be a separate Node, linked by edges. Decompose immediately.
- **If you find yourself writing "supporting evidence:", "tensions:", "where it's weakest:", "modern deployment:" — STOP.** Those are entire sub-Nodes, not paragraphs. Make them Nodes. Add edges.
- **Million-tiny-Nodes is the target, not few-fat-Nodes.** A graph with 5,000 leaf-Nodes of 3 sentences each is more navigable than 500 Nodes of 30 sentences each.
- **Heavily linked** is still the rule — `[[wiki-links]]` for every named entity, concept, or contested claim. Forward references are fine.
- **No section headings inside the body.** Sections imply sub-topics, sub-topics are Nodes.
- **No intros, no conclusions, no TL;DRs.** The Node IS the label.

**Render order matters.** The UI shows the graph connections (deepening, cases, counter-arguments, related) BEFORE the body, by design. Don't try to compensate for that in the body — let the graph carry the structure.

**When in doubt, ask the user** whether something is "graph-side" or "body-side." Default to graph-side.

This applies to **content/*.md only** — code comments, READMEs, and ADRs follow their own conventions.

## Shaping navigation through edge choice

Every Node author is also a **navigation author**. The edges you pick aren't decoration — they directly decide how a reader moves through the graph. The Node page renders edges in **distinct reading sections**, and the section is chosen entirely by edge type. Pick types deliberately.

### The three reading dimensions

1. **Deepening (vertical, downward into the substrate).** Edges meaning "this engages a more fundamental question." Renders under **"Goes deeper into"**.
   - `case_of` — A is a specific instance of the more general B. (`pelagian-controversy` `case_of` `grace-vs-free-will-debate`.)
   - `invokes` — A engages B as a deeper principle. (`jesus-was-muslim-argument` `invokes` `biblical-inerrancy`.)
   - `presupposes` — A takes B for granted. (`historical-jesus-quest` `presupposes` `gospels-as-historical-sources`.)
   - `specializes` — A is a narrower form of B. (`reformed-covenant-theology` `specializes` `covenant-theology`.)
   - `instance_of` — formal taxonomic membership.
   - `builds_on` — A explicitly extends B's earlier work / argument.

2. **Cases (vertical, upward into specifics).** The inverse direction — populated automatically by the pipeline from inbound edges of the above. Renders under **"Specific cases"**. You usually don't write these; they accumulate as you author more specific Nodes pointing back.

3. **Lateral (sideways, peer-to-peer).** Edges between Nodes at similar level of abstraction. Renders under **"Related"**.
   - `parallels_with` (symmetric) — structural / thematic kinship.
   - `contradicts` (symmetric) — tension.
   - `refutes` — directional disagreement.
   - `related_to` (symmetric) — generic catch-all; use only when nothing more specific fits.
   - All other non-deepening edges (genealogy, geography, narrative — `father_of`, `lived_in`, `occurs_at`, etc.) also render here.

### Marking the primary deepening line

When a Node has multiple deepening edges, **mark the one most-recommended next step** with `primary: true`:

```yaml
edges:
  - { type: case_of, target: grace-vs-free-will-debate, primary: true }
  - { type: invokes, target: original-sin }
  - { type: presupposes, target: divine-foreknowledge }
```

The UI puts the primary one first and badges it with ★. Use this sparingly — at most one per Node. It tells a reader "if you're going to deepen one way from here, go this way."

### Relational Nodes — `concerns:`

Some Nodes don't exist on their own — they exist *because of* two or more other Nodes. The Pelagian Controversy isn't a thing without Augustine AND Pelagius. The Synoptic Problem isn't a thing without Matthew, Mark, and Luke. For these, declare the relata in `concerns:`:

```yaml
type: Event           # or Argument / Theory / Concept
name: Pelagian Controversy
concerns: [augustine-of-hippo, pelagius]
```

The UI renders these prominently as **"Between Augustine and Pelagius"** at the top of the page. Each relatum also gets a **"Relations involving this"** section listing the relational Nodes that name it. Empty / omitted `concerns:` means the Node is substantial (Abraham, Genesis, Trento — they exist in themselves).

Rule of thumb: if the Node's title contains "vs", "controversy", "dispute", "tension", "synthesis between", or names two+ persons/things → it's almost certainly relational, write `concerns:`.

### Decomposing an argument into sub-claims (fractal pattern)

A substantive Argument usually rests on several discrete sub-claims, each of which is itself debatable and deserves its own treatment. Don't put the whole argument's evidence inside the parent body — break it out into structured pieces.

The pattern, illustrated for the parent Argument "Jesus Was a Muslim Prophet":

```
[Argument]  Jesus Was a Muslim Prophet  (parent, summary)
   ↑ supports         ↑ supports          ↑ supports
[Concept]  Prostration of Jesus    [Concept]  Jesus's Prayer Practice    [Concept]  Tahrif
     ├─ has_case →                      ├─ has_case →                          ...
     │   [Argument] Islamic Reading:     │   [Argument] Islamic Reading:
     │   Jesus's Prostration as Submission  Jesus Prayed to Allah
     │           ↕ contradicts                       ↕ contradicts
     └─ has_case →                      └─ has_case →
         [Argument] Christian Reading:       [Argument] Christian Reading:
         Filial Obedience to the Father      Jesus Prayed to the Father
              responds_to ↑                       responds_to ↑
              (the Islamic reading)               (the Islamic reading)
```

Three rules of decomposition:

1. **Each point of evidence is its own Node**, not a paragraph in the parent body. The parent summarizes; the children carry the substance.
2. **For contested points, each tradition gets its own Argument Node, both `has_case` of a shared Concept Node** that names the topic neutrally ("Prostration of Jesus" — not "Islamic prostration of Jesus"). The Concept is the neutral pivot; the Arguments are the partisan readings.
3. **Use `supports`** from sub-claim → parent argument (auto-infers `supported_by` on the parent). UI puts these in the "Specific cases" section of the parent — drilling down into the parent reveals its supporting structure.

### Refutes, responds_to, contradicts — when to use which

These three argumentative-opposition edges all render in the **"Counter-arguments and responses"** UI section. Choose deliberately:

- **`refutes`** (directional, strong): A claims B is wrong and offers grounds. "Multiple Attestation refutes Q4:157 Crucifixion Denial."
- **`responds_to`** (directional, measured): A answers B without claiming definitive refutation. "Patristic Trinitarianism responds_to Islamic Critique of Trinity." Useful when you want to acknowledge an opposing claim has standing but offer an alternative.
- **`contradicts`** (symmetric): the positions are logically incompatible — but neither side has explicitly engaged the other. Use when the contradiction is structural, not the result of dialogue.

When writing a Christian response to an Islamic claim (or vice versa), prefer **`responds_to`** unless you're making the stronger claim of refutation. Lean charitable; the body argues the substance.

### When to write a relational Node vs. just an edge

- **Just an edge** if the relationship is trivial (Abraham `father_of` Isaac) or expressible in one sentence.
- **A relational Node** if the relationship deserves its own body — its history, scholarly debate, primary sources, reception. Then write a Node with `concerns:` and use edges from the relata to describe the *trivial* connection, while the substantial discussion lives in the relational Node.

### Argumentation classification (required for `type: Argument`)

Every `type: Argument` Node MUST carry a structured `argumentation:` block with all four axes non-empty. The pipeline **fails** at ingest if any axis is missing. This is enforced so the corpus can be analyzed (run `bun run analyze`) without missing data.

```yaml
argumentation:
  stance:    [against-christianity, for-islam]      # for/against, multiple OK
  tradition: [islamic-apologetic]                   # intellectual lineage
  method:    [textual-critique, from-prophecy]      # how it argues
  subject:   [christology, scriptural-transmission] # what it concerns
```

Allowed values live in `ontology.yaml::argumentation_axes`. New values you introduce in a Node are auto-registered as `status: seen` — promote them to `canonical` when you've decided they belong. **Don't invent synonyms** for existing values; reuse the canonical set so analysis stays comparable.

**Axes — when in doubt:**
- **stance**: at least one. If the Argument is descriptive ("documentary hypothesis"), use `skeptical-of-religion` or `internal-christian-disagreement` etc. Most Arguments have ≥1 clear stance.
- **tradition**: the intellectual lineage that owns / advances this argument. Multiple if the argument is shared across traditions.
- **method**: the kind of reasoning. Multiple is common (most arguments use 2-3 methods).
- **subject**: what the argument is *about* doctrinally / historically. Almost always ≥1; commonly 2-3.

The `argumentation:` block applies only when `type: Argument` is the PRIMARY type. Secondary `also: [Argument]` is a hint, not a strict commitment, and is not validated.

For `type: Theory`, `Concept`, or `Event` Nodes that nonetheless have argumentative character, `argumentation:` is **allowed but optional**. Use it when meaningful; skip when descriptive.

The UI renders the argumentation block as a panel under the Node header, with each value clickable to `/axis/{axis}/{value}` — a corpus filter showing every Node sharing that classification.

### Practical checklist while writing a Node

After drafting the body, look at the frontmatter:

- [ ] Does this Node have a deeper question / underlying principle it engages? → add `case_of` / `invokes` / `presupposes`.
- [ ] Is there ONE deepening edge that's the recommended next step for a reader? → mark `primary: true`.
- [ ] Is the Node fundamentally *about the relation* between two named things? → add `concerns:`.
- [ ] Did I link liberally in the body via `[[wiki-links]]`? (Required — see "Writing style".)
- [ ] If a Text Node, is `canon:` set?
- [ ] If type is `Argument`, is `argumentation:` set with all four axes? (Pipeline-enforced — ingest fails otherwise.)

Skipping these is allowed (forward refs are warnings, not errors), but every skipped one shrinks how legible the graph becomes downstream.

## Architecture summary

See [`CONTEXT.md`](./CONTEXT.md) for the domain glossary and [`docs/adr/`](./docs/adr/) for architectural decisions. Key invariants:

- Markdown files in `content/` are the **single source of truth**. Everything else (SQLite indices, generated `graph.json`, NetworkX in-memory graphs, any future graph DB) is a derived index, rebuildable from the markdown at any time.
- Each Node is exactly one `.md` file. **Filename (kebab-case ASCII slug) IS the ID.** Type comes from frontmatter, never from directory.
- Edges are declared two ways: typed in frontmatter (`edges: [{type, target}]`) or as inline `[[wiki-links]]` in the body (inferred as `mentions`). Reciprocity is inferred by the pipeline from `ontology.yaml`, never duplicated across files.

## Tooling

- **JS/TS**: Bun (`bun install`, `bun add`, `bunx`). Never pnpm/npm/yarn.
- **Python** (pipeline): `uv` for env + dependency management.
- **Web framework**: SvelteKit with `adapter-node`, running on Bun. Use the Svelte MCP for documentation lookups and `svelte-autofixer` for component validation.
- **Runtime split**: hybrid — SvelteKit serves UI + simple SQLite queries; a Python sidecar (FastAPI / Litestar) handles ML-heavy endpoints (semantic search encoding, vector search execution, NetworkX algorithms, future LLM tool-use). Both processes share the same SQLite file. See [ADR 0009](./docs/adr/0009-hybrid-sveltekit-python-sidecar.md).
- **Database**: SQLite with the `sqlite-vec` extension. Single file at `app/.db/index.sqlite`, rebuilt from `content/*.md` by the pipeline. FTS5 for text search, sqlite-vec for embeddings. Bun accesses it via `bun:sqlite`; Python via `apsw` or `sqlite3`.
- **Embeddings**: sentence-transformers in the Python pipeline AND the Python sidecar. The exact same model is used at ingestion and at query time — version this explicitly.
