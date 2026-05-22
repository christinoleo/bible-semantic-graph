import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { DBNotBuiltError, getNode, listNodesByAxisValue } from '$lib/server/db';
import { ARGUMENTATION_AXES, type ArgumentationAxis } from '$lib/types';

export const load: PageServerLoad = ({ params }) => {
	if (!ARGUMENTATION_AXES.includes(params.axis as ArgumentationAxis)) {
		throw error(404, `Unknown axis '${params.axis}' — must be one of ${ARGUMENTATION_AXES.join(', ')}`);
	}
	try {
		const nodes = listNodesByAxisValue(params.axis, params.value);
		// If a Node exists with slug == this axis value, surface it as the
		// curated companion — the axis page is the raw filter, the Node is
		// the editorial commentary.
		const curated = getNode(params.value);
		if (nodes.length === 0 && !curated) {
			throw error(404, `No Nodes with ${params.axis}: ${params.value}`);
		}
		return { axis: params.axis, value: params.value, nodes, curated };
	} catch (e) {
		if (e instanceof DBNotBuiltError) throw error(503, e.message);
		throw e;
	}
};
