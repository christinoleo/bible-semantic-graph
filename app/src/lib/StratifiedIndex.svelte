<script lang="ts">
	import type { NodeSummary } from '$lib/types';

	type Entry = NodeSummary & { degree: number };

	type Props = {
		title: string;
		eyebrow?: string;
		subtitle?: string;
		accent?: string;
		glyph?: string;
		nodes: Entry[];
		showTypeOnRow?: boolean;
		featuredCount?: number;
	};

	let {
		title,
		eyebrow = '',
		subtitle = '',
		accent = '#5b3a99',
		glyph = '◇',
		nodes,
		showTypeOnRow = false,
		featuredCount = 5
	}: Props = $props();

	let filter = $state('');

	const sortedByDegree = $derived(
		[...nodes].sort((a, b) =>
			b.degree - a.degree || a.name.localeCompare(b.name)
		)
	);

	const featured = $derived(
		sortedByDegree.filter((n) => n.degree > 0).slice(0, featuredCount)
	);

	const sortedByName = $derived(
		[...nodes].sort((a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: 'base' }))
	);

	function alpha(c: string): string {
		const k = c[0]?.toUpperCase() ?? '';
		return /[A-Z]/.test(k) ? k : '#';
	}

	function matches(n: Entry, q: string): boolean {
		if (!q) return true;
		return n.name.toLowerCase().includes(q.toLowerCase());
	}

	const filtered = $derived(sortedByName.filter((n) => matches(n, filter)));

	const grouped = $derived.by(() => {
		const buckets: Record<string, Entry[]> = {};
		for (const n of filtered) {
			const k = alpha(n.name);
			(buckets[k] ??= []).push(n);
		}
		return Object.entries(buckets).sort(([a], [b]) => {
			if (a === '#') return 1;
			if (b === '#') return -1;
			return a.localeCompare(b);
		});
	});
</script>

<div class="strat" style="--accent: {accent}">
	<header class="strat-head">
		{#if eyebrow}
			<div class="eyebrow">{eyebrow}</div>
		{/if}
		<div class="title-row">
			<span class="glyph" aria-hidden="true">{glyph}</span>
			<h1 class="title">{title}</h1>
		</div>
		{#if subtitle}
			<p class="subtitle">{subtitle}</p>
		{/if}
		<div class="meter">
			<span><strong>{nodes.length.toLocaleString()}</strong> entries</span>
			{#if featured.length > 0}
				<span class="dot">·</span>
				<span>
					most connected:
					<a class="meter-link" href="/n/{featured[0].slug}">{featured[0].name}</a>
					<span class="meter-degree">{featured[0].degree}</span>
				</span>
			{/if}
		</div>
	</header>

	{#if featured.length > 0}
		<section class="featured-block">
			<div class="featured-label">Most central</div>
			<ol class="featured-list">
				{#each featured as n, i (n.slug)}
					<li>
						<span class="featured-rank">{String(i + 1).padStart(2, '0')}</span>
						<a class="featured-name" href="/n/{n.slug}">{n.name}</a>
						{#if showTypeOnRow}
							<span class="type-pill" data-type={n.type}>{n.type}</span>
						{/if}
						<span class="featured-degree" title="edge count">{n.degree}</span>
					</li>
				{/each}
			</ol>
		</section>
	{/if}

	{#if nodes.length > featuredCount}
		<div class="filter-bar">
			<input
				type="search"
				bind:value={filter}
				placeholder="Filter {nodes.length.toLocaleString()} entries by name…"
				autocomplete="off"
				aria-label="Filter entries by name"
			/>
			{#if filter}
				<span class="filter-count">
					{filtered.length} / {nodes.length}
				</span>
				<button type="button" class="filter-clear" onclick={() => (filter = '')}>
					clear
				</button>
			{/if}
		</div>
	{/if}

	{#if filtered.length === 0}
		<p class="empty">No entries match <em>“{filter}”</em>.</p>
	{:else}
		<div class="bands">
			{#each grouped as [letter, entries] (letter)}
				<section class="band">
					<h2 class="band-letter">{letter}</h2>
					<ul class="band-list">
						{#each entries as n (n.slug)}
							<li>
								<a class="entry-name" href="/n/{n.slug}">{n.name}</a>
								{#if showTypeOnRow}
									<span class="type-pill" data-type={n.type}>{n.type}</span>
								{/if}
								<span class="entry-degree" title="edge count">
									{n.degree}
								</span>
							</li>
						{/each}
					</ul>
				</section>
			{/each}
		</div>
	{/if}
</div>

<style>
	.strat {
		--display: 'Fraunces', 'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, serif;
		--ink: #1a1a1a;
		--ink-soft: #6b665d;
		--ink-faint: #a8a294;
		--rule: #d8cfba;
		--gold: #a8842c;
		--gutter: 1.25rem;
	}

	.strat-head {
		padding: 3rem var(--gutter) 2.25rem;
		border-bottom: 1px solid var(--rule);
		margin-bottom: 2.25rem;
	}

	.eyebrow {
		font-family: var(--mono);
		font-size: 0.7rem;
		letter-spacing: 0.22em;
		text-transform: uppercase;
		color: var(--ink-faint);
		margin-bottom: 0.6rem;
	}

	.title-row {
		display: flex;
		align-items: baseline;
		gap: 0.85rem;
		margin-bottom: 0.35rem;
	}

	.glyph {
		font-family: var(--display);
		font-variation-settings: 'opsz' 144, 'wght' 360;
		font-size: clamp(2rem, 4vw, 3rem);
		line-height: 1;
		color: var(--accent);
	}

	.title {
		font-family: var(--display);
		font-variation-settings: 'opsz' 144, 'SOFT' 30, 'wght' 420;
		font-size: clamp(2.2rem, 5vw, 3.4rem);
		line-height: 1;
		letter-spacing: -0.015em;
		margin: 0;
		color: var(--ink);
		border: none;
		padding: 0;
	}

	.subtitle {
		font-family: var(--display);
		font-variation-settings: 'opsz' 24, 'wght' 380;
		font-size: 1.05rem;
		color: var(--ink-soft);
		margin: 0 0 0.85rem;
		font-style: italic;
	}

	.meter {
		font-family: var(--mono);
		font-size: 0.78rem;
		color: var(--ink-soft);
		letter-spacing: 0.02em;
		display: inline-flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 0.4rem 0.6rem;
	}

	.meter strong {
		color: var(--ink);
		font-weight: 500;
		font-variant-numeric: lining-nums tabular-nums;
	}

	.meter .dot {
		color: var(--ink-faint);
	}

	.meter-link {
		color: var(--accent);
		text-decoration: underline;
		text-decoration-thickness: 1px;
		text-underline-offset: 3px;
	}

	.meter-degree {
		font-variant-numeric: tabular-nums;
		color: var(--ink-faint);
	}

	/* ── Featured ────────────────────────────────────────────────── */
	.featured-block {
		margin: 0 var(--gutter) 1.5rem;
		padding: 0 0 0 1.25rem;
		border-left: 3px solid var(--accent);
	}

	.featured-label {
		font-family: var(--mono);
		font-size: 0.68rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		color: var(--ink-faint);
		margin-bottom: 0.5rem;
	}

	.featured-list {
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: 0.25rem 1.5rem;
	}

	.featured-list li {
		display: grid;
		grid-template-columns: auto 1fr auto auto;
		align-items: baseline;
		gap: 0.65rem;
		padding: 0.35rem 0;
	}

	.featured-rank {
		font-family: var(--mono);
		font-size: 0.7rem;
		color: var(--ink-faint);
		font-variant-numeric: tabular-nums;
	}

	.featured-name {
		font-family: var(--display);
		font-variation-settings: 'opsz' 24, 'wght' 480;
		font-size: 1.02rem;
		color: var(--ink);
		text-decoration: none;
		line-height: 1.25;
		min-width: 0;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.featured-name:hover {
		color: var(--accent);
		text-decoration: underline;
		text-decoration-thickness: 1px;
		text-underline-offset: 3px;
	}

	.featured-degree {
		font-family: var(--mono);
		font-size: 0.72rem;
		color: var(--accent);
		font-variant-numeric: tabular-nums;
		font-weight: 500;
	}

	/* ── Filter bar ──────────────────────────────────────────────── */
	.filter-bar {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin: 0 var(--gutter) 1.5rem;
		padding: 0.6rem 0.85rem;
		background: #fff;
		border: 1px solid var(--rule);
		border-radius: 4px;
		position: sticky;
		top: 3.5rem;
		z-index: 4;
	}

	.filter-bar input {
		flex: 1;
		font: inherit;
		font-size: 0.95rem;
		font-family: 'Iowan Old Style', Palatino, Georgia, serif;
		border: none;
		background: transparent;
		outline: none;
		color: var(--ink);
		padding: 0.15rem 0;
	}

	.filter-bar input::placeholder {
		color: var(--ink-faint);
		font-style: italic;
	}

	.filter-count {
		font-family: var(--mono);
		font-size: 0.72rem;
		color: var(--ink-faint);
		font-variant-numeric: tabular-nums;
	}

	.filter-clear {
		font-family: var(--mono);
		font-size: 0.65rem;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		background: transparent;
		border: 1px solid var(--rule);
		padding: 0.2rem 0.55rem;
		border-radius: 3px;
		color: var(--ink-soft);
		cursor: pointer;
	}

	.filter-clear:hover {
		background: var(--accent);
		color: #fff;
		border-color: var(--accent);
	}

	.empty {
		font-family: var(--display);
		font-style: italic;
		color: var(--ink-faint);
		text-align: center;
		padding: 3rem var(--gutter);
	}

	.empty em {
		color: var(--ink-soft);
	}

	/* ── Alphabetical bands ──────────────────────────────────────── */
	.bands {
		column-count: 3;
		column-gap: 2.4rem;
		column-rule: 1px solid var(--rule);
		padding: 0 var(--gutter);
	}

	@media (min-width: 1200px) {
		.bands {
			column-count: 4;
		}
	}

	@media (max-width: 760px) {
		.bands {
			column-count: 1;
		}
	}

	.band {
		break-inside: avoid;
		margin-bottom: 1.5rem;
	}

	.band-letter {
		font-family: var(--display);
		font-variation-settings: 'opsz' 144, 'wght' 320, 'SOFT' 60;
		font-size: 2.4rem;
		line-height: 1;
		margin: 0 0 0.3rem;
		color: var(--gold);
		border-bottom: 1px solid var(--rule);
		padding-bottom: 0.3rem;
		letter-spacing: -0.02em;
	}

	.band-list {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.band-list li {
		display: grid;
		grid-template-columns: 1fr auto auto;
		align-items: baseline;
		gap: 0.4rem;
		padding: 0.32rem 0;
		border-bottom: 1px dotted var(--rule);
	}

	.band-list li:last-child {
		border-bottom: none;
	}

	.entry-name {
		color: var(--ink);
		text-decoration: none;
		font-size: 0.95rem;
		line-height: 1.3;
		min-width: 0;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.entry-name:hover {
		color: var(--accent);
		text-decoration: underline;
		text-decoration-thickness: 1px;
		text-underline-offset: 2px;
	}

	.entry-degree {
		font-family: var(--mono);
		font-size: 0.7rem;
		color: var(--ink-faint);
		font-variant-numeric: tabular-nums;
	}

	.band-list :global(.type-pill) {
		font-size: 0.58rem;
	}
</style>
