import type { PageServerLoad } from './$types';
import { DBNotBuiltError, listNodes } from '$lib/server/db';
import type { NodeSummary } from '$lib/types';

export const load: PageServerLoad = () => {
	try {
		return { nodes: listNodes() };
	} catch (e) {
		if (e instanceof DBNotBuiltError) {
			return { dbMissing: e.message, nodes: [] as NodeSummary[] };
		}
		throw e;
	}
};
