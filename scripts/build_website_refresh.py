#!/usr/bin/env python3
"""Build the owner-requested multipage refresh on the isolated review branch.

The original public pages are read from an immutable baseline. Existing legal,
support and studio content is retained. The existing newsletter embed moves to
its own page. No production branch, hosting setting or DNS record is changed.
"""
from __future__ import annotations
import hashlib
import html
import json
import re
import subprocess
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = '785d43f367cb78f1b728a62dc3ba906f3b920a64'
BRANCH = 'design/website-multipage-existing-art-03'
DOMAIN = 'https://vitalisinteractive.com/'
FEED = 'https://steamcommunity.com/app/4820790/announcements/'
PAGES = {'fos': 'family-office-simulator.html', 'mso': 'main-street-operator.html', 'dp': 'dealer-principal.html'}
LINKS = {
 'fos': 'https://store.steampowered.com/app/4820790/Family_Office_Simulator/',
 'mso': 'https://store.steampowered.com/app/5070740/Main_Street_Operator/',
 'dp': 'https://store.steampowered.com/app/5158570/Dealer_Principal_The_Dealership_Simulator/',
}
NAMES = {'fos': 'Family Office Simulator', 'mso': 'Main Street Operator', 'dp': 'Dealer Principal'}
NAV = [('Home', 'index.html'), ('Games', 'games.html'), ('Studio', 'studio.html'), ('Updates', 'latest.html'), ('Support', 'support.html'), ('Contact', 'contact.html')]
UPDATES = [
 ('2026-09-14', 'September 14, 2026', 'Closing reliability, save durability & Marketplace', 'A correction for affected long-running saves at month close, stronger financial-state handling, clearer Marketplace listings, and calendar-accurate days on market. Existing saves remain supported.'),
 ('2026-09-09', 'September 9, 2026', 'AcrePilot closing authority fix', 'Corrects a case where older negotiation receipts could block a valid accepted acquisition. Existing saves and accepted deals are supported.'),
 ('2026-09-08', 'September 8, 2026', 'AcrePilot closing & financing follow-up', 'Corrects exchange-credit settlement reconciliation and a separate exact-cent balance issue that could prevent the financing screen from opening.'),
 ('2026-09-05', 'September 5, 2026', 'AcrePilot closing & mortgage lifecycle fix', 'Corrects closing and month-close failures involving legitimate mortgage lifecycle changes, older acquisition history, and checking balances with cents.'),
 ('2026-08-31', 'August 31, 2026', 'AcrePilot closing hotfix', 'Improves compatibility with older Banking and line-of-credit history, preserves valid LOC-funded purchases, and adds clearer closing explanations.'),
]
E = html.escape

def git(*args: str) -> str:
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True)

def original(path: str) -> str:
    return git('show', f'{BASE}:{path}')

def fragment(text: str, pattern: str) -> str:
    found = re.search(pattern, text, re.S)
    if not found:
        raise RuntimeError('Expected baseline content was not found: ' + pattern)
    return found.group(1)

def external(url: str, label: str, css='vi-button') -> str:
    return f'<a class="{css}" href="{E(url)}" target="_blank" rel="noopener noreferrer">{E(label)} <span aria-hidden="true">↗</span></a>'

def image(item: dict, alt: str, eager=False, css='') -> str:
    timing = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    return f'<img class="{css}" src="{E(item["path"])}" width="{item["width"]}" height="{item["height"]}" alt="{E(alt)}" {timing} decoding="async">'

def header(current: str) -> str:
    links = ''.join(f'<a href="{path}"' + (' aria-current="page"' if current == path else '') + f'>{label}</a>' for label, path in NAV)
    return f'''<header class="vi-header"><div class="vi-wrap vi-header-inner">
<a class="vi-brand" href="index.html" aria-label="Vitalis Interactive home"><img src="assets/vitalis-mark-exact-2026.webp" width="56" height="56" alt="Vitalis Interactive"><span>VITALIS<span>INTERACTIVE</span></span></a>
<button class="vi-menu" type="button" data-menu aria-expanded="false" aria-controls="site-navigation" aria-label="Open navigation menu"><span></span><span></span><span></span></button>
<nav class="vi-nav" id="site-navigation" data-nav aria-label="Primary navigation">{links}</nav>
</div></header>'''

FOOTER = '''<footer class="vi-footer"><div class="vi-wrap vi-footer-top">
<div class="vi-signature"><img src="assets/vitalis-master-exact-2026.webp" width="100" height="100" alt="Vitalis Interactive"><p>Independent simulation games.<br>Business, ownership, and the work in between.</p></div>
<div class="vi-footer-contacts"><div><span>Business, press &amp; creators</span><a href="mailto:hello@vitalisinteractive.com">hello@vitalisinteractive.com</a></div><div><span>Player support</span><a href="mailto:support@vitalisinteractive.com">support@vitalisinteractive.com</a></div></div>
</div><div class="vi-wrap vi-footer-bottom"><span>© <span data-year>2026</span> Vitalis Interactive</span><div><a href="dispatch.html">Email updates</a><a href="contact.html">Contact</a><a href="privacy.html">Privacy</a></div></div></footer>'''

def document(path: str, title: str, description: str, body: str, game=None, legacy=False) -> str:
    canonical = DOMAIN + ('' if path == 'index.html' else path)
    preview = f'assets/games/{game}-capsule.webp' if game else 'assets/vitalis-master-exact-2026.webp'
    data = {'@context': 'https://schema.org', '@type': 'WebPage', 'name': title, 'url': canonical,
            'publisher': {'@type': 'Organization', 'name': 'Vitalis Interactive', 'url': DOMAIN}}
    if game:
        data.update({'@type': 'VideoGame', 'name': NAMES[game], 'sameAs': LINKS[game], 'image': DOMAIN + preview})
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(description)}"><meta name="theme-color" content="#141414"><meta name="color-scheme" content="light"><meta name="robots" content="{'noindex,follow' if path == '404.html' else 'index,follow,max-image-preview:large'}">
<link rel="canonical" href="{canonical}"><link rel="icon" href="assets/favicon-32.png" type="image/png"><link rel="manifest" href="site.webmanifest">
<meta property="og:site_name" content="Vitalis Interactive"><meta property="og:type" content="website"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(description)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{DOMAIN + preview}"><meta property="og:image:alt" content="{E(NAMES[game] if game else 'Vitalis Interactive')}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{E(title)}"><meta name="twitter:description" content="{E(description)}"><meta name="twitter:image" content="{DOMAIN + preview}">
<link rel="stylesheet" href="styles.css"><link rel="stylesheet" href="foundation.css"><link rel="stylesheet" href="newsletter.css"><link rel="stylesheet" href="exact-logo-fix.css" data-vitalis-exact-logo><link rel="stylesheet" href="studio-refresh.css">
<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script></head>
<body class="vi-site" data-refresh="03"><a class="vi-skip" href="#main">Skip to content</a>{header(path)}<main id="main" class="{'vi-legacy' if legacy else 'vi-main'}">{body}</main>{FOOTER}<script src="site.js"></script></body></html>\n'''

def card(key: str, assets: dict, number: str) -> str:
    label = 'Available now · Early Access' if key == 'fos' else 'Coming soon'
    short = {'fos': 'Acquire property, manage capital, and build a family institution.',
             'mso': 'Take over a tired laundromat. Make it worth coming back to.',
             'dp': 'Run the dealership, not just the showroom.'}[key]
    return f'''<article class="vi-game"><a class="vi-art-link" href="{PAGES[key]}" aria-label="Explore {NAMES[key]}">{image(assets[key]['capsule'], NAMES[key] + ' — official Steam capsule artwork')}</a><div class="vi-game-meta"><span>{number} / {label}</span><a href="{PAGES[key]}">Explore the game <span aria-hidden="true">→</span></a></div><h2><a href="{PAGES[key]}">{NAMES[key]}</a></h2><p>{short}</p>{external(LINKS[key], 'Play on Steam' if key == 'fos' else 'Wishlist on Steam', 'vi-inline-link')}</article>'''

def latest_strip() -> str:
    return '''<section class="vi-update-strip"><div class="vi-wrap vi-update-inner"><div><span class="vi-kicker">Latest from the studio · September 14, 2026</span><h2>FOS: closing reliability &amp; Marketplace improvements.</h2></div><a class="vi-inline-link" href="latest.html">Read the update <span aria-hidden="true">→</span></a></div></section>'''

def homepage(assets: dict) -> str:
    shot = assets['fos']['screenshots'][0] if assets['fos']['screenshots'] else assets['fos']['capsule']
    return f'''<section class="vi-home-hero"><div class="vi-wrap vi-hero-grid"><div class="vi-hero-copy"><span class="vi-kicker vi-gold">Available now · Steam Early Access</span><h1>Family Office<br>Simulator</h1><p>Acquire property. Put capital to work. Build a family office that lasts beyond one generation.</p><div class="vi-actions">{external(LINKS['fos'], 'Play on Steam', 'vi-button vi-primary')}<a class="vi-inline-link" href="family-office-simulator.html">Explore the game <span aria-hidden="true">→</span></a></div><span class="vi-small vi-hero-platform">Windows PC · Single-player</span></div><a class="vi-hero-art" href="family-office-simulator.html" aria-label="Explore Family Office Simulator">{image(shot, 'Family Office Simulator — screenshot from the public Steam page' if assets['fos']['screenshots'] else 'Family Office Simulator — official Steam artwork', True)}<span>Family Office Simulator <span aria-hidden="true">↗</span></span></a></div></section>
<section class="vi-section"><div class="vi-wrap"><div class="vi-section-heading"><div><span class="vi-kicker">In development</span><h2>Next from Vitalis.</h2></div><a class="vi-inline-link" href="games.html">All games <span aria-hidden="true">→</span></a></div><div class="vi-games-grid">{card('mso', assets, '01')}{card('dp', assets, '02')}</div></div></section>{latest_strip()}'''

def gallery(key: str, assets: dict) -> str:
    shots = assets[key]['screenshots']
    if not shots:
        return ''
    entries = ''.join(f'<figure><a href="{E(shot["path"])}" target="_blank" rel="noopener noreferrer" aria-label="Open {NAMES[key]} screenshot {i} at full size">{image(shot, NAMES[key] + f" — official Steam screenshot {i}")}</a><figcaption>Screenshot {i} from the public Steam page. Open image for full size.</figcaption></figure>' for i, shot in enumerate(shots, 1))
    return f'<section class="vi-section vi-gallery-section"><div class="vi-wrap"><div class="vi-section-heading"><div><span class="vi-kicker">A closer look</span><h2>Inside the game.</h2></div></div><div class="vi-gallery">{entries}</div></div></section>'

def gamepage(key: str, assets: dict) -> str:
    item = assets[key]
    status = 'Available now in Steam Early Access' if key == 'fos' else 'In development · Coming soon'
    intro = E(html.unescape(item['short_description']))
    subtitle = '<p class="vi-game-subtitle">The Dealership Simulator</p>' if key == 'dp' else ''
    concepts = {
      'fos': [('Invest with consequences', 'Property, financing, liquidity, and operating costs are connected. A deal has to work after the purchase as well as before it.'), ('Build the office', 'Hire staff, manage the workload, and establish the structures that carry the institution into its next generation.')],
      'mso': [('The floor is your business', 'Walk the store, clean and repair machines, and earn back customers while keeping the day-to-day operation moving.'), ('Make the turnaround work', 'Set prices, manage cash flow, modernize equipment, and pay down the seller note. Decide when the store is worth keeping—or selling.')],
      'dp': [('The desk, not the car', 'The focus is running the dealership: inventory, desking, finance and insurance, service, parts, and the team behind the operation.'), ('One connected business', 'Cash flow, OEM relationships, and customer satisfaction matter alongside the next deal. Development is ongoing; follow the Steam page for availability.')],
    }
    narrative = ''.join(f'<article><h2>{heading}</h2><p>{copy}</p></article>' for heading, copy in concepts[key])
    art = image(item['capsule'], NAMES[key] + ' — current Steam capsule artwork', True)
    body = f'''<section class="vi-product-hero"><div class="vi-wrap"><a class="vi-breadcrumb" href="games.html">← All games</a><div class="vi-product-grid"><div><span class="vi-kicker vi-gold">{status}</span><h1>{NAMES[key]}</h1>{subtitle}<p class="vi-lead">{intro}</p><div class="vi-actions">{external(LINKS[key], 'Play on Steam' if key == 'fos' else 'Wishlist on Steam', 'vi-button vi-primary')}</div></div><figure class="vi-capsule-feature">{art}<figcaption>Official game artwork</figcaption></figure></div></div></section><section class="vi-section"><div class="vi-wrap vi-story">{narrative}</div></section>'''
    body += gallery(key, assets)
    if key == 'fos':
        body += latest_strip()
    else:
        body += f'<section class="vi-update-strip"><div class="vi-wrap vi-update-inner"><div><span class="vi-kicker">In development</span><h2>Follow {NAMES[key]} on Steam.</h2><p>The game is not released yet. Wishlist it to follow its progress.</p></div>{external(LINKS[key], "Wishlist on Steam", "vi-button vi-dark")}</div></section>'
    return body

def main() -> int:
    branch = git('branch', '--show-current').strip()
    if branch != BRANCH:
        raise RuntimeError(f'Refusing to build on {branch!r}; expected {BRANCH}')
    if git('status', '--porcelain').strip():
        raise RuntimeError('Initial worktree is not clean; refusing to overwrite work')
    assets_path = ROOT / 'assets/games/sources.json'
    assets = json.loads(assets_path.read_text())
    for key in NAMES:
        item = assets[key]['capsule']
        actual = hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest()
        if actual != item['sha256']:
            raise RuntimeError(f'Artwork hash mismatch for {key}')
    source_home = original('index.html')
    dispatch = fragment(source_home, r'(<section class="dispatch-section".*?</section>)')
    original_js = original('site.js')
    original_tracker = fragment(original_js, r'(  if \(!window\.__vitalisMetricoolTrackerLoaded\).*?\n  \})')
    pages = {}
    pages['index.html'] = document('index.html', 'Vitalis Interactive | Independent Simulation Games', 'Explore Family Office Simulator, Main Street Operator, and Dealer Principal. Independent simulation games about business and ownership.', homepage(assets), 'fos')
    catalog = '<section class="vi-page-intro"><div class="vi-wrap"><span class="vi-kicker">Vitalis Interactive</span><h1>Our games.</h1><p>Find your next business to run.</p></div></section><section class="vi-section vi-catalog"><div class="vi-wrap vi-catalog-grid">' + ''.join(card(key, assets, f'{i:02}') for i, key in enumerate(NAMES, 1)) + '</div></section>'
    pages['games.html'] = document('games.html', 'Games | Vitalis Interactive', 'Play Family Office Simulator. Discover Main Street Operator and Dealer Principal, both coming soon.', catalog)
    for key, path in PAGES.items():
        pages[path] = document(path, NAMES[key] + (' — The Dealership Simulator' if key == 'dp' else '') + ' | Vitalis Interactive', html.unescape(assets[key]['short_description']), gamepage(key, assets), key)
    for path in ('studio.html', 'support.html', 'contact.html', 'privacy.html', '404.html'):
        old = original(path)
        title = html.unescape(fragment(old, r'<title>(.*?)</title>'))
        description = html.unescape(fragment(old, r'<meta name="description" content="(.*?)">'))
        body = fragment(old, r'<main id="main">(.*?)</main>')
        pages[path] = document(path, title, description, body, legacy=True)
    old_news = fragment(original('latest.html'), r'<div class="container update-list">(.*?)\n      </div>')
    new_news = ''.join(f'<article id="update-{date}"><time datetime="{date}">{display}</time><div><h2>{E(title)}</h2><p>{E(copy)}</p>{external(FEED, "Full notes on Steam", "vi-inline-link")}</div></article>' for date, display, title, copy in UPDATES)
    news_body = '<section class="vi-page-intro"><div class="vi-wrap"><span class="vi-kicker">From the studio</span><h1>Updates.</h1><p>What shipped, what changed, and the notes behind it.</p></div></section><section class="vi-section"><div class="vi-wrap update-list">' + new_news + old_news + '</div></section>'
    pages['latest.html'] = document('latest.html', 'Updates | Vitalis Interactive', 'Family Office Simulator release notes, hotfixes, and studio updates. Latest update: September 14, 2026.', news_body)
    pages['dispatch.html'] = document('dispatch.html', 'Vitalis Dispatch | Email Updates', 'Join Vitalis Dispatch for major game releases, development updates, and occasional playtest invitations.', dispatch.replace('<h2 id="dispatch-title">', '<h1 id="dispatch-title">').replace('Get major Vitalis updates by email.</h2>', 'Get major Vitalis updates by email.</h1>'), legacy=True)
    # Validate that moving the mailing list did not alter the existing provider endpoint.
    iframe = fragment(source_home, r'(<iframe .*?</iframe>)')
    if iframe not in pages['dispatch.html']:
        raise RuntimeError('Existing Brevo embed changed unexpectedly')
    for path, text in pages.items():
        (ROOT / path).write_text(text, encoding='utf-8')
    javascript = original_js.replace("if (event.key === 'Escape') setMenuState(false);", "if (event.key === 'Escape' && nav?.classList.contains('open')) { setMenuState(false); menu?.focus(); }")
    javascript = javascript.replace("  document.querySelectorAll('[data-year]')", "  window.matchMedia('(min-width: 901px)').addEventListener('change', event => { if (event.matches) setMenuState(false); });\n\n  document.querySelectorAll('[data-year]')")
    if original_tracker not in javascript:
        raise RuntimeError('Existing Metricool loader changed unexpectedly')
    (ROOT / 'site.js').write_text(javascript, encoding='utf-8')
    # Only the two games expressly revealed by the owner leave the protected list.
    checker = original('scripts/check_site.py')
    checker = re.sub(r'EXPECTED_NAV = \(.*?\n\)', 'EXPECTED_NAV = ' + repr(tuple(NAV)), checker, count=1, flags=re.S)
    checker = re.sub(r'CURRENT_PAGE = \{.*?\n\}', 'CURRENT_PAGE = ' + repr({path: path for _, path in NAV}), checker, count=1, flags=re.S)
    checker = checker.replace('NEWSLETTER_PAGES = {"index.html", "privacy.html"}', 'NEWSLETTER_PAGES = {"dispatch.html", "privacy.html"}')
    for sequence in ('(77, 97, 105, 110, 32, 83, 116, 114, 101, 101, 116, 32, 79, 112, 101, 114, 97, 116, 111, 114),', '(68, 101, 97, 108, 101, 114, 32, 80, 114, 105, 110, 99, 105, 112, 97, 108),'):
        if checker.count(sequence) != 1:
            raise RuntimeError('Unexpected protected-project baseline')
        checker = checker.replace('        ' + sequence + '\n', '')
    (ROOT / 'scripts/check_site.py').write_text(checker, encoding='utf-8')
    urls = ''.join(f'<url><loc>{DOMAIN + ("" if name == "index.html" else name)}</loc><lastmod>2026-09-15</lastmod></url>' for name in pages if name != '404.html')
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + '</urlset>\n')
    ET.parse(ROOT / 'sitemap.xml')
    notes = '''\n\n## September 2026 multipage refresh\n\nThe current-art review uses neutral charcoal, off-white and restrained gold.\n`studio-refresh.css` supplies the new shared presentation.\nMSO and Dealer Principal now have their own pages. The full newsletter signup\nretains the existing Brevo embed on `dispatch.html`, linked from every footer.\nHome is a short introduction, not a single-page application.\nArtwork provenance is recorded in `assets/games/sources.json`. No generated\nsubstitute art from the early design mockups is used.\nPublication still requires owner approval; this task does not change hosting.\n'''
    (ROOT / 'README.md').write_text(original('README.md') + notes, encoding='utf-8')
    design = original('DESIGN.md').replace('Dark teal/ink, warm paper, and restrained gold are the core palette.', 'Neutral charcoal, off-white, and restrained gold are the website palette. Existing game art retains its own colors.').replace('Headlines: Georgia / Times fallback.', 'New studio-page headlines: Arial / Helvetica / system sans-serif, with deliberate weight and spacing.')
    (ROOT / 'DESIGN.md').write_text(design + notes, encoding='utf-8')
    print(f'Built {len(pages)} real HTML pages; no dialog-based game navigation.')
    print('Exact studio identity, existing artwork, original legal content, Brevo embed and Metricool loader preserved.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
