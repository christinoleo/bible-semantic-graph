---
name: youtube-to-graph
description: Given a YouTube URL, drive Chrome to Gemini, request a thorough transcription of everything said and done in the video, then propose new Nodes and Edges to add to the Bible Semantic Graph based on the transcript. Use when the user provides a YouTube link and asks to extract knowledge into the graph.
allowed-tools: mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__new_page, mcp__chrome-devtools__list_pages, mcp__chrome-devtools__select_page, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__click, mcp__chrome-devtools__fill, mcp__chrome-devtools__type_text, mcp__chrome-devtools__wait_for, mcp__chrome-devtools__evaluate_script, mcp__chrome-devtools__press_key, Read, Write, Edit, Bash, Glob, Grep
---

# YouTube → Graph

Take a YouTube URL, get a transcript from Gemini, and propose Nodes/Edges for the Bible Semantic Graph.

## Workflow

### 1. Get the transcript from Gemini

Use the Chrome DevTools MCP. If Brave/Chrome isn't running, ask the user to launch it (do not start it yourself — they may have other sessions open).

1. `list_pages` — see if a Gemini tab is already open.
2. If not, `new_page` to `https://gemini.google.com/app`.
3. `take_snapshot` to find the prompt input element.
4. `fill` the input with the prompt below (substituting the URL).
5. `click` the send button (or `press_key` Enter).
6. Poll for completion. **Do NOT use `wait_for` with "Send message"** — that's an `aria-label`, not visible text, and will always time out. Instead, `evaluate_script` checking for the absence of `button[aria-label="Stop response"]`:
   ```js
   () => ({ done: !document.querySelector('button[aria-label="Stop response"]') })
   ```
   Poll every few seconds (or use `wait_for` with text Gemini actually renders, like the closing punctuation of the prompt context).
7. Extract the response text via `evaluate_script` reading `div.markdown.markdown-main-panel` (or the latest `message-content` element). Use `.innerText`.

**Prompt to send to Gemini (verbatim):**

```
Please provide a thorough, timestamped transcription of everything said and done in this YouTube video. Include:

- Spoken content from every speaker, with speaker labels when distinguishable.
- Onscreen text, captions, slides, and any visual citations (book references, manuscript shots, dates).
- A short note on visual context only when it carries meaning (e.g., "shows a manuscript page of P52", "displays Greek text of John 1:1").
- Cited Bible verses, Quran references, council documents, and named scholars.

Be exhaustive — I will use this to build a knowledge graph, so do not summarize or skip "obvious" content. Preserve names exactly, including diacritics.

Video: {YOUTUBE_URL}
```

If Gemini refuses (rate limit, video unavailable, etc.), report back to the user and stop. Do not fabricate a transcript.

### 2. Save the raw transcript

Save the Gemini output to `.cache/transcripts/{video-slug}.md` (create the directory if needed, and add it to `.gitignore` if not already). The slug is the YouTube video ID — `dQw4w9WgXcQ` for `https://www.youtube.com/watch?v=dQw4w9WgXcQ`.

Include a small header:

```markdown
---
source: {YOUTUBE_URL}
fetched: {YYYY-MM-DD}
---

{transcript body}
```

### 3. Write Nodes and Edges directly

Read the transcript and **write the new/updated Nodes and Edges to `content/` directly** — no approval gate. Report what you did at the end. The user can revert/edit afterward; they want the loop fast.

**Hard rules to follow when drafting (from `CLAUDE.md`):**

- All file content in English. Foreign names/quoted source material preserve their original script and live in `aliases:` or quotes only.
- Body length caps:
  - `Argument`: 1–3 sentences.
  - `Concept`/`Theory`/`Event`: 1 short paragraph.
  - `Person`/`Place`/`Text`/`Manuscript`/`Council`/`Deity`: 1–2 short paragraphs.
- No section headings, intros, conclusions, or numbered evidence lists inside the body. Decompose into sub-Nodes + edges.
- Every named entity in the body → `[[wiki-link]]`.
- If `type: Argument`, include a complete `argumentation:` block (all 4 axes non-empty). Reuse canonical values from `ontology.yaml`. Don't invent synonyms.
- Pick deepening edges (`case_of`, `invokes`, `presupposes`, `specializes`, `instance_of`, `builds_on`) deliberately; mark at most one as `primary: true`.
- For relational Nodes (contains "vs", "controversy", "between X and Y"), set `concerns: [a, b, ...]`.
- If a Christian/Islamic-style partisan reading appears, follow the fractal pattern: a neutral `Concept` Node + two `has_case` `Argument` Nodes (Christian reading / Islamic reading), linked `responds_to` or `contradicts`.
- Check `ontology.yaml` for the canonical edge/argumentation values before introducing anything new.
- Check existing Nodes before proposing duplicates — use `Glob` on `content/**/*.md` and `Grep` for the proposed name and likely aliases.
- **Always attach `videos:`** in the frontmatter of every new Argument (and every Concept whose substance comes from a specific video) — the front-end renders them as YouTube chips. Shape:
  ```yaml
  videos:
    - { url: "https://youtu.be/{video-id}", title: "{exact YouTube title}", timestamp: "12:34" }
  ```
  - `timestamp` is **optional but strongly preferred**: when the transcript contains an obvious moment where the claim is made (a quote, an exchange), pick the `[MM:SS]` from that line and pass it through verbatim (`"12:34"`). The UI converts to seconds for YouTube's `?t=` param at render time, so any of `M:SS`, `MM:SS`, `H:MM:SS`, or raw seconds work.
  - Multiple `videos:` entries are fine if the claim is illustrated by more than one source.

### 4. Write the files

- New Node files go to the correct directory under `content/` matched to type: `content/people/`, `content/concepts/`, `content/events/`, `content/places/`, `content/texts/`, `content/manuscripts/`, `content/councils/`, `content/traditions/`, `content/mythological/`. Create a new directory only if the type truly has no home.
- Edge additions on existing Nodes via `Edit` on their frontmatter.
- Do not run the ingest pipeline; the user will. Report a concise summary at the end: new files created, existing files edited, edges added.

## Notes

- If the video is mostly secular and produces no Bible-graph-relevant Nodes, say so honestly. Don't pad the proposal.
- Long videos may need the transcript chunked. If Gemini truncates, ask it to continue in the same chat — don't re-paste the URL.
- Timestamps in the transcript are valuable; cite them in the `note:` field of edges when the claim is a paraphrase of a specific moment.
