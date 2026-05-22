import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import {
	DBNotBuiltError,
	getInboundEdges,
	getNode,
	getOutboundEdges
} from '$lib/server/db';
import { expandCitation } from '$lib/server/citations';
import {
	CASES_EDGE_TYPES,
	CONCERNS_EDGE_TYPE,
	COUNTER_EDGE_TYPES,
	DEEPENING_EDGE_TYPES,
	SPECIAL_EDGE_TYPES,
	type EdgeWithPeer
} from '$lib/types';

type EdgeGroups = [string, EdgeWithPeer[]][];

function groupByType(edges: EdgeWithPeer[]): EdgeGroups {
	const out = new Map<string, EdgeWithPeer[]>();
	for (const e of edges) {
		if (!out.has(e.type)) out.set(e.type, []);
		out.get(e.type)!.push(e);
	}
	return Array.from(out.entries());
}

export const load: PageServerLoad = ({ params }) => {
	try {
		const node = getNode(params.slug);
		if (!node) throw error(404, `No node named '${params.slug}'`);

		const outbound = getOutboundEdges(params.slug);
		const inbound = getInboundEdges(params.slug);
		const sources = node.sources.map(expandCitation);

		// Partition outbound edges into the reading sections + the special
		// "concerns" prologue + mentions (lateral but noisy → its own bucket).
		const concerns = outbound.filter((e) => e.type === CONCERNS_EDGE_TYPE);
		const deeper = outbound.filter((e) => DEEPENING_EDGE_TYPES.has(e.type));
		const cases = outbound.filter((e) => CASES_EDGE_TYPES.has(e.type));
		const counter = outbound.filter((e) => COUNTER_EDGE_TYPES.has(e.type));
		const lateral = outbound.filter(
			(e) =>
				!DEEPENING_EDGE_TYPES.has(e.type) &&
				!CASES_EDGE_TYPES.has(e.type) &&
				!COUNTER_EDGE_TYPES.has(e.type) &&
				!SPECIAL_EDGE_TYPES.has(e.type)
		);
		const mentions = outbound.filter(
			(e) => e.type === 'mentions' || e.type === 'mentioned_in'
		);

		// Inbound: backlinks (everything inbound except mentions and the
		// concerns inverse, which we surface inline below).
		const backlinks = inbound.filter(
			(e) =>
				e.type !== 'mentions' &&
				e.type !== 'mentioned_in' &&
				e.type !== 'concerns'
		);
		// Other nodes that "are about" this one. Two ways to find them, same
		// result: inbound `concerns` edges, or outbound `concern_of` edges
		// (the latter is auto-inferred by reciprocity). We use the inbound
		// concerns view because the peer (e.source) is the relational Node.
		const concernOf = inbound.filter((e) => e.type === 'concerns');

		return {
			node,
			sources,
			concerns,                          // EdgeWithPeer[] — "Between X and Y"
			concernOf,                         // EdgeWithPeer[] — Nodes about this one
			deeperByType: groupByType(deeper), // "Deeper / Underlying"
			casesByType: groupByType(cases),   // "Specific cases / Applications"
			counterByType: groupByType(counter), // "Counter-arguments and responses"
			lateralByType: groupByType(lateral), // "Related"
			mentionsByType: groupByType(mentions), // mentions / mentioned_in
			backlinksByType: groupByType(backlinks) // remaining inbound
		};
	} catch (e) {
		if (e instanceof DBNotBuiltError) {
			throw error(503, e.message);
		}
		throw e;
	}
};
