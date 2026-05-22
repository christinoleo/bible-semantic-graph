<script lang="ts">
	import type { PageProps } from './$types';
	import StratifiedIndex from '$lib/StratifiedIndex.svelte';
	import { TYPE_GLYPHS, TYPE_NOTES, TYPE_ACCENT } from '$lib/typeMeta';

	let { data }: PageProps = $props();

	const glyph = $derived(TYPE_GLYPHS[data.type] ?? '◇');
	const subtitle = $derived(TYPE_NOTES[data.type] ?? '');
	const accent = $derived(TYPE_ACCENT[data.type] ?? '#5b3a99');
</script>

<svelte:head>
	<title>{data.type} — Bible Semantic Graph</title>
</svelte:head>

<StratifiedIndex
	title={data.type}
	eyebrow="Type · Form"
	{subtitle}
	{accent}
	{glyph}
	nodes={data.nodes}
	showTypeOnRow={false}
/>
