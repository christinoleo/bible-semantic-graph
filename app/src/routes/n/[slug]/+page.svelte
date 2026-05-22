<script lang="ts">
	import type { PageProps } from './$types';
	import type { EdgeWithPeer, ArgumentationAxis } from '$lib/types';
	import { ARGUMENTATION_AXES } from '$lib/types';

	let { data }: PageProps = $props();

	// Direction-aware display label for an edge type. Reads as
	// "[this node] [label] [linked node]". The ontology stores the forward
	// and inverse phrasing as two separate edge types (e.g. responds_to /
	// has_response), so a single lookup gives the right phrase for each
	// side. Falls back to a snake_case → space rewrite when the ontology
	// has not yet assigned a label (e.g. an auto-registered new type).
	function edgeLabel(type: string): string {
		return data.edgeLabels[type] ?? type.replaceAll('_', ' ');
	}

	// Flatten the grouped (by edge type) shape returned by the server into a
	// single ordered list per direction — primary edge first, others after.
	// The edge type still appears as metadata on each row, so no information
	// is lost; grouping by type was a programmer's organisation, not a
	// reader's. Reader navigates by peer name and direction.
	function flatten(groups: [string, EdgeWithPeer[]][]): EdgeWithPeer[] {
		const flat = groups.flatMap(([, es]) => es);
		return flat.sort((a, b) => (b.primary ? 1 : 0) - (a.primary ? 1 : 0));
	}

	/** Convert a "MM:SS" / "M:SS" / "H:MM:SS" timestamp to whole seconds.
	 *  YouTube's `?t=` URL parameter accepts seconds; "12:34" alone would
	 *  not be honoured. Passes through anything already numeric. */
	function timestampToSeconds(ts: string): string {
		if (/^\d+$/.test(ts)) return ts;
		const parts = ts.split(':').map((p) => parseInt(p, 10));
		if (parts.some(Number.isNaN)) return ts; // unrecognised, hand it through
		let secs = 0;
		for (const part of parts) secs = secs * 60 + part;
		return String(secs);
	}

	function videoUrl(url: string, timestamp?: string): string {
		if (!timestamp) return url;
		const t = timestampToSeconds(timestamp);
		return `${url}${url.includes('?') ? '&' : '?'}t=${t}`;
	}

	const cases = $derived(flatten(data.casesByType));
	const deeper = $derived(flatten(data.deeperByType));
	const support = $derived(flatten(data.supportByType));
	const counter = $derived(flatten(data.counterByType));
	const lateral = $derived(flatten(data.lateralByType));
	const mentions = $derived(flatten(data.mentionsByType));
	const backlinks = $derived(flatten(data.backlinksByType));

	const edgeKey = (e: EdgeWithPeer): string =>
		`${e.target}|${e.source ?? ''}|${e.type}|${e.origin}`;

	function axisValues(axis: ArgumentationAxis): string[] {
		return data.node.argumentation ? data.node.argumentation[axis] : [];
	}
</script>

<svelte:head>
	<title>{data.node.name} — Bible Semantic Graph</title>
</svelte:head>

{#snippet edgeRow(e: EdgeWithPeer)}
	<li class="edge" class:primary={e.primary}>
		<div class="edge-marker" aria-hidden="true">{e.primary ? '★' : ''}</div>
		<div class="edge-main">
			<div class="edge-line">
				{#if e.peer}
					<a class="edge-peer" href="/n/{e.peer.slug}">{e.peer.name}</a>
					<span class="type-pill">{e.peer.type}</span>
				{:else}
					<span class="wikilink-unresolved">{e.target}</span>
				{/if}
				<span class="edge-type">{edgeLabel(e.type)}</span>
			</div>
			{#if e.note}
				<p class="edge-note">
					{#if e.noteSegments && e.noteSegments.length > 0}{#each e.noteSegments as seg, i (i)}{#if seg.kind === 'text'}{seg.text}{:else}<a
									class="ref-link"
									href={seg.ref.url ?? '#'}
									target="_blank"
									rel="noopener"
									title={seg.ref.reader_label ?? ''}>{seg.text} ↗</a
								>{/if}{/each}{:else}{e.note}{/if}
				</p>
			{/if}
		</div>
	</li>
{/snippet}

<article class="compass">
	{#if cases.length > 0}
		<section class="region cases" data-dir="up">
			<header class="dir-header">
				<span class="dir-glyph" aria-hidden="true">↑</span>
				<h2 class="dir-label">sub-topics</h2>
				<span class="dir-count">{cases.length}</span>
			</header>
			<ul class="edge-list edge-list-wide">
				{#each cases as e (edgeKey(e))}
					{@render edgeRow(e)}
				{/each}
			</ul>
		</section>
	{/if}

	{#if lateral.length > 0}
		<aside class="region related" data-dir="lateral">
			<header class="dir-header">
				<span class="dir-glyph" aria-hidden="true">◇</span>
				<h2 class="dir-label">related</h2>
				<span class="dir-count">{lateral.length}</span>
			</header>
			<ul class="edge-list">
				{#each lateral as e (edgeKey(e))}
					{@render edgeRow(e)}
				{/each}
			</ul>
		</aside>
	{/if}

	<section class="region identity">
		<div class="type-tab">{data.node.type}</div>
		<div class="shelf">
			<span class="shelf-label">shelf</span>
			<code class="shelf-slug">{data.node.slug}</code>
		</div>

		<h1 class="node-name">{data.node.name}</h1>

		{#if data.node.also.length > 0}
			<p class="also-row">
				<span class="meta-label">also</span>
				{#each data.node.also as t (t)}
					<span class="also-pill">{t}</span>
				{/each}
			</p>
		{/if}

		{#if data.concerns.length > 0}
			<p class="between">
				Between
				{#each data.concerns as e, i (e.target)}
					{#if e.peer}
						<a href="/n/{e.peer.slug}"><strong>{e.peer.name}</strong></a>
					{:else}
						<span class="wikilink-unresolved">{e.target}</span>
					{/if}
					{#if i < data.concerns.length - 2}, {:else if i === data.concerns.length - 2} and {/if}
				{/each}
			</p>
		{/if}

		{#if data.node.aliases.length > 0}
			<p class="aliases">
				<span class="meta-label">aliases</span>
				{#each data.node.aliases as alias (alias)}
					<code>{alias}</code>
				{/each}
			</p>
		{/if}

		{#if data.node.canon.length > 0}
			<p class="canon-row">
				<span class="meta-label">canon</span>
				{#each data.node.canon as c (c)}
					<span class="canon-pill">{c}</span>
				{/each}
			</p>
		{/if}

		{#if data.node.argumentation}
			<div class="argumentation">
				{#each ARGUMENTATION_AXES as axis (axis)}
					{@const values = axisValues(axis)}
					{#if values.length > 0}
						<div class="axis-row">
							<span class="axis-label">{axis}</span>
							<div class="axis-values">
								{#each values as v (v)}
									<a href="/axis/{axis}/{v}" class="axis-pill" data-axis={axis}>{v}</a>
								{/each}
							</div>
						</div>
					{/if}
				{/each}
			</div>
		{/if}

		{#if data.node.body_html.trim().length > 0}
			<div class="body">
				{@html data.node.body_html}
			</div>
		{/if}

		{#if data.concernOf.length > 0}
			<div class="named-in">
				<span class="meta-label">named in</span>
				<ul class="named-in-list">
					{#each data.concernOf as e (edgeKey(e))}
						<li>
							{#if e.peer}
								<a href="/n/{e.peer.slug}">{e.peer.name}</a>
								<span class="type-pill">{e.peer.type}</span>
							{:else}
								<span class="wikilink-unresolved">{e.target}</span>
							{/if}
						</li>
					{/each}
				</ul>
			</div>
		{/if}

		{#if data.sources.length > 0}
			<div class="sources">
				<span class="meta-label">sources</span>
				<ul>
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
			</div>
		{/if}

		{#if data.node.videos.length > 0}
			<div class="videos">
				<span class="meta-label">videos</span>
				<ul>
					{#each data.node.videos as v (v.url)}
						<li>
							<a
								class="video-chip"
								href={videoUrl(v.url, v.timestamp)}
								target="_blank"
								rel="noopener"
								title={v.title ?? v.url}
							>
								<svg class="yt-logo" viewBox="0 0 24 24" aria-hidden="true">
									<path d="M21.6 7.2a2.5 2.5 0 0 0-1.76-1.77C18.25 5 12 5 12 5s-6.25 0-7.84.43A2.5 2.5 0 0 0 2.4 7.2C2 8.8 2 12 2 12s0 3.2.4 4.8a2.5 2.5 0 0 0 1.76 1.77C5.75 19 12 19 12 19s6.25 0 7.84-.43a2.5 2.5 0 0 0 1.76-1.77c.4-1.6.4-4.8.4-4.8s0-3.2-.4-4.8zM10 15V9l5.2 3-5.2 3z" fill="currentColor"/>
								</svg>
								<span class="video-title">{v.title ?? v.url}</span>
								{#if v.timestamp}<span class="video-ts">@ {v.timestamp}</span>{/if}
							</a>
						</li>
					{/each}
				</ul>
			</div>
		{/if}

		{#if data.node.tags.length > 0}
			<p class="tags-row">
				{#each data.node.tags as t (t)}
					<a class="tag" href="/tag/{t}">{t}</a>
				{/each}
			</p>
		{/if}
	</section>

	{#if support.length > 0}
		<aside class="region support" data-dir="support">
			<header class="dir-header">
				<span class="dir-glyph" aria-hidden="true">✓</span>
				<h2 class="dir-label">arguments in favor</h2>
				<span class="dir-count">{support.length}</span>
			</header>
			<ul class="edge-list">
				{#each support as e (edgeKey(e))}
					{@render edgeRow(e)}
				{/each}
			</ul>
		</aside>
	{/if}

	{#if counter.length > 0}
		<aside class="region counter" data-dir="counter">
			<header class="dir-header">
				<span class="dir-glyph" aria-hidden="true">↯</span>
				<h2 class="dir-label">arguments against</h2>
				<span class="dir-count">{counter.length}</span>
			</header>
			<ul class="edge-list">
				{#each counter as e (edgeKey(e))}
					{@render edgeRow(e)}
				{/each}
			</ul>
		</aside>
	{/if}

	{#if deeper.length > 0}
		<section class="region deeping" data-dir="down">
			<header class="dir-header">
				<span class="dir-glyph" aria-hidden="true">↓</span>
				<h2 class="dir-label">depends on</h2>
				<span class="dir-count">{deeper.length}</span>
			</header>
			<ul class="edge-list edge-list-wide">
				{#each deeper as e (edgeKey(e))}
					{@render edgeRow(e)}
				{/each}
			</ul>
		</section>
	{/if}

	{#if backlinks.length > 0 || mentions.length > 0}
		<section class="region outer">
			<div class="outer-grid">
				{#if backlinks.length > 0}
					<div class="peripheral-block">
						<h3 class="peripheral-label">other inbound</h3>
						<ul class="peripheral-list">
							{#each backlinks as e (edgeKey(e))}
								<li>
									{#if e.peer}
										<a href="/n/{e.peer.slug}">{e.peer.name}</a>
									{:else}
										<span class="wikilink-unresolved">{e.target}</span>
									{/if}
									<span class="edge-type">{edgeLabel(e.type)}</span>
								</li>
							{/each}
						</ul>
					</div>
				{/if}
				{#if mentions.length > 0}
					<div class="peripheral-block">
						<h3 class="peripheral-label">mentions</h3>
						<ul class="peripheral-list">
							{#each mentions as e (edgeKey(e))}
								<li>
									{#if e.peer}
										<a href="/n/{e.peer.slug}">{e.peer.name}</a>
									{:else}
										<span class="wikilink-unresolved">{e.target}</span>
									{/if}
								</li>
							{/each}
						</ul>
					</div>
				{/if}
			</div>
		</section>
	{/if}
</article>

<style>
	/* Break the article out of the global 980px main column on wide viewports. */
	:global(main:has(.compass)) {
		max-width: 1480px;
		padding-inline: 2rem;
	}
	@media (max-width: 1199px) {
		:global(main:has(.compass)) {
			max-width: 760px;
			padding-inline: 1.25rem;
		}
	}

	/* ===== Compass grid =================================================== */
	.compass {
		display: grid;
		gap: 2.5rem 2.25rem;
		grid-template-columns: minmax(0, 1fr) minmax(0, 2.4fr) minmax(0, 1fr);
		align-items: start;
	}

	.region {
		min-width: 0;
	}

	.support {
		grid-column: 1 / 2;
		grid-row: 1;
	}
	.identity {
		grid-column: 2 / 3;
		grid-row: 1;
	}
	.counter {
		grid-column: 3 / 4;
		grid-row: 1;
	}
	.related {
		grid-column: 1 / 2;
		grid-row: 2;
	}
	.deeping {
		grid-column: 2 / 3;
		grid-row: 2;
	}
	.cases {
		grid-column: 3 / 4;
		grid-row: 2;
	}
	.outer {
		grid-column: 1 / -1;
		grid-row: 3;
	}

	/* When no flanking columns exist, identity centers nicely. */
	.compass:not(:has(.related)):not(:has(.counter)):not(:has(.support)) .identity {
		grid-column: 1 / -1;
		max-width: 780px;
		justify-self: center;
		width: 100%;
	}

	/* ===== Mobile / narrow — stack with directional accents ============== */
	@media (max-width: 1199px) {
		.compass {
			grid-template-columns: 1fr;
			grid-template-rows: none;
			gap: 2.5rem;
		}
		.cases,
		.support,
		.related,
		.identity,
		.counter,
		.deeping,
		.outer {
			grid-column: 1 / -1;
			grid-row: auto;
		}
		.identity {
			order: 1;
			justify-self: stretch;
			max-width: none;
		}
		.deeping {
			order: 2;
		}
		.cases {
			order: 3;
		}
		.support {
			order: 4;
		}
		.counter {
			order: 5;
		}
		.related {
			order: 6;
		}
		.outer {
			order: 7;
		}

		/* On mobile, give each direction a colored left rail — the desktop spatial
		   cue is gone, so the color does the work. */
		.region[data-dir] {
			border-left: 3px solid var(--dir-color, var(--border));
			padding-left: 1rem;
		}
	}

	/* ===== Directional header ============================================= */
	.dir-header {
		display: flex;
		align-items: baseline;
		gap: 0.85rem;
		margin: 0 0 1.1rem;
		padding: 0;
		border: none;
		background: none;
		position: static;
	}
	.dir-glyph {
		font-size: 1.65rem;
		font-weight: 300;
		line-height: 1;
		color: var(--dir-color, var(--fg-muted));
	}
	.dir-label {
		font-family: var(--mono);
		font-size: 0.72rem;
		font-weight: 500;
		letter-spacing: 0.22em;
		text-transform: uppercase;
		color: var(--fg-muted);
		margin: 0;
		padding: 0;
		border: none;
	}
	.dir-count {
		font-family: var(--mono);
		font-size: 0.7rem;
		color: var(--fg-soft);
		margin-left: auto;
		letter-spacing: 0.05em;
	}

	[data-dir='up'] {
		--dir-color: #a07c1a;
	}
	[data-dir='down'] {
		--dir-color: var(--accent);
	}
	[data-dir='lateral'] {
		--dir-color: var(--fg-muted);
	}
	[data-dir='counter'] {
		--dir-color: var(--unresolved);
	}
	[data-dir='support'] {
		--dir-color: #2d7a3e;
	}

	/* ===== Edge list & row =============================================== */
	.edge-list {
		list-style: none;
		margin: 0;
		padding: 0;
	}
	.edge-list-wide {
		columns: 2;
		column-gap: 2.5rem;
	}
	/* Cases now lives in a single narrow column; force single-column edge list. */
	.cases .edge-list-wide {
		columns: 1;
	}
	@media (max-width: 1199px) {
		.edge-list-wide {
			columns: 1;
		}
	}

	.edge {
		display: grid;
		grid-template-columns: 1.2rem 1fr;
		gap: 0.5rem;
		padding: 0.55rem 0;
		border-top: 1px solid var(--border);
		align-items: baseline;
		break-inside: avoid;
	}
	.edge:first-child {
		border-top: none;
	}
	.edge-marker {
		text-align: center;
		color: var(--accent);
		font-size: 0.9rem;
		line-height: 1;
	}
	.edge-main {
		min-width: 0;
	}
	.edge-line {
		display: flex;
		align-items: baseline;
		gap: 0.45rem;
		flex-wrap: wrap;
	}
	.edge-peer {
		color: var(--fg);
		font-weight: 500;
	}
	.edge-peer:hover {
		color: var(--accent);
		text-decoration: underline;
	}
	.edge.primary .edge-peer {
		color: var(--accent);
	}
	.edge-type {
		margin-left: auto;
		font-family: var(--mono);
		font-size: 0.68rem;
		letter-spacing: 0.06em;
		color: var(--fg-soft);
		white-space: nowrap;
	}
	.edge-note {
		margin: 0.2rem 0 0;
		color: var(--fg-muted);
		font-size: 0.88rem;
		line-height: 1.45;
	}

	/* ===== Identity / center card ======================================= */
	.identity {
		position: relative;
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: 4px;
		padding: 2.5rem 2.25rem 2rem;
		box-shadow:
			0 1px 2px rgba(50, 40, 20, 0.04),
			0 12px 28px -16px rgba(50, 40, 20, 0.12);
	}
	@media (max-width: 1199px) {
		.identity {
			padding: 2rem 1.25rem 1.5rem;
		}
	}

	.type-tab {
		position: absolute;
		top: -0.9rem;
		right: 1.5rem;
		background: var(--accent);
		color: #fff;
		padding: 0.32rem 0.95rem;
		font-family: var(--mono);
		font-size: 0.68rem;
		font-weight: 500;
		letter-spacing: 0.16em;
		text-transform: uppercase;
		border-radius: 2px;
		box-shadow: 0 3px 8px -3px rgba(91, 58, 153, 0.4);
	}

	.shelf {
		display: flex;
		align-items: baseline;
		gap: 0.55rem;
		margin: 0 0 1.5rem;
		padding-bottom: 0.6rem;
		border-bottom: 1px dashed var(--border);
	}
	.shelf-label {
		font-family: var(--mono);
		font-size: 0.62rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		color: var(--fg-soft);
	}
	.shelf-slug {
		font-family: var(--mono);
		font-size: 0.78rem;
		color: var(--fg-muted);
		word-break: break-all;
	}

	.node-name {
		font-family: inherit;
		font-size: 2.4rem;
		font-weight: 600;
		line-height: 1.05;
		margin: 0 0 0.75rem;
		letter-spacing: -0.01em;
	}
	@media (min-width: 1200px) {
		.node-name::first-letter {
			font-size: 1.35em;
			color: var(--accent);
			font-weight: 600;
			padding-right: 0.04em;
		}
	}
	@media (max-width: 1199px) {
		.node-name {
			font-size: 1.85rem;
		}
	}

	.also-row {
		margin: 0 0 0.6rem;
		display: flex;
		flex-wrap: wrap;
		gap: 0.3rem;
		align-items: baseline;
	}
	.also-pill {
		display: inline-block;
		font-family: var(--mono);
		font-size: 0.6rem;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--fg-soft);
		background: var(--bg);
		border: 1px solid var(--border);
		padding: 0.1rem 0.45rem;
		border-radius: 2px;
	}

	.between {
		font-size: 1rem;
		margin: 0 0 0.85rem;
		color: var(--fg-muted);
	}
	.between a {
		color: var(--accent);
	}

	.meta-label {
		font-family: var(--mono);
		font-size: 0.62rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		color: var(--fg-soft);
		margin-right: 0.5rem;
	}

	.aliases {
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 0.3rem;
		margin: 0 0 0.5rem;
	}
	.aliases code {
		font-family: var(--mono);
		background: var(--bg);
		padding: 0.05rem 0.4rem;
		border-radius: 2px;
		font-size: 0.85rem;
	}

	.canon-row {
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 0.3rem;
		margin: 0 0 1rem;
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
	}

	.argumentation {
		display: grid;
		gap: 0.4rem;
		margin: 1.1rem 0 1.4rem;
		padding: 0.85rem 1rem;
		background: var(--bg);
		border-left: 2px solid var(--accent);
		border-radius: 0 4px 4px 0;
	}
	.axis-row {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
		align-items: baseline;
	}
	.axis-label {
		font-family: var(--mono);
		font-size: 0.62rem;
		letter-spacing: 0.16em;
		text-transform: uppercase;
		color: var(--fg-soft);
		min-width: 5.5rem;
	}
	.axis-values {
		display: flex;
		flex-wrap: wrap;
		gap: 0.3rem;
	}
	.axis-pill {
		display: inline-block;
		font-size: 0.78rem;
		padding: 0.05rem 0.5rem;
		border-radius: 3px;
		text-decoration: none;
	}
	.axis-pill[data-axis='stance'] {
		background: #fce9e6;
		color: #a3372c;
	}
	.axis-pill[data-axis='tradition'] {
		background: #e9eefc;
		color: #2c4ea3;
	}
	.axis-pill[data-axis='method'] {
		background: #f3e9fc;
		color: #6b2ca3;
	}
	.axis-pill[data-axis='subject'] {
		background: #fcf5e0;
		color: #8a6a1d;
	}
	.axis-pill:hover {
		text-decoration: underline;
	}

	.body {
		max-width: 62ch;
		margin: 1.5rem 0;
		font-size: 1.02rem;
		line-height: 1.65;
	}
	.body :global(p) {
		margin: 0 0 1rem;
	}

	.named-in {
		margin: 1.4rem 0 0;
		padding-top: 1rem;
		border-top: 1px dashed var(--border);
	}
	.named-in-list {
		list-style: none;
		padding: 0;
		margin: 0.4rem 0 0;
	}
	.named-in-list li {
		padding: 0.25rem 0;
		font-size: 0.92rem;
	}

	.sources {
		margin: 1.5rem 0 0;
		padding-top: 1rem;
		border-top: 1px solid var(--border);
	}
	.sources ul {
		list-style: none;
		margin: 0.4rem 0 0;
		padding: 0;
	}
	.sources li {
		padding: 0.2rem 0;
		font-size: 0.92rem;
	}

	.videos {
		margin: 1rem 0 0;
	}
	.videos ul {
		list-style: none;
		margin: 0.4rem 0 0;
		padding: 0;
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
	}
	.videos li {
		margin: 0;
	}
	.video-chip {
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		padding: 0.3rem 0.6rem 0.3rem 0.4rem;
		border: 1px solid var(--border);
		border-radius: 999px;
		font-size: 0.85rem;
		text-decoration: none;
		color: inherit;
		background: var(--surface, transparent);
		transition: background-color 0.12s ease, border-color 0.12s ease;
		max-width: 28rem;
	}
	.video-chip:hover {
		background: var(--surface-hover, rgba(0, 0, 0, 0.04));
		border-color: var(--text-muted, #999);
	}
	.yt-logo {
		width: 1.1rem;
		height: 1.1rem;
		color: #ff0000;
		flex-shrink: 0;
	}
	.video-title {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.video-ts {
		font-variant-numeric: tabular-nums;
		color: var(--text-muted, #888);
		font-size: 0.78rem;
	}

	.tags-row {
		margin: 1.2rem 0 0;
		padding-top: 0.75rem;
		border-top: 1px dashed var(--border);
	}

	/* Counter region — soft red rule under the header to match the dir color. */
	.counter .dir-header {
		padding-bottom: 0.4rem;
		border-bottom: 1px solid var(--unresolved-soft);
	}

	/* ===== Outer / peripheral ============================================ */
	.outer {
		padding-top: 1rem;
		border-top: 1px solid var(--border);
	}
	.outer-grid {
		display: grid;
		gap: 2rem;
		grid-template-columns: 1fr 1fr;
	}
	@media (max-width: 1199px) {
		.outer-grid {
			grid-template-columns: 1fr;
		}
	}
	.peripheral-block {
		min-width: 0;
	}
	.peripheral-label {
		font-family: var(--mono);
		font-size: 0.65rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		color: var(--fg-soft);
		margin: 0 0 0.6rem;
		font-weight: 500;
	}
	.peripheral-list {
		list-style: none;
		margin: 0;
		padding: 0;
		display: flex;
		flex-wrap: wrap;
		gap: 0.35rem 0.6rem;
	}
	.peripheral-list li {
		font-size: 0.85rem;
		padding: 0;
		border: none;
		display: inline-flex;
		align-items: baseline;
		gap: 0.25rem;
	}
	.peripheral-list .edge-type {
		margin-left: 0;
	}

	/* ===== Misc ========================================================== */
	.ref-link {
		color: var(--accent);
		text-decoration: none;
		border-bottom: 1px dashed var(--accent);
		white-space: nowrap;
	}
	.ref-link:hover {
		border-bottom-style: solid;
	}
</style>
