<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { page } from '$app/state';

	let { children } = $props();
	let query = $state('');

	$effect(() => {
		const q = page.url.searchParams.get('q');
		if (q && !query) query = q;
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<header>
	<div class="bar">
		<a href="/" class="brand">Bible Semantic Graph</a>
		<form action="/search" method="get" class="search">
			<input
				type="search"
				name="q"
				placeholder="Search nodes, names, body…"
				bind:value={query}
				autocomplete="off"
			/>
		</form>
	</div>
</header>

<main>
	{@render children()}
</main>

<footer>
	<small>A personal knowledge graph.</small>
</footer>
