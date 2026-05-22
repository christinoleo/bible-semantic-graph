<script lang="ts">
	import type { PageProps } from './$types';
	import StratifiedIndex from '$lib/StratifiedIndex.svelte';
	import { AXIS_ACCENT, AXIS_GLOSS } from '$lib/typeMeta';

	let { data }: PageProps = $props();

	const accent = $derived(AXIS_ACCENT[data.axis] ?? '#5b3a99');
	const gloss = $derived(AXIS_GLOSS[data.axis] ?? '');
</script>

<svelte:head>
	<title>{data.axis}: {data.value} — Bible Semantic Graph</title>
</svelte:head>

{#if data.curated}
	<aside class="curated" style="--accent: {accent}">
		<p class="curated-header">
			This {data.axis} value has a curated Node:
			<a href="/n/{data.curated.slug}"><strong>{data.curated.name}</strong></a>
			<span class="type-pill" data-type={data.curated.type}>{data.curated.type}</span>
		</p>
		<div class="curated-body">
			{@html data.curated.body_html}
		</div>
	</aside>
{/if}

<StratifiedIndex
	title={data.value}
	eyebrow="{data.axis} · {gloss}"
	subtitle="Arguments classified under this axis value"
	{accent}
	glyph="§"
	nodes={data.nodes}
	showTypeOnRow={true}
/>

<style>
	.curated {
		margin: 1rem 0 1.5rem;
		padding: 0.85rem 1.1rem;
		border-left: 3px solid var(--accent);
		background: #fff;
		border-radius: 0 5px 5px 0;
	}
	.curated-header {
		margin: 0 0 0.5rem;
		font-size: 0.85rem;
		color: var(--fg-muted);
	}
	.curated-body :global(p) {
		margin: 0.4rem 0;
	}
</style>
