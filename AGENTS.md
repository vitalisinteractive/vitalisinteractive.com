# Repository instructions

This is the `vitalisinteractive/vitalisinteractive.com` multipage static website. Active public pages are `index.html`, `games.html`, `studio.html`, `latest.html`, `family-office-simulator.html`, `support.html`, `contact.html`, `privacy.html`, and `404.html`. The former `dispatch.html` signup is retired and remains only as a noindex information route. Pages are supported by `styles.css`, `foundation.css`, `site.js`, and `assets/`.

- Keep public writing plainspoken, specific, warm, and verifiable. Avoid formulaic slogans, generic corporate copy, and repeated template sections.
- Do not name or promote an unrevealed project without explicit owner approval.
- Do not expose personal names, personal addresses, private identifiers, or private contact details by default.
- Preserve accessible landmarks, useful image alternatives, keyboard focus, readable contrast, responsive layouts, and the mobile-menu accessibility state.
- Preserve the single Metricool loader. The retired game-newsletter embed must not be re-enabled; protect historical consent and suppression records outside this repository.
- Validate with `python scripts/check_site.py` and `git diff --check`. Browser-check changed pages through a local HTTP server when layout or interaction changes.
- Treat a dirty worktree, unexpected branch, missing file, or remote mismatch as a stop condition. Never clean, reset, overwrite, merge, push, deploy, publish, or reveal a project without explicit approval.

- `scripts/build_website_refresh.py` is a retired one-shot migration script. Do not run or revive it for current site work.
- Current files on `main` are authoritative. Any new generator must preserve current update history, PRODUCT.md, DESIGN.md, legal/support content, analytics, privacy/retention terms, and exact provenance.
