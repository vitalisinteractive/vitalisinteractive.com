# Vitalis Interactive website

Static, responsive one-page studio website prepared for GitHub Pages and the custom domain `vitalisinteractive.com`.

## Files

- `index.html` — page content and SEO metadata
- `styles.css` — responsive styling
- `script.js` — mobile navigation and subtle reveal behavior
- `CNAME` — tells GitHub Pages to serve `vitalisinteractive.com`
- `.nojekyll` — disables unnecessary Jekyll processing
- `robots.txt` and `sitemap.xml` — search-engine basics

## Current public links

- Steam: `https://store.steampowered.com/app/4820790/Family_Office_Simulator/`
- YouTube: `https://www.youtube.com/@VitalisInteractive`
- TikTok: `https://www.tiktok.com/@vitalisinteractive`
- Contact: `vitalisinteractive@gmail.com`

## Before publishing

1. The approved Vitalis logo is included in optimized web, header-mark, favicon, app-icon, and social-sharing formats.
2. Ideally replace the remotely loaded Steam header image with a local image in `assets/` so the website does not depend on Steam's CDN URL remaining unchanged.
3. Review the wording once on desktop and mobile.

## GitHub Pages setup

1. Create a **public** GitHub repository named `vitalisinteractive.com` under the `vitalisinteractive` account.
2. Upload all files in this folder to the repository root.
3. In the repository, open **Settings → Pages**.
4. Under **Build and deployment**, choose **Deploy from a branch**.
5. Select the default branch (normally `main`) and `/ (root)`, then save.
6. In **Custom domain**, enter `vitalisinteractive.com`.
7. After DNS resolves, enable **Enforce HTTPS**.

## Squarespace DNS setup for GitHub Pages

In Squarespace Domains DNS settings, remove only the current forwarding records for `vitalisinteractive.com`, then add GitHub Pages records:

### Apex A records

- Host: `@` → `185.199.108.153`
- Host: `@` → `185.199.109.153`
- Host: `@` → `185.199.110.153`
- Host: `@` → `185.199.111.153`

### WWW record

- Type: `CNAME`
- Host: `www`
- Data: `vitalisinteractive.github.io`

Do not change the forwarding or DNS for `familyofficesimulator.com`; it should continue directing visitors to Steam.
