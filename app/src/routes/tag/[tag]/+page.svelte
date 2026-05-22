<script lang="ts">
	import type { PageProps } from './$types';
	let { data }: PageProps = $props();
</script>

<svelte:head>
	<title>#{data.tag} — Bible Semantic Graph</title>
</svelte:head>

<h1>#{data.tag}</h1>
<p class="meta">{data.nodes.length} node{data.nodes.length === 1 ? '' : 's'}</p>

<ul class="list">
	{#each data.nodes as n (n.slug)}
		<li>
			<a href="/n/{n.slug}">{n.name}</a>
			<span class="type-pill">{n.type}</span>
		</li>
	{/each}
</ul>
