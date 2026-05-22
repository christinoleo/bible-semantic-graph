import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { DBNotBuiltError, listNodesByTag } from '$lib/server/db';

export const load: PageServerLoad = ({ params }) => {
	try {
		const nodes = listNodesByTag(params.tag);
		if (nodes.length === 0) throw error(404, `No nodes tagged '${params.tag}'`);
		return { tag: params.tag, nodes };
	} catch (e) {
		if (e instanceof DBNotBuiltError) throw error(503, e.message);
		throw e;
	}
};
