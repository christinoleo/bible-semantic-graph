import type { PageServerLoad } from './$types';
import {
	DBNotBuiltError,
	axisValueCounts,
	edgeCount,
	mostConnectedNodes,
	totalCount,
	typeCounts
} from '$lib/server/db';
import { ARGUMENTATION_AXES, type ArgumentationAxis, type NodeSummary } from '$lib/types';

export type AxisPreview = {
	axis: ArgumentationAxis;
	values: { value: string; count: number }[];
	total: number;
};

export const load: PageServerLoad = () => {
	try {
		const axes: AxisPreview[] = ARGUMENTATION_AXES.map((axis) => {
			const all = axisValueCounts(axis);
			return {
				axis,
				values: all.slice(0, 6),
				total: all.length
			};
		});
		return {
			total: totalCount(),
			edges: edgeCount(),
			byType: typeCounts(),
			featured: mostConnectedNodes(8),
			axes
		};
	} catch (e) {
		if (e instanceof DBNotBuiltError) {
			return {
				dbMissing: e.message,
				total: 0,
				edges: 0,
				byType: [] as { type: string; count: number }[],
				featured: [] as (NodeSummary & { degree: number })[],
				axes: [] as AxisPreview[]
			};
		}
		throw e;
	}
};
