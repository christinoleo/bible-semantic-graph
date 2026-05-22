<script lang="ts">
	import type { PageProps } from './$types';
	let { data }: PageProps = $props();
</script>

<svelte:head>
	<title>{data.type} — Bible Semantic Graph</title>
</svelte:head>

<h1><span class="type-pill">{data.type}</span></h1>
<p class="meta">{data.nodes.length} node{data.nodes.length === 1 ? '' : 's'}</p>

<ul class="list">
	{#each data.nodes as n (n.slug)}
		<li>
			<a href="/n/{n.slug}">{n.name}</a>
			{#each n.tags as t (t)}
				<a class="tag" href="/tag/{t}">{t}</a>
			{/each}
		</li>
	{/each}
</ul>
