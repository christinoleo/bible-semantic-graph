import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { parse as parseYaml } from 'yaml';
import type { CitationLink } from '$lib/types';

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

// Handles: "Gen 22", "Gen 21-26", "Gen 22:1", "Gen 22:1-19", "Gen 11:26-25:11"
const CITATION_RE =
	/^\s*((?:\d\s*)?[A-Za-z]+)\s*(\d+)(?::(\d+))?(?:-(?:(\d+):)?(\d+))?\s*$/;

export function expandCitation(raw: string): CitationLink {
	const m = raw.match(CITATION_RE);
	if (!m) return { raw, url: null, reader_label: null };

	const [, bookRaw, chapter, vs, endCh, endV] = m;
	const bookKey = bookRaw.replace(/\s+/g, '').toLowerCase();
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
