<script lang="ts">
	import type { PageProps } from './$types';
	import type { EdgeWithPeer } from '$lib/types';
	let { data }: PageProps = $props();

	function fmtType(t: string): string {
		return t.replaceAll('_', ' ');
	}
</script>

<svelte:head>
	<title>{data.node.name} — Bible Semantic Graph</title>
</svelte:head>

<article>
	<header style="background:none;border:none;position:static;padding:0;">
		<h1>{data.node.name} <span class="type-pill">{data.node.type}</span></h1>
		{#if data.node.also.length > 0}
			<p class="meta">also: {data.node.also.join(', ')}</p>
		{/if}

		{#if data.concerns.length > 0}
			<p class="concerns">
				Between
				{#each data.concerns as e, i (e.target)}
					{#if e.peer}
						<a href="/n/{e.peer.slug}"><strong>{e.peer.name}</strong></a>
					{:else}
						<span class="wikilink-unresolved">{e.target}</span>
					{/if}
					{#if i < data.concerns.length - 2}, {:else if i === data.concerns.length - 2}{' and '}{/if}
				{/each}
			</p>
		{/if}

		{#if data.node.aliases.length > 0}
			<p class="aliases">
				aliases:
				{#each data.node.aliases as alias, i (alias)}
					<code>{alias}</code>{i < data.node.aliases.length - 1 ? ' · ' : ''}
				{/each}
			</p>
		{/if}
		{#if data.node.canon.length > 0}
			<p class="meta">
				canon:
				{#each data.node.canon as c (c)}
					<span class="canon-pill">{c}</span>
				{/each}
			</p>
		{/if}

		{#if data.node.argumentation}
			<div class="argumentation">
				{#each ['stance', 'tradition', 'method', 'subject'] as axis (axis)}
					{@const values = data.node.argumentation[axis]}
					{#if values && values.length > 0}
						<div class="axis-row">
							<span class="axis-label">{axis}</span>
							{#each values as v (v)}
								<a href="/axis/{axis}/{v}" class="axis-pill" data-axis={axis}>{v}</a>
							{/each}
						</div>
					{/if}
				{/each}
			</div>
		{/if}
		{#if data.node.tags.length > 0}
			<p class="meta">
				{#each data.node.tags as t (t)}
					<a class="tag" href="/tag/{t}">{t}</a>
				{/each}
			</p>
		{/if}
	</header>

	{#snippet edgeList(edges: EdgeWithPeer[])}
		<ul class="list">
			{#each edges as e (e.target + '|' + (e.source ?? '') + '|' + e.type + '|' + e.origin)}
				<li class:primary-edge={e.primary}>
					{#if e.peer}
						<a href="/n/{e.peer.slug}">{e.peer.name}</a>
						<span class="type-pill">{e.peer.type}</span>
					{:else}
						<span class="wikilink-unresolved">{e.target}</span>
					{/if}
					{#if e.note}<span class="meta">— {e.note}</span>{/if}
					{#if e.primary}<span class="meta primary-marker">★ primary</span>{/if}
					{#if e.origin !== 'frontmatter'}<span class="meta">({e.origin})</span>{/if}
				</li>
			{/each}
		</ul>
	{/snippet}

	{#snippet edgeSection(title: string, hint: string, groups: [string, EdgeWithPeer[]][])}
		{#if groups.length > 0}
			<h2>{title} <span class="section-hint">{hint}</span></h2>
			<div class="edges">
				{#each groups as [type, edges] (type)}
					<div class="edge-group">
						<header>{fmtType(type)}</header>
						{@render edgeList(edges)}
					</div>
				{/each}
			</div>
		{/if}
	{/snippet}

	{@render edgeSection(
		'Goes deeper into',
		'(underlying questions / what this invokes)',
		data.deeperByType
	)}

	{@render edgeSection(
		'Specific cases',
		'(applications / what builds on this)',
		data.casesByType
	)}

	{@render edgeSection(
		'Counter-arguments and responses',
		'(refutations, responses, contradictions)',
		data.counterByType
	)}

	{@render edgeSection(
		'Related',
		'(lateral — parallel, otherwise connected)',
		data.lateralByType
	)}

	{#if data.concernOf.length > 0}
		<h2>Relations involving this <span class="section-hint">(other Nodes whose subject is this one)</span></h2>
		<div class="edges">
			<div class="edge-group">
				{@render edgeList(data.concernOf)}
			</div>
		</div>
	{/if}

	<!-- Body comes AFTER the graph: the graph is the substance, the body is the label. -->
	{#if data.node.body_html.trim().length > 0}
		<h2>Note <span class="section-hint">(label — the graph carries the substance)</span></h2>
		<div class="body">
			{@html data.node.body_html}
		</div>
	{/if}

	{#if data.sources.length > 0}
		<h2>Sources</h2>
		<ul class="list">
			{#each data.sources as s (s.raw)}
				<li>
					{#if s.url}
						<a href={s.url} target="_blank" rel="noopener">{s.raw}</a>
						{#if s.reader_label}<span class="meta">— {s.reader_label}</span>{/if}
					{:else}
						<span>{s.raw}</span>
						<span class="meta">— unparseable citation</span>
					{/if}
				</li>
			{/each}
		</ul>
	{/if}

	{@render edgeSection(
		'Backlinks',
		'(other inbound connections)',
		data.backlinksByType
	)}

	{@render edgeSection(
		'Mentions',
		'(implicit links from wiki-link syntax)',
		data.mentionsByType
	)}
</article>

<style>
	.concerns {
		font-size: 1rem;
		margin: 0.25rem 0 0.75rem;
		color: var(--fg-muted);
	}
	.concerns a {
		color: var(--accent);
	}
	.canon-pill {
		display: inline-block;
		font-size: 0.7rem;
		text-transform: lowercase;
		letter-spacing: 0.04em;
		background: #e8f0e3;
		color: #3d6b2c;
		padding: 0.05rem 0.4rem;
		border-radius: 4px;
		margin: 0 0.2rem 0 0;
	}
	.argumentation {
		display: grid;
		gap: 0.3rem;
		margin: 0.5rem 0 1rem;
		padding: 0.6rem 0.8rem;
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: 6px;
	}
	.axis-row {
		display: flex;
		flex-wrap: wrap;
		gap: 0.3rem;
		align-items: baseline;
	}
	.axis-label {
		font-family: var(--mono);
		font-size: 0.7rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--fg-muted);
		min-width: 5.5rem;
	}
	.axis-pill {
		display: inline-block;
		font-size: 0.78rem;
		padding: 0.05rem 0.5rem;
		border-radius: 4px;
		text-decoration: none;
	}
	.axis-pill[data-axis='stance']    { background: #fce9e6; color: #a3372c; }
	.axis-pill[data-axis='tradition'] { background: #e9eefc; color: #2c4ea3; }
	.axis-pill[data-axis='method']    { background: #f3e9fc; color: #6b2ca3; }
	.axis-pill[data-axis='subject']   { background: #fcf5e0; color: #8a6a1d; }
	.axis-pill:hover { text-decoration: underline; }
	.section-hint {
		font-size: 0.75rem;
		font-weight: normal;
		color: var(--fg-soft);
		font-family: var(--mono);
	}
	.primary-edge {
		font-weight: 500;
	}
	.primary-marker {
		color: var(--accent);
		font-weight: 500;
	}
</style>
