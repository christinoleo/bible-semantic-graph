<script lang="ts">
	import type { PageProps } from './$types';
	let { data }: PageProps = $props();
</script>

<svelte:head>
	<title>{data.axis}: {data.value} — Bible Semantic Graph</title>
</svelte:head>

<h1>
	<span class="axis-label">{data.axis}</span>
	<span class="axis-pill" data-axis={data.axis}>{data.value}</span>
</h1>

{#if data.curated}
	<aside class="curated">
		<p class="curated-header">
			This {data.axis} value has a curated Node:
			<a href="/n/{data.curated.slug}"><strong>{data.curated.name}</strong></a>
			<span class="type-pill">{data.curated.type}</span>
		</p>
		<div class="curated-body">
			{@html data.curated.body_html}
		</div>
	</aside>
{/if}

<h2>
	Arguments classified as {data.axis} = {data.value}
	<span class="section-hint">({data.nodes.length})</span>
</h2>

<ul class="list">
	{#each data.nodes as n (n.slug)}
		<li>
			<a href="/n/{n.slug}">{n.name}</a>
			<span class="type-pill">{n.type}</span>
			{#each n.tags as t (t)}
				<a class="tag" href="/tag/{t}">{t}</a>
			{/each}
		</li>
	{/each}
</ul>

<style>
	.axis-label {
		font-family: var(--mono);
		font-size: 0.8rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--fg-muted);
		margin-right: 0.5rem;
	}
	.axis-pill {
		display: inline-block;
		font-size: 1rem;
		padding: 0.15rem 0.7rem;
		border-radius: 5px;
	}
	.axis-pill[data-axis='stance']    { background: #fce9e6; color: #a3372c; }
	.axis-pill[data-axis='tradition'] { background: #e9eefc; color: #2c4ea3; }
	.axis-pill[data-axis='method']    { background: #f3e9fc; color: #6b2ca3; }
	.axis-pill[data-axis='subject']   { background: #fcf5e0; color: #8a6a1d; }
	.curated {
		margin: 1rem 0 1.5rem;
		padding: 0.75rem 1rem;
		border-left: 3px solid var(--accent);
		background: var(--bg-card);
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
	.section-hint {
		font-size: 0.8rem;
		font-weight: normal;
		color: var(--fg-soft);
		font-family: var(--mono);
	}
</style>
