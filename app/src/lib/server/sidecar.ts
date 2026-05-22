/**
 * Thin client for the Python ML sidecar. Bind to 127.0.0.1 only.
 * Returns null on failure rather than throwing — callers degrade to text-only.
 */

const SIDECAR_URL = process.env.SIDECAR_URL ?? 'http://127.0.0.1:7655';

export interface SemanticHit {
	slug: string;
	distance: number;
}

export async function semanticSearch(
	query: string,
	limit = 20
): Promise<SemanticHit[] | null> {
	try {
		const res = await fetch(`${SIDECAR_URL}/search/semantic`, {
			method: 'POST',
			headers: { 'content-type': 'application/json' },
			body: JSON.stringify({ query, limit }),
			signal: AbortSignal.timeout(5000)
		});
		if (!res.ok) return null;
		const data = (await res.json()) as { hits: SemanticHit[] };
		return data.hits ?? [];
	} catch {
		return null;
	}
}
