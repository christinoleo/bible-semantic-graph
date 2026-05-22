import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		host: true, // bind 0.0.0.0 so Tailscale peers (and LAN) can reach the dev server
		port: 7654,
		strictPort: true,
		// Vite blocks requests whose Host header isn't in its allowlist (CVE-2025-24010).
		// Allow Tailscale MagicDNS, `.ts.net`, and bare hostnames.
		allowedHosts: true
	},
	preview: {
		host: true,
		port: 7654,
		strictPort: true,
		allowedHosts: true
	}
});
