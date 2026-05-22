import type { PageServerLoad } from './$types';
import {
	DBNotBuiltError,
	nodesBySlugs,
	searchText
} from '$lib/server/db';
import { semanticSearch } from '$lib/server/sidecar';
import type { NodeSummary, SearchHit } from '$lib/types';

interface RankedResult {
	node: NodeSummary;
	hits: SearchHit[];
}

export const load: PageServerLoad = async ({ url }) => {
	const q = url.searchParams.get('q')?.trim() ?? '';
	if (!q) return { q, results: [] as RankedResult[], semanticAvailable: true };

	let textHits: SearchHit[] = [];
	let semanticHits: SearchHit[] = [];
	let semanticAvailable = true;

	try {
		textHits = searchText(q, 25);
	} catch (e) {
		if (e instanceof DBNotBuiltError) {
			return {
				q,
				results: [],
				semanticAvailable: false,
				dbMissing: e.message
			};
		}
		throw e;
	}

	const semHits = await semanticSearch(q, 25);
	if (semHits === null) {
		semanticAvailable = false;
	} else {
		semanticHits = semHits.map((h) => ({
			slug: h.slug,
			score: 1 - h.distance,
			source: 'semantic' as const
		}));
	}

	// Merge by slug
	const bySlug = new Map<string, SearchHit[]>();
	for (const h of [...textHits, ...semanticHits]) {
		if (!bySlug.has(h.slug)) bySlug.set(h.slug, []);
		bySlug.get(h.slug)!.push(h);
	}
	const slugs = Array.from(bySlug.keys());
	const nodes = nodesBySlugs(slugs);
	const results: RankedResult[] = slugs
		.filter((s) => nodes.has(s))
		.map((slug) => ({ node: nodes.get(slug)!, hits: bySlug.get(slug)! }))
		.sort((a, b) => combinedScore(b.hits) - combinedScore(a.hits));

	return { q, results, semanticAvailable };
};

function combinedScore(hits: SearchHit[]): number {
	// Naive: sum text BM25-derived score + semantic similarity; ranked higher = better
	let score = 0;
	for (const h of hits) {
		if (h.source === 'text') score += h.score * 2; // text matches outrank semantic
		else score += h.score;
	}
	return score;
}
