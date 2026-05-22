<script lang="ts">
	import type { PageProps } from './$types';
	let { data }: PageProps = $props();

	const AXIS_DESCRIPTIONS: Record<string, string> = {
		stance: 'For/against — what side the argument takes',
		tradition: 'Intellectual lineage that owns / advances the argument',
		method: 'How the argument reasons',
		subject: 'What the argument is about doctrinally'
	};
</script>

<svelte:head>
	<title>Argumentation axes — Bible Semantic Graph</title>
</svelte:head>

<h1>Argumentation axes</h1>
<p class="meta">
	Every <code>type: Argument</code> Node is classified along four axes. Click a value to see every Argument sharing that classification.
</p>

{#if data.dbMissing}
	<div class="notice">{data.dbMissing}</div>
{/if}

{#each data.axes as { axis, values } (axis)}
	<section class="axis-section">
		<h2>
			<span class="axis-name" data-axis={axis}>{axis}</span>
			<span class="section-hint">{AXIS_DESCRIPTIONS[axis]}</span>
		</h2>
		{#if values.length === 0}
			<p class="meta">No values yet.</p>
		{:else}
			<ul class="value-list">
				{#each values as { value, count } (value)}
					<li>
						<a href="/axis/{axis}/{value}" class="axis-pill" data-axis={axis}>{value}</a>
						<span class="meta">— {count}</span>
					</li>
				{/each}
			</ul>
		{/if}
	</section>
{/each}

<style>
	.axis-section {
		margin: 1.5rem 0;
	}
	.axis-name {
		font-family: var(--mono);
		font-size: 1rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		padding: 0.1rem 0.55rem;
		border-radius: 5px;
	}
	.axis-name[data-axis='stance']    { background: #fce9e6; color: #a3372c; }
	.axis-name[data-axis='tradition'] { background: #e9eefc; color: #2c4ea3; }
	.axis-name[data-axis='method']    { background: #f3e9fc; color: #6b2ca3; }
	.axis-name[data-axis='subject']   { background: #fcf5e0; color: #8a6a1d; }
	.section-hint {
		font-size: 0.78rem;
		font-weight: normal;
		color: var(--fg-soft);
		font-family: var(--mono);
		margin-left: 0.5rem;
	}
	.value-list {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem 0.8rem;
	}
	.value-list li {
		display: inline-flex;
		align-items: baseline;
		gap: 0.3rem;
	}
	.axis-pill {
		display: inline-block;
		font-size: 0.85rem;
		padding: 0.1rem 0.55rem;
		border-radius: 4px;
		text-decoration: none;
	}
	.axis-pill[data-axis='stance']    { background: #fce9e6; color: #a3372c; }
	.axis-pill[data-axis='tradition'] { background: #e9eefc; color: #2c4ea3; }
	.axis-pill[data-axis='method']    { background: #f3e9fc; color: #6b2ca3; }
	.axis-pill[data-axis='subject']   { background: #fcf5e0; color: #8a6a1d; }
	.axis-pill:hover { text-decoration: underline; }
</style>
