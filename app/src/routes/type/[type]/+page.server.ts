import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { DBNotBuiltError, listNodesByTypeWithDegree } from '$lib/server/db';

export const load: PageServerLoad = ({ params }) => {
	try {
		const nodes = listNodesByTypeWithDegree(params.type);
		if (nodes.length === 0) throw error(404, `No nodes of type '${params.type}'`);
		return { type: params.type, nodes };
	} catch (e) {
		if (e instanceof DBNotBuiltError) throw error(503, e.message);
		throw e;
	}
};
