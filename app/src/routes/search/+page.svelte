<script lang="ts">
	import type { PageProps } from './$types';
	let { data }: PageProps = $props();
</script>

<svelte:head>
	<title>Search: {data.q || '…'}</title>
</svelte:head>

<h1>Search</h1>
{#if data.q}
	<p class="meta">
		Query: <strong>{data.q}</strong> —
		{data.results.length} result{data.results.length === 1 ? '' : 's'}
		{#if !data.semanticAvailable}
			· <span style="color:var(--unresolved)">semantic search unavailable</span>
		{/if}
	</p>
{:else}
	<p class="meta">Type a query in the search bar above.</p>
{/if}

{#if data.dbMissing}
	<div class="notice">{data.dbMissing}</div>
{/if}

{#if data.results.length > 0}
	<ul class="list">
		{#each data.results as r (r.node.slug)}
			<li>
				<a href="/n/{r.node.slug}">{r.node.name}</a>
				<span class="type-pill">{r.node.type}</span>
				<span class="meta">
					[{r.hits.map((h) => h.source).join(' + ')}]
				</span>
				{#each r.hits as h (h.source)}
					{#if h.source === 'text' && h.snippet}
						<div class="meta" style="font-size:0.88rem">{@html h.snippet}</div>
					{/if}
				{/each}
			</li>
		{/each}
	</ul>
{/if}
