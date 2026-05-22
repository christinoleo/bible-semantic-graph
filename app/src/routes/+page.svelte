<script lang="ts">
	import type { PageProps } from './$types';
	let { data }: PageProps = $props();

	const TYPE_GLYPHS: Record<string, string> = {
		Concept: '✦',
		Argument: '⚖',
		Theory: '❋',
		Event: '✸',
		Person: '☖',
		Place: '⌖',
		Text: '⌬',
		Manuscript: '✎',
		Council: '⌘',
		Deity: '☉',
		Mythological: '☽'
	};

	const TYPE_NOTES: Record<string, string> = {
		Concept: 'Ideas and categories',
		Argument: 'Positions and proofs',
		Theory: 'Systems and schools',
		Event: 'Moments in history',
		Person: 'Figures and authors',
		Place: 'Locales and sites',
		Text: 'Books and writings',
		Manuscript: 'Codices and witnesses',
		Council: 'Synods and decrees',
		Deity: 'Divine names',
		Mythological: 'Figures of legend'
	};

	const AXIS_GLOSS: Record<string, string> = {
		stance: 'For or against',
		tradition: 'Intellectual lineage',
		method: 'Mode of reasoning',
		subject: 'Doctrinal field'
	};

	const roman = ['Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ', 'Ⅴ', 'Ⅵ', 'Ⅶ', 'Ⅷ', 'Ⅸ', 'Ⅹ', 'Ⅺ', 'Ⅻ'];
</script>

<svelte:head>
	<title>Bible Semantic Graph</title>
	<meta
		name="description"
		content="A personal cartography of Scripture, doctrine, and disputation — a graph of {data.total} nodes connected by {data.edges} edges."
	/>
</svelte:head>

<div class="home">
	<!-- ╔══ FRONTISPIECE ══════════════════════════════════════════════ ╗ -->
	<section class="frontispiece">
		<div class="frontispiece-grid">
			<aside class="marginalia left">
				<div class="folio">FOLIO · I</div>
				<div class="fleuron" aria-hidden="true">❦</div>
				<div class="marg-note">
					<em>Apparatus criticus</em><br />
					of a personal canon —<br />
					begun anno&nbsp;MMXXIV
				</div>
			</aside>

			<div class="title-block">
				<div class="eyebrow">An evolving cartography of</div>
				<h1 class="title">
					<span class="title-bible">Bible</span>
					<span class="title-amp" aria-hidden="true">·</span>
					<span class="title-semantic"><em>Semantic</em></span>
					<span class="title-graph">Graph</span>
				</h1>
				<p class="subtitle">
					Scripture &middot; Doctrine &middot; <em>Disputatio</em>
				</p>

				<div class="rule-double"></div>

				<p class="lede">
					<span class="dropcap">A</span>n entry here is a <em>label</em>, not a treatise — the
					substance lives in the connections between it and its neighbours. Each node is small by
					design; the graph carries the structure. Wander by <a href="#types">form</a>, by
					<a href="#axes">argumentation</a>, by <a href="/search">name</a>, or by following any
					link until the next one tugs harder.
				</p>
			</div>

			<aside class="marginalia right">
				<dl class="meter">
					<div>
						<dt>nodes</dt>
						<dd>{data.total.toLocaleString()}</dd>
					</div>
					<div>
						<dt>edges</dt>
						<dd>{data.edges.toLocaleString()}</dd>
					</div>
					<div>
						<dt>forms</dt>
						<dd>{data.byType.length}</dd>
					</div>
					<div>
						<dt>axes</dt>
						<dd>4</dd>
					</div>
				</dl>
			</aside>
		</div>
	</section>

	{#if data.dbMissing}
		<div class="notice">{data.dbMissing}</div>
	{/if}

	<!-- ╔══ I. FORMS ═════════════════════════════════════════════════ ╗ -->
	{#if data.byType.length > 0}
		<section id="types" class="section">
			<header class="section-head">
				<span class="num">{roman[0]}</span>
				<h2>The Forms</h2>
				<span class="dash" aria-hidden="true"></span>
				<span class="hint">eleven categories, one filename each</span>
			</header>

			<ul class="type-grid">
				{#each data.byType as { type, count } (type)}
					<li>
						<a class="type-card" href="/type/{type}" data-type={type}>
							<span class="glyph" aria-hidden="true">{TYPE_GLYPHS[type] ?? '◇'}</span>
							<span class="type-name">{type}</span>
							<span class="type-note">{TYPE_NOTES[type] ?? ''}</span>
							<span class="type-count">{count}</span>
						</a>
					</li>
				{/each}
			</ul>
		</section>
	{/if}

	<!-- ╔══ II. ARGUMENTATION ═══════════════════════════════════════ ╗ -->
	{#if data.axes.length > 0 && data.axes.some((a) => a.values.length > 0)}
		<section id="axes" class="section">
			<header class="section-head">
				<span class="num">{roman[1]}</span>
				<h2>The Argumentation</h2>
				<span class="dash" aria-hidden="true"></span>
				<span class="hint">
					<a href="/axis">four axes</a> by which any argument is classified
				</span>
			</header>

			<div class="axes-grid">
				{#each data.axes as { axis, values, total } (axis)}
					<article class="axis-panel" data-axis={axis}>
						<header>
							<span class="axis-label" data-axis={axis}>{axis}</span>
							<span class="axis-gloss">{AXIS_GLOSS[axis]}</span>
						</header>
						{#if values.length === 0}
							<p class="axis-empty">No values yet.</p>
						{:else}
							<ul class="axis-values">
								{#each values as { value, count } (value)}
									<li>
										<a class="axis-pill" data-axis={axis} href="/axis/{axis}/{value}">
											{value}
										</a>
										<span class="axis-count">{count}</span>
									</li>
								{/each}
							</ul>
							{#if total > values.length}
								<a class="axis-more" href="/axis">
									{total - values.length} more →
								</a>
							{/if}
						{/if}
					</article>
				{/each}
			</div>
		</section>
	{/if}

	<!-- ╔══ III. MOST CONNECTED ═════════════════════════════════════ ╗ -->
	{#if data.featured.length > 0}
		<section class="section">
			<header class="section-head">
				<span class="num">{roman[2]}</span>
				<h2>The Anchors</h2>
				<span class="dash" aria-hidden="true"></span>
				<span class="hint">most connected — start anywhere, but these pull harder</span>
			</header>

			<ol class="featured">
				{#each data.featured as n, i (n.slug)}
					<li>
						<span class="featured-rank">{String(i + 1).padStart(2, '0')}</span>
						<div class="featured-body">
							<a class="featured-name" href="/n/{n.slug}">{n.name}</a>
							<span class="featured-meta">
								<span class="type-pill" data-type={n.type}>{n.type}</span>
								<span class="featured-degree">
									{n.degree} edge{n.degree === 1 ? '' : 's'}
								</span>
							</span>
						</div>
					</li>
				{/each}
			</ol>
		</section>
	{/if}

	<!-- ╔══ IV. EXPLICIT ════════════════════════════════════════════ ╗ -->
	{#if data.total > 0}
		<section class="section colophon-section">
			<div class="colophon">
				<div class="colophon-rule" aria-hidden="true"></div>
				<p class="colophon-line">
					<span class="ornament" aria-hidden="true">❦</span>
					<span>or read the <a href="/all">full index of {data.total.toLocaleString()} entries</a></span>
					<span class="dot" aria-hidden="true">·</span>
					<span><a href="/axis">browse the four axes</a></span>
					<span class="dot" aria-hidden="true">·</span>
					<span><a href="/search">search by name or text</a></span>
				</p>
			</div>
		</section>
	{/if}
</div>

<style>
	/* Widen the page container only when the home is rendered. */
	:global(main:has(.home)) {
		max-width: 1280px;
	}

	/* Match the header bar's max-width to the widened home content so the
	   sticky bar stays aligned with what's below it. */
	:global(body:has(.home) header .bar) {
		max-width: 1280px;
	}

	/* ── Home-only typography ─────────────────────────────────────── */
	.home {
		--display: 'Fraunces', 'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, serif;
		--ink: #1a1a1a;
		--ink-soft: #6b665d;
		--ink-faint: #a8a294;
		--paper: #fafaf7;
		--paper-warm: #f3eee2;
		--rule: #d8cfba;
		--rule-strong: #1a1a1a;
		--accent: #5b3a99;
		--gold: #a8842c;
		--vermillion: #a3372c;

		margin: -2rem -1.25rem 0;
		padding: 0 1.25rem;
	}

	/* ── FRONTISPIECE ─────────────────────────────────────────────── */
	.frontispiece {
		position: relative;
		padding: 4rem 0 2.5rem;
		border-bottom: 1px solid var(--rule);
		background:
			radial-gradient(
				ellipse 60% 80% at 100% 0%,
				rgba(168, 132, 44, 0.08),
				transparent 60%
			),
			radial-gradient(
				ellipse 40% 60% at 0% 100%,
				rgba(91, 58, 153, 0.06),
				transparent 60%
			);
	}

	.frontispiece-grid {
		display: grid;
		grid-template-columns: minmax(140px, 1fr) minmax(0, 3.4fr) minmax(140px, 1fr);
		gap: 2rem;
		align-items: start;
	}

	.title-block {
		text-align: center;
		min-width: 0;
	}

	.eyebrow {
		font-family: var(--mono);
		font-size: 0.72rem;
		letter-spacing: 0.22em;
		text-transform: uppercase;
		color: var(--ink-soft);
		margin-bottom: 1.25rem;
	}

	.title {
		font-family: var(--display);
		font-variation-settings: 'opsz' 144, 'SOFT' 30, 'wght' 460;
		font-weight: 460;
		font-size: clamp(2.6rem, 7.5vw, 5.4rem);
		line-height: 0.96;
		letter-spacing: -0.02em;
		margin: 0 0 0.5rem;
		color: var(--ink);
	}

	.title-semantic em {
		font-style: italic;
		font-variation-settings: 'opsz' 144, 'SOFT' 100, 'wght' 360;
		color: var(--accent);
		letter-spacing: -0.025em;
	}

	.title-amp {
		display: inline-block;
		color: var(--gold);
		font-weight: 300;
		margin: 0 0.15em;
		transform: translateY(-0.15em);
	}

	.subtitle {
		font-family: var(--display);
		font-variation-settings: 'opsz' 24, 'wght' 360;
		font-size: clamp(1rem, 1.4vw, 1.25rem);
		color: var(--ink-soft);
		font-style: normal;
		letter-spacing: 0.04em;
		margin: 0 0 1.75rem;
	}

	.subtitle em {
		color: var(--ink);
		font-style: italic;
	}

	.rule-double {
		width: min(420px, 60%);
		height: 5px;
		margin: 0 auto 2rem;
		border-top: 1px solid var(--rule-strong);
		border-bottom: 1px solid var(--rule-strong);
	}

	.lede {
		font-family: 'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, serif;
		font-size: 1.05rem;
		line-height: 1.65;
		max-width: 56ch;
		margin: 0 auto;
		text-align: left;
		color: var(--ink);
	}

	.lede :global(a) {
		color: var(--accent);
		text-decoration: underline;
		text-decoration-thickness: 1px;
		text-underline-offset: 3px;
		text-decoration-color: rgba(91, 58, 153, 0.35);
	}

	.lede :global(a:hover) {
		text-decoration-color: var(--accent);
	}

	.dropcap {
		font-family: var(--display);
		font-variation-settings: 'opsz' 144, 'SOFT' 60, 'wght' 700;
		float: left;
		font-size: 4.2rem;
		line-height: 0.85;
		padding: 0.35rem 0.55rem 0 0;
		color: var(--accent);
	}

	/* ── Marginalia ── */
	.marginalia {
		font-family: var(--mono);
		font-size: 0.72rem;
		color: var(--ink-soft);
		line-height: 1.55;
	}

	.marginalia.left {
		text-align: right;
		padding-top: 0.4rem;
	}

	.marginalia.right {
		text-align: left;
		padding-top: 0.4rem;
	}

	.folio {
		font-size: 0.65rem;
		letter-spacing: 0.25em;
		color: var(--ink-faint);
		text-transform: uppercase;
		margin-bottom: 0.6rem;
	}

	.fleuron {
		font-family: var(--display);
		font-size: 2.2rem;
		color: var(--gold);
		line-height: 1;
		margin-bottom: 0.6rem;
	}

	.marg-note {
		font-family: var(--display);
		font-variation-settings: 'opsz' 14, 'wght' 380;
		font-size: 0.82rem;
		font-style: normal;
		color: var(--ink-soft);
		line-height: 1.5;
	}

	.marg-note em {
		color: var(--ink);
	}

	.meter {
		display: grid;
		grid-template-columns: 1fr;
		gap: 0.6rem;
		margin: 0;
	}

	.meter > div {
		display: flex;
		align-items: baseline;
		gap: 0.55rem;
		border-bottom: 1px dotted var(--rule);
		padding-bottom: 0.45rem;
	}

	.meter > div:last-child {
		border-bottom: none;
	}

	.meter dt {
		font-family: var(--mono);
		font-size: 0.65rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		color: var(--ink-faint);
		min-width: 3.2rem;
	}

	.meter dd {
		font-family: var(--display);
		font-variation-settings: 'opsz' 72, 'wght' 480;
		font-size: 1.6rem;
		line-height: 1;
		margin: 0;
		color: var(--ink);
		font-variant-numeric: lining-nums tabular-nums;
	}

	/* ── Section heads ────────────────────────────────────────────── */
	.section {
		padding: 3.5rem 0 1rem;
	}

	.section-head {
		display: flex;
		align-items: baseline;
		gap: 1rem;
		margin: 0 0 1.75rem;
	}

	.section-head .num {
		font-family: var(--display);
		font-variation-settings: 'opsz' 144, 'wght' 360;
		font-size: 2.4rem;
		line-height: 1;
		color: var(--gold);
		letter-spacing: -0.02em;
	}

	.section-head h2 {
		font-family: var(--display);
		font-variation-settings: 'opsz' 96, 'SOFT' 20, 'wght' 420;
		font-size: clamp(1.6rem, 2.6vw, 2.1rem);
		font-weight: 420;
		margin: 0;
		border: none;
		padding: 0;
		letter-spacing: -0.01em;
	}

	.section-head .dash {
		flex: 1;
		height: 1px;
		background: var(--rule);
		transform: translateY(-0.4rem);
	}

	.section-head .hint {
		font-family: var(--mono);
		font-size: 0.7rem;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--ink-faint);
		white-space: nowrap;
	}

	.section-head .hint :global(a) {
		color: var(--ink-soft);
		text-decoration: underline;
		text-decoration-color: var(--rule);
		text-underline-offset: 3px;
	}

	.section-head .hint :global(a:hover) {
		color: var(--accent);
		text-decoration-color: var(--accent);
	}

	/* ── Type grid ────────────────────────────────────────────────── */
	.type-grid {
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
		gap: 1px;
		background: var(--rule);
		border: 1px solid var(--rule);
	}

	.type-grid li {
		background: var(--paper);
	}

	.type-card {
		display: grid;
		grid-template-columns: auto 1fr auto;
		grid-template-rows: auto auto;
		grid-template-areas:
			'glyph name count'
			'glyph note count';
		column-gap: 0.85rem;
		row-gap: 0.1rem;
		padding: 1rem 1rem;
		color: var(--ink);
		text-decoration: none;
		transition: background 160ms ease;
		position: relative;
	}

	.type-card:hover {
		background: var(--paper-warm);
		text-decoration: none;
	}

	.type-card .glyph {
		grid-area: glyph;
		font-family: var(--display);
		font-variation-settings: 'opsz' 72, 'wght' 380;
		font-size: 1.7rem;
		line-height: 1;
		align-self: center;
		color: var(--accent);
	}

	.type-card[data-type='Person'] .glyph { color: #2c4ea3; }
	.type-card[data-type='Place'] .glyph { color: #5d8a1d; }
	.type-card[data-type='Text'] .glyph { color: #8a6a1d; }
	.type-card[data-type='Manuscript'] .glyph { color: #6b2ca3; }
	.type-card[data-type='Argument'] .glyph { color: var(--vermillion); }
	.type-card[data-type='Event'] .glyph { color: #1d6a8a; }
	.type-card[data-type='Council'] .glyph { color: #8a1d6a; }
	.type-card[data-type='Deity'] .glyph { color: var(--gold); }
	.type-card[data-type='Mythological'] .glyph { color: #6b665d; }

	.type-card .type-name {
		grid-area: name;
		font-family: var(--display);
		font-variation-settings: 'opsz' 24, 'wght' 480;
		font-size: 1.1rem;
		letter-spacing: -0.005em;
		line-height: 1.1;
	}

	.type-card .type-note {
		grid-area: note;
		font-family: var(--mono);
		font-size: 0.66rem;
		letter-spacing: 0.04em;
		color: var(--ink-faint);
		text-transform: uppercase;
	}

	.type-card .type-count {
		grid-area: count;
		font-family: var(--display);
		font-variation-settings: 'opsz' 72, 'wght' 320;
		font-size: 1.6rem;
		color: var(--ink-soft);
		align-self: center;
		font-variant-numeric: lining-nums tabular-nums;
	}

	/* ── Axes grid ────────────────────────────────────────────────── */
	.axes-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
		gap: 1rem;
	}

	.axis-panel {
		border: 1px solid var(--rule);
		background: var(--paper);
		padding: 1rem 1.1rem 1.2rem;
		border-top: 3px solid var(--ink);
	}

	.axis-panel[data-axis='stance'] { border-top-color: #a3372c; }
	.axis-panel[data-axis='tradition'] { border-top-color: #2c4ea3; }
	.axis-panel[data-axis='method'] { border-top-color: #6b2ca3; }
	.axis-panel[data-axis='subject'] { border-top-color: #8a6a1d; }

	.axis-panel header {
		background: none;
		position: static;
		border: none;
		padding: 0;
		margin-bottom: 0.85rem;
	}

	.axis-label {
		display: block;
		font-family: var(--display);
		font-variation-settings: 'opsz' 36, 'wght' 500, 'SOFT' 30;
		font-size: 1.15rem;
		text-transform: capitalize;
		color: var(--ink);
		line-height: 1;
		margin-bottom: 0.3rem;
	}

	.axis-panel[data-axis='stance'] .axis-label { color: #a3372c; }
	.axis-panel[data-axis='tradition'] .axis-label { color: #2c4ea3; }
	.axis-panel[data-axis='method'] .axis-label { color: #6b2ca3; }
	.axis-panel[data-axis='subject'] .axis-label { color: #8a6a1d; }

	.axis-gloss {
		font-family: var(--mono);
		font-size: 0.65rem;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--ink-faint);
	}

	.axis-values {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
	}

	.axis-values li {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 0.5rem;
	}

	.axis-pill {
		font-family: 'Iowan Old Style', Palatino, Georgia, serif;
		font-size: 0.9rem;
		padding: 0.05rem 0.45rem;
		border-radius: 3px;
		text-decoration: none;
		color: var(--ink);
		background: transparent;
	}

	.axis-panel[data-axis='stance'] .axis-pill { background: #fce9e6; color: #a3372c; }
	.axis-panel[data-axis='tradition'] .axis-pill { background: #e9eefc; color: #2c4ea3; }
	.axis-panel[data-axis='method'] .axis-pill { background: #f3e9fc; color: #6b2ca3; }
	.axis-panel[data-axis='subject'] .axis-pill { background: #fcf5e0; color: #8a6a1d; }

	.axis-pill:hover {
		filter: brightness(0.94);
		text-decoration: none;
	}

	.axis-count {
		font-family: var(--mono);
		font-size: 0.7rem;
		color: var(--ink-faint);
		font-variant-numeric: tabular-nums;
	}

	.axis-more {
		display: inline-block;
		margin-top: 0.85rem;
		font-family: var(--mono);
		font-size: 0.7rem;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--ink-soft);
		text-decoration: none;
	}

	.axis-more:hover {
		color: var(--accent);
		text-decoration: underline;
	}

	.axis-empty {
		font-family: var(--mono);
		font-size: 0.75rem;
		color: var(--ink-faint);
		font-style: italic;
		margin: 0;
	}

	/* ── Featured / anchors ───────────────────────────────────────── */
	.featured {
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
		gap: 0;
	}

	.featured li {
		display: grid;
		grid-template-columns: auto 1fr;
		gap: 0.9rem;
		align-items: baseline;
		padding: 0.85rem 0.9rem;
		border-bottom: 1px solid var(--rule);
		border-right: 1px solid var(--rule);
	}

	.featured-rank {
		font-family: var(--mono);
		font-size: 0.7rem;
		color: var(--ink-faint);
		font-variant-numeric: tabular-nums;
		letter-spacing: 0.06em;
	}

	.featured-body {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		min-width: 0;
	}

	.featured-name {
		font-family: var(--display);
		font-variation-settings: 'opsz' 24, 'wght' 460;
		font-size: 1.02rem;
		color: var(--ink);
		text-decoration: none;
		line-height: 1.25;
	}

	.featured-name:hover {
		color: var(--accent);
		text-decoration: underline;
		text-decoration-thickness: 1px;
		text-underline-offset: 3px;
	}

	.featured-meta {
		display: flex;
		align-items: center;
		gap: 0.55rem;
	}

	.featured-degree {
		font-family: var(--mono);
		font-size: 0.66rem;
		color: var(--ink-faint);
		letter-spacing: 0.06em;
		text-transform: uppercase;
	}

	/* ── Type-pill recoloring (used in featured + index) ─────────── */
	.type-pill[data-type='Person'] { background: #e9eefc; color: #2c4ea3; }
	.type-pill[data-type='Place'] { background: #eef5e1; color: #4a6f17; }
	.type-pill[data-type='Text'] { background: #fcf5e0; color: #8a6a1d; }
	.type-pill[data-type='Manuscript'] { background: #f3e9fc; color: #6b2ca3; }
	.type-pill[data-type='Argument'] { background: #fce9e6; color: #a3372c; }
	.type-pill[data-type='Event'] { background: #e1eef5; color: #1d6a8a; }
	.type-pill[data-type='Council'] { background: #fce5f3; color: #8a1d6a; }
	.type-pill[data-type='Deity'] { background: #faf0d4; color: #a8842c; }
	.type-pill[data-type='Mythological'] { background: #ece9e2; color: #5b554a; }

	/* ── Colophon ─────────────────────────────────────────────────── */
	.colophon-section {
		padding-top: 3rem;
	}

	.colophon {
		text-align: center;
		padding: 2.5rem 0 0.5rem;
	}

	.colophon-rule {
		width: 5rem;
		height: 1px;
		background: var(--rule);
		margin: 0 auto 1.5rem;
		position: relative;
	}

	.colophon-rule::before,
	.colophon-rule::after {
		content: '';
		position: absolute;
		top: 50%;
		width: 3px;
		height: 3px;
		background: var(--gold);
		border-radius: 50%;
		transform: translateY(-50%);
	}

	.colophon-rule::before { left: -8px; }
	.colophon-rule::after { right: -8px; }

	.colophon-line {
		font-family: var(--display);
		font-variation-settings: 'opsz' 18, 'wght' 380;
		font-size: 1rem;
		color: var(--ink-soft);
		margin: 0;
		line-height: 1.7;
		display: inline-flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.5rem 0.75rem;
		max-width: 60ch;
	}

	.colophon-line a {
		color: var(--ink);
		text-decoration: underline;
		text-decoration-color: rgba(91, 58, 153, 0.35);
		text-underline-offset: 3px;
		text-decoration-thickness: 1px;
	}

	.colophon-line a:hover {
		color: var(--accent);
		text-decoration-color: var(--accent);
	}

	.colophon-line .ornament {
		color: var(--gold);
		font-size: 1.15rem;
		font-style: italic;
	}

	.colophon-line .dot {
		color: var(--ink-faint);
	}

	/* ── Responsive ───────────────────────────────────────────────── */
	@media (max-width: 900px) {
		.frontispiece-grid {
			grid-template-columns: 1fr;
			gap: 2rem;
		}
		.marginalia.left,
		.marginalia.right {
			text-align: left;
		}
		.marginalia.right {
			border-top: 1px solid var(--rule);
			padding-top: 1.2rem;
		}
		.meter {
			grid-template-columns: repeat(2, 1fr);
			gap: 0.8rem 1.5rem;
		}
		.meter > div {
			border-bottom: 1px dotted var(--rule);
		}
		.fleuron {
			display: none;
		}
	}

	@media (max-width: 560px) {
		.section-head .hint {
			display: none;
		}
		.frontispiece {
			padding: 2.5rem 0 1.5rem;
		}
	}
</style>
