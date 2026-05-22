<script lang="ts">
	import type { PageProps } from './$types';
	import StratifiedIndex from '$lib/StratifiedIndex.svelte';

	let { data }: PageProps = $props();
</script>

<svelte:head>
	<title>#{data.tag} — Bible Semantic Graph</title>
</svelte:head>

<StratifiedIndex
	title="#{data.tag}"
	eyebrow="Tag"
	subtitle="Every node carrying this tag"
	accent="#5b3a99"
	glyph="#"
	nodes={data.nodes}
	showTypeOnRow={true}
/>
