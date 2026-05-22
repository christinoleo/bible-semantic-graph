import { Database } from 'bun:sqlite';
import { existsSync, statSync } from 'node:fs';
import { join } from 'node:path';
import type {
	EdgeRow,
	EdgeWithPeer,
	NodeFull,
	NodeSummary,
	SearchHit
} from '$lib/types';

// SvelteKit cwd is `app/`, so the DB is one level up.
const DB_PATH = join(process.cwd(), '..', '.db', 'index.sqlite');

// Cache a Database connection but re-open it if the file's inode changes
// (which happens whenever the pipeline DROPs+recreates tables — or if the
// file is removed and rebuilt). This makes dev edit-and-reload work without
// having to restart SvelteKit.
let _db: Database | null = null;
let _dbMtimeMs: number | null = null;

export function db(): Database {
	if (!existsSync(DB_PATH)) {
		_db = null;
		_dbMtimeMs = null;
		throw new DBNotBuiltError();
	}
	const mtime = statSync(DB_PATH).mtimeMs;
	if (_db && _dbMtimeMs === mtime) return _db;
	if (_db) {
		try { _db.close(); } catch { /* ignore */ }
	}
	_db = new Database(DB_PATH, { readonly: true });
	_db.exec('PRAGMA journal_mode = WAL');
	_dbMtimeMs = mtime;
	return _db;
}

export class DBNotBuiltError extends Error {
	constructor() {
		super(`Index not built yet. Run: bun run ingest`);
		this.name = 'DBNotBuiltError';
	}
}

function parseSummaryRow(row: Record<string, unknown>): NodeSummary {
	return {
		slug: row.slug as string,
		type: row.type as string,
		name: row.name as string,
		tags: JSON.parse((row.tags_json as string) || '[]')
	};
}

function parseFullRow(row: Record<string, unknown>): NodeFull {
	const argRaw = row.argumentation_json as string | null;
	return {
		...parseSummaryRow(row),
		also: JSON.parse((row.also_json as string) || '[]'),
		aliases: JSON.parse((row.aliases_json as string) || '[]'),
		sources: JSON.parse((row.sources_json as string) || '[]'),
		canon: JSON.parse((row.canon_json as string) || '[]'),
		argumentation: argRaw ? JSON.parse(argRaw) : null,
		body_html: row.body_html as string
	};
}

export function getNode(slug: string): NodeFull | null {
	const row = db().query('SELECT * FROM nodes WHERE slug = ?').get(slug) as
		| Record<string, unknown>
		| null;
	return row ? parseFullRow(row) : null;
}

export function listNodes(): NodeSummary[] {
	const rows = db()
		.query('SELECT slug, type, name, tags_json FROM nodes ORDER BY name COLLATE NOCASE')
		.all() as Record<string, unknown>[];
	return rows.map(parseSummaryRow);
}

export function listNodesByType(type: string): NodeSummary[] {
	const rows = db()
		.query(
			'SELECT slug, type, name, tags_json FROM nodes WHERE type = ? ORDER BY name COLLATE NOCASE'
		)
		.all(type) as Record<string, unknown>[];
	return rows.map(parseSummaryRow);
}

export function listNodesByTag(tag: string): NodeSummary[] {
	const rows = db()
		.query(
			`SELECT slug, type, name, tags_json
       FROM nodes
       WHERE EXISTS (SELECT 1 FROM json_each(tags_json) WHERE value = ?)
       ORDER BY name COLLATE NOCASE`
		)
		.all(tag) as Record<string, unknown>[];
	return rows.map(parseSummaryRow);
}

export function listNodesByAxisValue(axis: string, value: string): NodeSummary[] {
	// argumentation_json is a JSON object like {stance:[...], tradition:[...], ...}
	// SQLite json_extract + json_each lets us filter on nested arrays.
	const rows = db()
		.query(
			`SELECT slug, type, name, tags_json
       FROM nodes
       WHERE argumentation_json IS NOT NULL
         AND EXISTS (
           SELECT 1 FROM json_each(json_extract(argumentation_json, '$.' || ?))
           WHERE value = ?
         )
       ORDER BY name COLLATE NOCASE`
		)
		.all(axis, value) as Record<string, unknown>[];
	return rows.map(parseSummaryRow);
}

export function axisValueCounts(axis: string): { value: string; count: number }[] {
	return db()
		.query(
			`SELECT json_each.value AS value, COUNT(*) AS count
       FROM nodes, json_each(json_extract(nodes.argumentation_json, '$.' || ?))
       WHERE nodes.argumentation_json IS NOT NULL
       GROUP BY value
       ORDER BY count DESC, value`
		)
		.all(axis) as { value: string; count: number }[];
}

export function typeCounts(): { type: string; count: number }[] {
	return db()
		.query(
			'SELECT type, COUNT(*) AS count FROM nodes GROUP BY type ORDER BY count DESC, type'
		)
		.all() as { type: string; count: number }[];
}

export function totalCount(): number {
	const row = db().query('SELECT COUNT(*) AS n FROM nodes').get() as { n: number };
	return row.n;
}

export function getOutboundEdges(slug: string): EdgeWithPeer[] {
	const rows = db()
		.query(
			`SELECT e.source, e.target, e.type, e.note, e.primary_flag, e.origin,
              n.slug AS peer_slug, n.type AS peer_type, n.name AS peer_name, n.tags_json AS peer_tags
       FROM edges e
       LEFT JOIN nodes n ON n.slug = e.target
       WHERE e.source = ?
       ORDER BY e.primary_flag DESC, e.type, peer_name`
		)
		.all(slug) as Record<string, unknown>[];
	return rows.map(toEdgeWithPeer);
}

export function getInboundEdges(slug: string): EdgeWithPeer[] {
	const rows = db()
		.query(
			`SELECT e.source, e.target, e.type, e.note, e.primary_flag, e.origin,
              n.slug AS peer_slug, n.type AS peer_type, n.name AS peer_name, n.tags_json AS peer_tags
       FROM edges e
       LEFT JOIN nodes n ON n.slug = e.source
       WHERE e.target = ?
       ORDER BY e.type, peer_name`
		)
		.all(slug) as Record<string, unknown>[];
	return rows.map((r) => ({ ...toEdgeWithPeer(r), source: r.source as string }));
}

function toEdgeWithPeer(row: Record<string, unknown>): EdgeWithPeer {
	const peer: NodeSummary | null = row.peer_slug
		? {
				slug: row.peer_slug as string,
				type: row.peer_type as string,
				name: row.peer_name as string,
				tags: JSON.parse((row.peer_tags as string) || '[]')
			}
		: null;
	return {
		source: row.source as string,
		target: row.target as string,
		type: row.type as string,
		note: (row.note as string) || null,
		primary: Boolean(row.primary_flag),
		origin: row.origin as EdgeRow['origin'],
		peer
	};
}

export function searchText(query: string, limit = 20): SearchHit[] {
	if (!query.trim()) return [];
	const safe = query.replace(/["]/g, '');
	const rows = db()
		.query(
			`SELECT slug, bm25(nodes_fts) AS score,
              snippet(nodes_fts, 3, '<mark>', '</mark>', '…', 16) AS snippet
       FROM nodes_fts
       WHERE nodes_fts MATCH ?
       ORDER BY score
       LIMIT ?`
		)
		.all(`${safe}*`, limit) as { slug: string; score: number; snippet: string }[];
	return rows.map((r) => ({
		slug: r.slug,
		score: -r.score,
		source: 'text' as const,
		snippet: r.snippet
	}));
}

export function nodesBySlugs(slugs: string[]): Map<string, NodeSummary> {
	if (slugs.length === 0) return new Map();
	const placeholders = slugs.map(() => '?').join(',');
	const rows = db()
		.query(
			`SELECT slug, type, name, tags_json FROM nodes WHERE slug IN (${placeholders})`
		)
		.all(...slugs) as Record<string, unknown>[];
	return new Map(rows.map((r) => [r.slug as string, parseSummaryRow(r)]));
}
