<script lang="ts">
	import type { PageProps } from './$types';
	let { data }: PageProps = $props();

	function alpha(c: string): string {
		const k = c[0]?.toUpperCase() ?? '';
		return /[A-Z]/.test(k) ? k : '#';
	}

	const grouped = $derived.by(() => {
		const buckets: Record<string, typeof data.nodes> = {};
		for (const n of data.nodes) {
			const k = alpha(n.name);
			(buckets[k] ??= []).push(n);
		}
		return Object.entries(buckets).sort(([a], [b]) => {
			if (a === '#') return 1;
			if (b === '#') return -1;
			return a.localeCompare(b);
		});
	});

	const letters = $derived(grouped.map(([k]) => k));
</script>

<svelte:head>
	<title>Index — Bible Semantic Graph</title>
</svelte:head>

<div class="page">
	<header class="page-head">
		<div class="eyebrow">
			<a href="/">← Frontispiece</a>
		</div>
		<h1>The Index</h1>
		<p class="lede">
			Every node, alphabetical &middot; <strong>{data.nodes.length.toLocaleString()}</strong>
			entries in total.
		</p>
	</header>

	{#if data.dbMissing}
		<div class="notice">{data.dbMissing}</div>
	{/if}

	{#if letters.length > 0}
		<nav class="letter-nav" aria-label="Jump to letter">
			{#each letters as l (l)}
				<a href="#L-{l}">{l}</a>
			{/each}
		</nav>
	{/if}

	<div class="index">
		{#each grouped as [letter, entries] (letter)}
			<section class="index-group" id="L-{letter}">
				<h2 class="index-letter">{letter}</h2>
				<ul class="index-list">
					{#each entries as n (n.slug)}
						<li>
							<a href="/n/{n.slug}">{n.name}</a>
							<span class="type-pill" data-type={n.type}>{n.type}</span>
						</li>
					{/each}
				</ul>
			</section>
		{/each}
	</div>
</div>

<style>
	.page {
		--display: 'Fraunces', 'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, serif;
		--ink: #1a1a1a;
		--ink-soft: #6b665d;
		--ink-faint: #a8a294;
		--rule: #d8cfba;
		--accent: #5b3a99;
		--gold: #a8842c;
	}

	.page-head {
		padding: 1.5rem 0 2rem;
		border-bottom: 1px solid var(--rule);
		margin-bottom: 2rem;
	}

	.eyebrow {
		font-family: var(--mono);
		font-size: 0.72rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		color: var(--ink-soft);
		margin-bottom: 0.85rem;
	}

	.eyebrow a {
		color: var(--ink-soft);
		text-decoration: none;
	}

	.eyebrow a:hover {
		color: var(--accent);
		text-decoration: underline;
	}

	.page-head h1 {
		font-family: var(--display);
		font-variation-settings: 'opsz' 144, 'SOFT' 30, 'wght' 420;
		font-size: clamp(2.2rem, 5vw, 3.4rem);
		line-height: 1;
		margin: 0 0 0.5rem;
		letter-spacing: -0.015em;
	}

	.lede {
		font-family: 'Iowan Old Style', Palatino, Georgia, serif;
		color: var(--ink-soft);
		font-size: 1rem;
		margin: 0;
	}

	.lede strong {
		color: var(--ink);
		font-weight: 600;
		font-variant-numeric: lining-nums tabular-nums;
	}

	.letter-nav {
		display: flex;
		flex-wrap: wrap;
		gap: 0.2rem 0.4rem;
		padding: 0.85rem 1rem;
		margin: 0 0 2rem;
		border: 1px solid var(--rule);
		background: #fff;
		border-radius: 4px;
		position: sticky;
		top: 0;
		z-index: 5;
	}

	.letter-nav a {
		font-family: var(--display);
		font-variation-settings: 'opsz' 24, 'wght' 500;
		font-size: 1rem;
		min-width: 1.6rem;
		text-align: center;
		padding: 0.15rem 0.35rem;
		color: var(--ink);
		text-decoration: none;
		border-radius: 3px;
		font-variant-numeric: lining-nums;
	}

	.letter-nav a:hover {
		background: var(--accent);
		color: #fff;
		text-decoration: none;
	}

	.index {
		column-count: 3;
		column-gap: 2.4rem;
		column-rule: 1px solid var(--rule);
	}

	@media (min-width: 1200px) {
		.index {
			column-count: 4;
		}
	}

	@media (max-width: 760px) {
		.index {
			column-count: 1;
		}
	}

	.index-group {
		break-inside: avoid;
		margin-bottom: 1.5rem;
		scroll-margin-top: 4rem;
	}

	.index-letter {
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

	.index-list {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.index-list li {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 0.55rem;
		padding: 0.32rem 0;
		border-bottom: 1px dotted var(--rule);
	}

	.index-list li:last-child {
		border-bottom: none;
	}

	.index-list a {
		color: var(--ink);
		text-decoration: none;
		font-size: 0.95rem;
		line-height: 1.3;
	}

	.index-list a:hover {
		color: var(--accent);
		text-decoration: underline;
		text-decoration-thickness: 1px;
		text-underline-offset: 2px;
	}

	.type-pill {
		flex-shrink: 0;
		font-size: 0.6rem;
	}

	.type-pill[data-type='Person'] { background: #e9eefc; color: #2c4ea3; }
	.type-pill[data-type='Place'] { background: #eef5e1; color: #4a6f17; }
	.type-pill[data-type='Text'] { background: #fcf5e0; color: #8a6a1d; }
	.type-pill[data-type='Manuscript'] { background: #f3e9fc; color: #6b2ca3; }
	.type-pill[data-type='Argument'] { background: #fce9e6; color: #a3372c; }
	.type-pill[data-type='Event'] { background: #e1eef5; color: #1d6a8a; }
	.type-pill[data-type='Council'] { background: #fce5f3; color: #8a1d6a; }
	.type-pill[data-type='Deity'] { background: #faf0d4; color: #a8842c; }
	.type-pill[data-type='Mythological'] { background: #ece9e2; color: #5b554a; }
</style>
