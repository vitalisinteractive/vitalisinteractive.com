# Repository instructions

This is the `vitalisinteractive/vitalisinteractive.com` multipage static website. Active public pages are `index.html`, `games.html`, `studio.html`, `latest.html`, `family-office-simulator.html`, `support.html`, `contact.html`, `privacy.html`, and `404.html`. They are supported by `styles.css`, `foundation.css`, `newsletter.css`, `site.js`, and `assets/`.

- Keep public writing plainspoken, specific, warm, and verifiable. Avoid formulaic slogans, generic corporate copy, and repeated template sections.
- Do not name or promote an unrevealed project without explicit owner approval.
- Do not expose personal names, personal addresses, private identifiers, or private contact details by default.
- Preserve accessible landmarks, useful image alternatives, keyboard focus, readable contrast, responsive layouts, and the mobile-menu accessibility state.
- Preserve the single Metricool loader and the Brevo embed unless a task explicitly authorizes those systems.
- Validate with `python scripts/check_site.py` and `git diff --check`. Browser-check changed pages through a local HTTP server when layout or interaction changes.
- Treat a dirty worktree, unexpected branch, missing file, or remote mismatch as a stop condition. Never clean, reset, overwrite, merge, push, deploy, publish, or reveal a project without explicit approval.
