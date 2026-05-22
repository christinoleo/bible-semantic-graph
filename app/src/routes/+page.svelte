<script lang="ts">
	import type { PageProps } from './$types';
	let { data }: PageProps = $props();
</script>

<h1>Bible Semantic Graph</h1>
<p class="meta">
	{data.total} node{data.total === 1 ? '' : 's'} indexed.
</p>

{#if data.dbMissing}
	<div class="notice">{data.dbMissing}</div>
{/if}

{#if data.byType.length > 0}
	<h2>Browse by type</h2>
	<ul class="list">
		{#each data.byType as { type, count } (type)}
			<li>
				<a href="/type/{type}"><span class="type-pill">{type}</span></a>
				<span class="meta">— {count}</span>
			</li>
		{/each}
	</ul>
{/if}

<h2>Browse by argumentation</h2>
<p class="meta"><a href="/axis">All four axes →</a> (stance · tradition · method · subject)</p>

{#if data.nodes.length > 0}
	<h2>All nodes</h2>
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
{/if}
