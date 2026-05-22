import type { PageServerLoad } from './$types';
import { DBNotBuiltError, axisValueCounts } from '$lib/server/db';
import { ARGUMENTATION_AXES, type ArgumentationAxis } from '$lib/types';

export type AxisIndexEntry = {
	axis: ArgumentationAxis;
	values: { value: string; count: number }[];
};

export const load: PageServerLoad = () => {
	try {
		const axes: AxisIndexEntry[] = ARGUMENTATION_AXES.map((axis) => ({
			axis,
			values: axisValueCounts(axis)
		}));
		return { axes };
	} catch (e) {
		if (e instanceof DBNotBuiltError) {
			return { dbMissing: e.message, axes: [] as AxisIndexEntry[] };
		}
		throw e;
	}
};
