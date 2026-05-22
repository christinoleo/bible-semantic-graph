export interface NodeSummary {
	slug: string;
	type: string;
	name: string;
	tags: string[];
}

export interface Argumentation {
	stance: string[];
	tradition: string[];
	method: string[];
	subject: string[];
}

export const ARGUMENTATION_AXES = ['stance', 'tradition', 'method', 'subject'] as const;
export type ArgumentationAxis = (typeof ARGUMENTATION_AXES)[number];

export interface NodeFull extends NodeSummary {
	also: string[];
	aliases: string[];
	sources: string[];
	canon: string[];
	argumentation: Argumentation | null;
	body_html: string;
}

export interface EdgeRow {
	source: string;
	target: string;
	type: string;
	note: string | null;
	primary: boolean;
	origin: 'frontmatter' | 'wikilink' | 'inferred';
}

export interface EdgeWithPeer extends EdgeRow {
	peer: NodeSummary | null;
}

/** Edge types that mean "going DEEPER / toward the more fundamental".
 *  Outbound edges of these types render in the "Deeper" section. */
export const DEEPENING_EDGE_TYPES = new Set([
	'invokes',
	'case_of',
	'presupposes',
	'instance_of',
	'builds_on',
	'specializes',
	'supports'
]);

/** Edge types that mean "MORE SPECIFIC cases of this Node".
 *  Outbound edges of these types (i.e., inverses of the deepening set) render
 *  in the "Cases / Applications" section. */
export const CASES_EDGE_TYPES = new Set([
	'invoked_by',
	'has_case',
	'presupposed_by',
	'has_instance',
	'extended_by',
	'generalizes',
	'supported_by'
]);

/** Argumentative-opposition edges. Get their own UI section so contradiction
 *  / response chains are salient rather than buried in "Related". */
export const COUNTER_EDGE_TYPES = new Set([
	'refutes',
	'refuted_by',
	'responds_to',
	'has_response',
	'contradicts'
]);

/** Edges that represent the "relata" of a Relational Node — rendered as
 *  "Between X and Y" at the top. */
export const CONCERNS_EDGE_TYPE = 'concerns';

/** Edges treated separately from the three reading sections. */
export const SPECIAL_EDGE_TYPES = new Set([
	CONCERNS_EDGE_TYPE,
	'concern_of',
	'mentions',
	'mentioned_in'
]);

export interface SearchHit {
	slug: string;
	score: number;
	source: 'text' | 'semantic';
	snippet?: string;
}

export interface CitationLink {
	raw: string;
	url: string | null;
	reader_label: string | null;
}
