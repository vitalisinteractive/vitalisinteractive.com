# Vitalis Interactive website

This repository contains the multipage static website for `vitalisinteractive.com`. The site uses plain HTML, CSS, and JavaScript and is hosted through GitHub Pages.

## Active site files

- `index.html` and the other root-level `.html` files contain the public pages and metadata.
- `styles.css` contains the core palette, layout, components, and responsive rules.
- `foundation.css` contains shared accessibility and resilient-layout refinements.
- `newsletter.css` contains the Vitalis Dispatch embed and privacy-page styles.
- `site.js` contains the mobile navigation, copyright year, and single Metricool loader.
- `assets/` contains the site logo and related static media.
- `sitemap.xml`, `robots.txt`, `site.webmanifest`, `CNAME`, and `.nojekyll` support search, browser, and GitHub Pages behavior.

Public contact addresses:

- General, business, creators, press, and partnerships: `hello@vitalisinteractive.com`
- Player support and bug reports: `support@vitalisinteractive.com`

## Local preview

From the repository root, run:

```powershell
python -m http.server 8000
```

Then open `http://127.0.0.1:8000/`. Use an HTTP server rather than opening the HTML files directly so relative resources behave as they do on GitHub Pages.

## Validation

Run the standard-library site check and Git whitespace check before review:

```powershell
python scripts/check_site.py
git diff --check
```

The validation workflow runs the site check on pushes and pull requests.

## Publication

GitHub Pages serves the repository root from `main` at `vitalisinteractive.com`. A branch, local commit, or successful validation run is only a candidate: merging to `main` or publishing any change requires explicit approval. Do not change `CNAME`, DNS, or Pages settings as part of ordinary website edits.
