"""SQLite schema + connection helper with sqlite-vec loaded."""

from __future__ import annotations

from pathlib import Path

import apsw
import sqlite_vec


SCHEMA = """
CREATE TABLE IF NOT EXISTS nodes (
  slug        TEXT PRIMARY KEY,
  type        TEXT NOT NULL,
  also_json   TEXT NOT NULL DEFAULT '[]',
  name        TEXT NOT NULL,
  aliases_json TEXT NOT NULL DEFAULT '[]',
  tags_json   TEXT NOT NULL DEFAULT '[]',
  sources_json TEXT NOT NULL DEFAULT '[]',
  canon_json  TEXT NOT NULL DEFAULT '[]',
  argumentation_json TEXT,  -- nullable JSON; NULL for non-argumentative nodes
  body_md     TEXT NOT NULL DEFAULT '',
  body_html   TEXT NOT NULL DEFAULT '',
  file_path   TEXT NOT NULL,
  updated_at  INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type);
CREATE INDEX IF NOT EXISTS idx_nodes_name ON nodes(name);

CREATE TABLE IF NOT EXISTS edges (
  source  TEXT NOT NULL,
  type    TEXT NOT NULL,
  target  TEXT NOT NULL,
  note    TEXT,
  primary_flag INTEGER NOT NULL DEFAULT 0,
  origin  TEXT NOT NULL CHECK (origin IN ('frontmatter','wikilink','inferred')),
  PRIMARY KEY (source, type, target, origin)
);

CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source);
CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target);

CREATE TABLE IF NOT EXISTS aliases (
  alias_normalized TEXT NOT NULL,
  alias_raw        TEXT NOT NULL,
  slug             TEXT NOT NULL,
  PRIMARY KEY (alias_normalized, slug)
);

CREATE INDEX IF NOT EXISTS idx_aliases_norm ON aliases(alias_normalized);

CREATE TABLE IF NOT EXISTS meta (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS nodes_fts USING fts5(
  slug UNINDEXED,
  name,
  aliases,
  body,
  tags
);
"""

# Created separately because vec0 dimension must match the encoder.
VEC_SCHEMA_TEMPLATE = """
CREATE VIRTUAL TABLE IF NOT EXISTS nodes_vec USING vec0(
  slug TEXT PRIMARY KEY,
  embedding FLOAT[{dim}]
);
"""


def open_db(path: Path, load_vec: bool = True) -> apsw.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = apsw.Connection(str(path))
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA foreign_keys = ON")
    if load_vec:
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
    return conn


def init_schema(conn: apsw.Connection, embedding_dim: int) -> None:
    """Drop and recreate regular tables. For the sqlite-vec virtual table,
    DROP+CREATE has compatibility issues across versions, so we DELETE FROM
    contents if it already exists and only CREATE on first run. This keeps
    the file inode stable across reingests so SvelteKit's open handle stays
    valid."""
    # Regular tables: drop and recreate (handles column schema migrations).
    for table in ["nodes_fts", "edges", "aliases", "nodes", "meta"]:
        conn.execute(f"DROP TABLE IF EXISTS {table}")
    conn.execute(SCHEMA)
    # Vec table: rebuild via DELETE if it exists, CREATE only if missing.
    existing = list(conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='nodes_vec'"
    ))
    if existing:
        conn.execute("DELETE FROM nodes_vec")
    else:
        conn.execute(VEC_SCHEMA_TEMPLATE.format(dim=embedding_dim))


def reset(conn: apsw.Connection) -> None:
    """No-op kept for backward call sites. init_schema() now wipes
    everything via DROP + recreate, so a separate DELETE pass is redundant."""
    pass
