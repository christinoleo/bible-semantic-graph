"""Full ingestion: content/*.md → SQLite (nodes, edges, aliases, FTS, vectors).

Idempotent. Safe to re-run. Used as the entry point for both the CLI
(`bun run ingest`) and the watcher.
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from pathlib import Path
from typing import Iterable

import apsw
import frontmatter
import typer
from rich.console import Console
from rich.table import Table

from . import paths
from .db import init_schema, open_db, reset
from .ontology import Ontology, load_ontology
from .renderer import WikiLinkResolver, render_body
from .schema import EdgeRecord, Frontmatter, NodeRecord
from .slugify import is_valid_slug, slugify

console = Console()


class IngestError(Exception):
    pass


def collect_files(content_dir: Path) -> list[Path]:
    return sorted(p for p in content_dir.rglob("*.md") if p.is_file())


def parse_node(path: Path, content_root: Path) -> tuple[Frontmatter, str]:
    """Read a markdown file, validate frontmatter, return (frontmatter, body_md)."""
    post = frontmatter.load(path)
    try:
        fm = Frontmatter.model_validate(dict(post.metadata))
    except Exception as e:
        raise IngestError(f"{path.relative_to(content_root)}: invalid frontmatter — {e}") from e
    return fm, post.content


def build_alias_index(
    parsed: list[tuple[str, Frontmatter, str, Path]],
) -> dict[str, str]:
    """Build alias_normalized → slug, raising on collision."""
    index: dict[str, str] = {}
    collisions: dict[str, list[str]] = defaultdict(list)
    for slug, fm, _body, _path in parsed:
        # The node's name itself is implicitly an alias.
        for raw in [fm.name, *fm.aliases]:
            norm = slugify(raw)
            if not norm:
                continue
            if norm in index and index[norm] != slug:
                collisions[norm].append(slug)
                collisions[norm].append(index[norm])
            else:
                index[norm] = slug
    if collisions:
        details = "\n".join(
            f"  '{norm}' claimed by: {', '.join(sorted(set(slugs)))}"
            for norm, slugs in collisions.items()
        )
        raise IngestError(f"alias collisions:\n{details}")
    return index


def write_node(conn: apsw.Connection, record: NodeRecord, updated_at: int) -> None:
    conn.execute(
        """
        INSERT INTO nodes (
          slug, type, also_json, name, aliases_json, tags_json,
          sources_json, canon_json, argumentation_json,
          body_md, body_html, file_path, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record.slug,
            record.type,
            json.dumps(record.also),
            record.name,
            json.dumps(record.aliases),
            json.dumps(record.tags),
            json.dumps(record.sources),
            json.dumps(record.canon),
            (
                json.dumps(record.argumentation.model_dump())
                if record.argumentation
                else None
            ),
            record.body_md,
            record.body_html,
            record.file_path,
            updated_at,
        ),
    )
    conn.execute(
        "INSERT INTO nodes_fts (slug, name, aliases, body, tags) VALUES (?, ?, ?, ?, ?)",
        (
            record.slug,
            record.name,
            " ".join(record.aliases),
            record.body_md,
            " ".join(record.tags),
        ),
    )
    for raw in [record.name, *record.aliases]:
        norm = slugify(raw)
        if not norm:
            continue
        conn.execute(
            "INSERT OR IGNORE INTO aliases (alias_normalized, alias_raw, slug) VALUES (?, ?, ?)",
            (norm, raw, record.slug),
        )


def write_edges(conn: apsw.Connection, edges: Iterable[EdgeRecord]) -> None:
    for e in edges:
        conn.execute(
            """
            INSERT OR IGNORE INTO edges (source, type, target, note, primary_flag, origin)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (e.source, e.type, e.target, e.note, 1 if e.primary else 0, e.origin),
        )


def materialize_edges(
    declared_edges: list[EdgeRecord],
    wikilink_mentions: dict[str, list[str]],
    concerns_decls: dict[str, list[str]],
    ontology: Ontology,
) -> list[EdgeRecord]:
    """Add wikilink-derived `mentions` edges, concerns edges, and inferred
    reciprocity."""
    out: list[EdgeRecord] = list(declared_edges)
    for source_slug, targets in wikilink_mentions.items():
        for t in targets:
            out.append(
                EdgeRecord(source=source_slug, type="mentions", target=t, origin="wikilink")
            )
    for source_slug, targets in concerns_decls.items():
        for t in targets:
            out.append(
                EdgeRecord(source=source_slug, type="concerns", target=t, origin="frontmatter")
            )
    # Reciprocity
    inferred: list[EdgeRecord] = []
    for e in out:
        inv = ontology.inverse_of(e.type)
        if inv is None:
            continue
        if inv == e.type and e.source == e.target:
            continue
        inferred.append(
            EdgeRecord(source=e.target, type=inv, target=e.source, note=e.note, origin="inferred")
        )
    out.extend(inferred)
    return out


def embed_nodes(records: list[NodeRecord]) -> list[tuple[str, list[float]]]:
    """Encode Note bodies into vectors. Lazy-imports torch/transformers."""
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(paths.EMBEDDING_MODEL, device=paths.EMBEDDING_DEVICE)
    texts = [
        f"{r.name}\n{' '.join(r.aliases)}\n{r.body_md}".strip()
        for r in records
    ]
    if not texts:
        return []
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return list(zip([r.slug for r in records], (v.tolist() for v in vectors)))


def write_vectors(conn: apsw.Connection, embeddings: list[tuple[str, list[float]]]) -> None:
    import struct

    for slug, vec in embeddings:
        if len(vec) != paths.EMBEDDING_DIM:
            raise IngestError(
                f"embedding dim mismatch for {slug}: got {len(vec)}, expected {paths.EMBEDDING_DIM}"
            )
        conn.execute(
            "INSERT INTO nodes_vec (slug, embedding) VALUES (?, ?)",
            (slug, struct.pack(f"{paths.EMBEDDING_DIM}f", *vec)),
        )


def ingest_all(
    content_dir: Path = paths.CONTENT_DIR,
    db_path: Path = paths.DB_PATH,
    ontology_path: Path = paths.ONTOLOGY_PATH,
    skip_embeddings: bool = False,
    dry_run: bool = False,
    strict: bool = False,
) -> dict[str, int]:
    """Run a full ingest. Returns counts for reporting.

    Args:
        dry_run: validate everything, but write nothing — no SQLite touch,
            no ontology mutation, no embeddings.
        strict: treat unresolved wiki-links / unresolved edge targets as
            errors instead of warnings. Use in CI / pre-commit to catch
            breakage before it gets in.
    """
    started = time.time()
    ontology = load_ontology(ontology_path)
    files = collect_files(content_dir)
    if not files:
        console.print(f"[yellow]No .md files found in {content_dir}[/yellow]")
        return {"nodes": 0, "edges": 0}

    # Pass 1: parse + validate frontmatter, collect slugs.
    parsed: list[tuple[str, Frontmatter, str, Path]] = []
    seen_slugs: dict[str, Path] = {}
    for path in files:
        slug = path.stem
        if not is_valid_slug(slug):
            raise IngestError(f"{path.relative_to(content_dir)}: invalid slug '{slug}'")
        if slug in seen_slugs:
            raise IngestError(
                f"slug collision: '{slug}' in {path} and {seen_slugs[slug]}"
            )
        seen_slugs[slug] = path
        fm, body = parse_node(path, content_dir)
        ontology.see_node_type(fm.type)
        for t in fm.also:
            ontology.see_node_type(t)
        for e in fm.edges:
            ontology.see_edge_type(e.type)
        if fm.argumentation:
            for axis in ("stance", "tradition", "method", "subject"):
                for v in getattr(fm.argumentation, axis):
                    ontology.see_axis_value(axis, v)
        parsed.append((slug, fm, body, path))

    slugs = set(seen_slugs.keys())
    alias_index = build_alias_index(parsed)
    resolver = WikiLinkResolver(slugs=slugs, alias_norm_to_slug=alias_index)

    # Pass 2: render bodies, collect edges.
    records: list[NodeRecord] = []
    declared_edges: list[EdgeRecord] = []
    wikilink_mentions: dict[str, list[str]] = {}
    concerns_decls: dict[str, list[str]] = {}
    unresolved: list[tuple[str, str]] = []

    for slug, fm, body, path in parsed:
        unresolved_in_node: list[str] = []
        html, mentioned = render_body(
            body, resolver, on_unresolved=lambda raw: unresolved_in_node.append(raw)
        )
        for raw in unresolved_in_node:
            unresolved.append((slug, raw))
        wikilink_mentions[slug] = mentioned
        rec = NodeRecord(
            slug=slug,
            type=fm.type,
            also=fm.also,
            name=fm.name,
            aliases=fm.aliases,
            tags=fm.tags,
            sources=fm.sources,
            canon=fm.canon,
            argumentation=fm.argumentation,
            body_md=body,
            body_html=html,
            file_path=str(path.relative_to(paths.PROJECT_ROOT)),
        )
        records.append(rec)
        for e in fm.edges:
            target = slugify(e.target)
            if target not in slugs:
                unresolved.append((slug, f"edge target '{e.target}'"))
            declared_edges.append(
                EdgeRecord(
                    source=slug, type=e.type, target=target, note=e.note,
                    primary=e.primary, origin="frontmatter",
                )
            )
        if fm.concerns:
            normalized = []
            for c in fm.concerns:
                t = slugify(c)
                if t not in slugs:
                    unresolved.append((slug, f"concerns target '{c}'"))
                normalized.append(t)
            concerns_decls[slug] = normalized

    all_edges = materialize_edges(declared_edges, wikilink_mentions, concerns_decls, ontology)

    # Strict-mode failures: ONLY the things that genuinely break the model.
    # Already raised earlier in this function:
    #   - file/slug collisions  (raise during pass 1)
    #   - alias collisions      (raise from build_alias_index)
    #   - invalid frontmatter   (raise from parse_node)
    # Intentionally NOT strict-failures (just warnings reported below):
    #   - unresolved [[wiki-links]] / edge targets — these are forward
    #     references to Nodes the author hasn't written yet. The graph
    #     remains valid; the UI renders them as hover-able placeholders.
    #   - new node/edge types — auto-registered as `status: seen` in
    #     ontology.yaml; the author promotes to canonical at leisure.

    if dry_run:
        if unresolved:
            table = Table(title="Unresolved references (warnings)", show_lines=False)
            table.add_column("Node")
            table.add_column("Target")
            for source, raw in unresolved[:30]:
                table.add_row(source, raw)
            console.print(table)
        duration = time.time() - started
        console.print(
            f"[green]✓ validate[/green] {len(records)} nodes, {len(all_edges)} edges, "
            f"{len(alias_index)} aliases, {len(unresolved)} unresolved "
            f"in {duration:.2f}s (no DB written)"
        )
        return {
            "nodes": len(records),
            "edges": len(all_edges),
            "unresolved": len(unresolved),
        }

    # Pass 3: write to SQLite.
    conn = open_db(db_path)
    init_schema(conn, paths.EMBEDDING_DIM)
    reset(conn)
    with conn:
        now = int(time.time())
        for rec in records:
            write_node(conn, rec, now)
        write_edges(conn, all_edges)
        conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
                     ("last_ingest_at", str(now)))
        conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
                     ("embedding_model", paths.EMBEDDING_MODEL))

    if not skip_embeddings:
        console.print(f"[dim]Encoding {len(records)} nodes…[/dim]")
        embeddings = embed_nodes(records)
        with conn:
            write_vectors(conn, embeddings)

    ontology.save_if_dirty()

    if unresolved:
        table = Table(title="Unresolved references (warnings)", show_lines=False)
        table.add_column("Node")
        table.add_column("Target")
        for source, raw in unresolved[:30]:
            table.add_row(source, raw)
        if len(unresolved) > 30:
            table.caption = f"… and {len(unresolved) - 30} more"
        console.print(table)

    duration = time.time() - started
    console.print(
        f"[green]✓[/green] {len(records)} nodes, {len(all_edges)} edges, "
        f"{len(alias_index)} aliases in {duration:.2f}s"
    )
    return {"nodes": len(records), "edges": len(all_edges)}


app = typer.Typer(add_completion=False, no_args_is_help=False)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    skip_embeddings: bool = typer.Option(False, "--skip-embeddings"),
    dry_run: bool = typer.Option(False, "--dry-run", help="validate without writing the DB"),
    strict: bool = typer.Option(
        False,
        "--strict",
        help="fail on unresolved references or new ontology entries",
    ),
) -> None:
    """Re-ingest the entire content/ tree into .db/index.sqlite."""
    if ctx.invoked_subcommand is not None:
        return
    try:
        ingest_all(skip_embeddings=skip_embeddings, dry_run=dry_run, strict=strict)
    except IngestError as e:
        console.print(f"[red]✗ failed:[/red] {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
