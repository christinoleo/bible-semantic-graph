import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { parse as parseYaml } from 'yaml';
import type { CitationLink, NoteSegment } from '$lib/types';

const ONTOLOGY_PATH = join(process.cwd(), '..', 'ontology.yaml');

interface ReaderConfig {
	label: string;
	url: string;
}

interface SourceReaders {
	default: string;
	readers: Record<string, ReaderConfig>;
}

let _readers: SourceReaders | null = null;

function loadReaders(): SourceReaders {
	if (_readers) return _readers;
	const raw = parseYaml(readFileSync(ONTOLOGY_PATH, 'utf-8')) as {
		source_readers: SourceReaders;
	};
	_readers = raw.source_readers;
	return _readers;
}

const BOOK_ALIASES: Record<string, string> = {
	gen: 'Genesis',
	ex: 'Exodus',
	exod: 'Exodus',
	lev: 'Leviticus',
	num: 'Numbers',
	deut: 'Deuteronomy',
	josh: 'Joshua',
	judg: 'Judges',
	'1sam': '1 Samuel',
	'2sam': '2 Samuel',
	'1kgs': '1 Kings',
	'2kgs': '2 Kings',
	ps: 'Psalms',
	psa: 'Psalms',
	prov: 'Proverbs',
	eccl: 'Ecclesiastes',
	isa: 'Isaiah',
	jer: 'Jeremiah',
	ezek: 'Ezekiel',
	dan: 'Daniel',
	matt: 'Matthew',
	mt: 'Matthew',
	mk: 'Mark',
	lk: 'Luke',
	jn: 'John',
	acts: 'Acts',
	rom: 'Romans',
	'1cor': '1 Corinthians',
	'2cor': '2 Corinthians',
	gal: 'Galatians',
	eph: 'Ephesians',
	phil: 'Philippians',
	col: 'Colossians',
	heb: 'Hebrews',
	jas: 'James',
	'1pet': '1 Peter',
	'2pet': '2 Peter',
	rev: 'Revelation',
	'2chr': '2 Chronicles',
	'1chr': '1 Chronicles'
};

const QURAN_BOOK_KEYS = new Set(['q', 'quran', 'sura', 'surah']);

// Lowercased keys for ALL recognised scripture book tokens — used by
// extractCitations to filter false positives ("Father 12:34" should NOT match).
const KNOWN_BOOK_KEYS: Set<string> = new Set([
	...Object.keys(BOOK_ALIASES),
	...Object.values(BOOK_ALIASES).map((v) => v.replace(/\s+/g, '').toLowerCase()),
	...QURAN_BOOK_KEYS
]);

// Handles: "Gen 22", "Gen 21-26", "Gen 22:1", "Gen 22:1-19", "Gen 11:26-25:11"
const CITATION_RE =
	/^\s*((?:\d\s*)?[A-Za-z]+)\s*(\d+)(?::(\d+))?(?:-(?:(\d+):)?(\d+))?\s*$/;

function expandQuranCitation(
	raw: string,
	chapter: string,
	vs: string | undefined,
	endCh: string | undefined,
	endV: string | undefined
): CitationLink {
	// quran.com URL shape: /<chapter>/<verse> or /<chapter>/<verse>-<endVerse>
	// Cross-chapter ranges aren't representable — fall back to the start chapter.
	let path = chapter;
	if (vs) {
		path = `${chapter}/${vs}`;
		if (endV && (!endCh || endCh === chapter)) path += `-${endV}`;
	}
	return {
		raw,
		url: `https://quran.com/${path}`,
		reader_label: 'Quran.com'
	};
}

export function expandCitation(raw: string): CitationLink {
	const m = raw.match(CITATION_RE);
	if (!m) return { raw, url: null, reader_label: null };

	const [, bookRaw, chapter, vs, endCh, endV] = m;
	const bookKey = bookRaw.replace(/\s+/g, '').toLowerCase();

	if (QURAN_BOOK_KEYS.has(bookKey)) {
		return expandQuranCitation(raw, chapter, vs, endCh, endV);
	}

	const book = BOOK_ALIASES[bookKey] ?? bookRaw.trim();

	// Build the passage portion: BibleGateway accepts everything from
	// "22" to "22:1-19" to "11:26-25:11" to "21-26" verbatim.
	let passage = chapter;
	if (vs) passage += `:${vs}`;
	if (endV) {
		if (endCh) passage += `-${endCh}:${endV}`;
		else if (vs) passage += `-${endV}`;
		else passage += `-${endV}`; // chapter range like "21-26"
	}

	const readers = loadReaders();
	const reader = readers.readers[readers.default];
	if (!reader) return { raw, url: null, reader_label: null };

	const url = reader.url
		.replaceAll('{book}', book.replace(/\s+/g, '+'))
		.replaceAll('{passage}', passage);

	return { raw, url, reader_label: reader.label };
}

// Scans free text (e.g., an edge note) and splits it into segments — plain
// text and clickable scripture refs — so each ref can be rendered as a link
// in place, with no badge duplication. Handles comma-continued forms like
// "Matt 26:39, 42" (each verse gets its own anchor) and "John 10:30, 17:5"
// (cross-chapter continuation). Only emits refs whose book token is in
// KNOWN_BOOK_KEYS, so prose like "Father 12:34" is left as plain text.
const HEAD_RE = /\b((?:\d\s*)?[A-Za-z]{1,12})\s+(\d+):(\d+(?:[-–]\d+)?)/g;
const CONT_RE = /^(\s*,\s*)(?:(\d+):)?(\d+(?:[-–]\d+)?)/;

interface RefMatch {
	start: number;
	end: number;
	link: CitationLink;
}

export function segmentNote(text: string): NoteSegment[] {
	if (!text) return [];
	const matches: RefMatch[] = [];
	HEAD_RE.lastIndex = 0;
	let m: RegExpExecArray | null;
	while ((m = HEAD_RE.exec(text)) !== null) {
		const book = m[1].trim();
		const bookKey = book.replace(/\s+/g, '').toLowerCase();
		if (!KNOWN_BOOK_KEYS.has(bookKey)) continue;

		const headStart = m.index;
		const headEnd = HEAD_RE.lastIndex;
		let chapter = m[2];
		const headRaw = `${book} ${chapter}:${m[3]}`;
		const headLink = expandCitation(headRaw);
		if (!headLink.url) continue;
		matches.push({ start: headStart, end: headEnd, link: headLink });

		// Walk continuations: ", 42" (same chapter) or ", 17:5" (new chapter).
		// Each continuation's verse-ref span (excluding the leading ", ")
		// becomes its own clickable anchor.
		let pos = headEnd;
		while (true) {
			const cm = text.slice(pos).match(CONT_RE);
			if (!cm) break;
			const sep = cm[1];
			const refStart = pos + sep.length;
			const refEnd = pos + cm[0].length;
			if (cm[2]) chapter = cm[2];
			const contRaw = `${book} ${chapter}:${cm[3]}`;
			const contLink = expandCitation(contRaw);
			if (contLink.url) {
				matches.push({ start: refStart, end: refEnd, link: contLink });
			}
			pos += cm[0].length;
		}
		HEAD_RE.lastIndex = pos;
	}

	const segments: NoteSegment[] = [];
	let cursor = 0;
	for (const r of matches) {
		if (r.start > cursor) {
			segments.push({ kind: 'text', text: text.slice(cursor, r.start) });
		}
		segments.push({ kind: 'ref', text: text.slice(r.start, r.end), ref: r.link });
		cursor = r.end;
	}
	if (cursor < text.length) {
		segments.push({ kind: 'text', text: text.slice(cursor) });
	}
	return segments;
}
