import type { PageServerLoad } from './$types';
import { DBNotBuiltError, listNodes, totalCount, typeCounts } from '$lib/server/db';

export const load: PageServerLoad = () => {
	try {
		return {
			total: totalCount(),
			byType: typeCounts(),
			nodes: listNodes()
		};
	} catch (e) {
		if (e instanceof DBNotBuiltError) {
			return { dbMissing: e.message, total: 0, byType: [], nodes: [] };
		}
		throw e;
	}
};
