#!/usr/bin/env python3
"""Apply reviewed Steam news to four public files. Preserve the approved design."""
from __future__ import annotations
import datetime as dt
import hashlib
import html
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE = '5a19ca75ea88b1db71ee88e8798e32662c5ca40b'
DATE = '2026-09-21'
FEED = 'https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=4820790&count=100&maxlength=0&feeds=steam_community_announcements'
UPDATES = [
 ('1844115010502605', 1790027803, '2026-09-21', 'steam-achievements', 'Steam Achievements & Save Recovery Update',
  ['25 Steam achievements are now live, including four hidden milestones. They cover property purchases, financing, staffing, governance, investing, Foundation giving, and succession. Existing campaigns can unlock achievements when the saved game state or history proves the milestone; missing historical evidence is not invented.',
   'Save warnings now stay attached to the save attempt that caused them. A later successful save no longer clears an unrelated unresolved warning, and quit or window-close recovery preserves the correct failure context. No new game is required.']),
 ('1844115010501448', 1789998518, '2026-09-21', 'succession-foundation-history', 'Succession, Foundation & AcrePilot History',
  ['Compare successor candidates, change the designated primary successor, nominate an alternate, and nominate professional successors aged 22–65. Designation does not boost readiness, and this update does not add voluntary retirement. AcrePilot starts with the newest 20 negotiation records and lets you reveal older records 20 at a time without deleting history.',
   'Foundation balances, unavailable annual comparisons, financing, and trust wording now explain what the simulation actually models. Foundation contributions do not currently reduce modeled taxable income. Existing saves are supported.']),
 ('1844115010498955', 1789912685, '2026-09-20', 'refinance-banking', 'Refinance Recovery & Banking Clarity Update',
  ['Refinancing no longer leaves the player trapped when a save acknowledgement fails. Uncommitted actions can be cleared and retried safely; actions that already happened are preserved with duplicate money or mortgage changes blocked. The same save path received additional safeguards for other high-value confirmations and acquisition closing.',
   'The Banking overview now shows the actual remaining line-of-credit availability, rather than labeling the full credit limit as available. Existing saves remain supported.']),
 ('1844115010497982', 1789855626, '2026-09-19', 'runtime-compatibility', 'Runtime & Compatibility Update',
  ['Maintenance brings the Windows desktop runtime onto a newer supported release, with Steam integration, rendering, save/load, quitting, relaunch, and pending-save handling revalidated. There are no intentional gameplay, balance, economy, progression, or save-format changes. Existing saves remain supported.']),
 ('1844115010497633', 1789841496, '2026-09-19', 'tax-accounting-property-manager', 'Tax, Accounting & Property Manager Integrity Update',
  ['Unpaid estimated-tax installments now remain outstanding through saves and year changes and are retried oldest first at later month closes when cash is available, without forcing an overdraft. Older saves are not assigned invented historical tax obligations.',
   'Completed Foundation contributions remain in the historical reports without repeating as a current-period expense. Property Manager replies now recognize delinquent tenants as well as late tenants. Existing saves are supported.']),
 ('1844115010495982', 1789763378, '2026-09-18', 'nnn-dynasty', 'NNN Economics, Save Compatibility & Dynasty Fixes',
  ['Single-tenant NNN acquisitions now use one consistent lease-based model for income, net operating income, valuation, and financing. Older owned properties retain their historical income and NOI until an actual lease transition, rather than having legitimate history rewritten on load.',
   'Later-generation Dynasty recovery and misleading ceremony instructions are corrected without changing the 65-point readiness requirement. Rent-action and acquisition safeguards also improve retry and save reliability. No new game is required.']),
]
BODY_HASHES = {
 '1844115010502605': '0c092a28f3cee2b6dd742ec04c938f246755df6af0204b898cf42c3cf9b336e9',
 '1844115010501448': '2546d4e7e63a0895af74610eb5a30beb0c942cb9120596134d3fb6334fdfcfe2',
 '1844115010498955': '7ab5199fbdea6576dda9108d33f2af09155654fe1ef9b20343b0f65a55ee2fff',
 '1844115010497982': '115e872336344457dfe8053a6dbb860352ed848825c3d277aa8a6da009cc06e3',
 '1844115010497633': 'a66b400d250d9578c196671de881644dee573374ad8bd89e2591dfb779b6a944',
 '1844115010495982': 'b11f5c5cf377ba7fe262e0274b9304159e4af17c3c73c8d0f56565c57ec10594',
}

def source_url(gid):
    return 'https://steamstore-a.akamaihd.net/news/externalpost/steam_community_announcements/' + gid

def verify_sources():
    with urlopen(Request(FEED, headers={'User-Agent': 'VitalisWebsiteContentReview/1.0', 'Cache-Control': 'no-cache'}), timeout=35) as response:
        data = json.load(response)['appnews']
    assert data['appid'] == 4820790
    items = data['newsitems']
    assert items[0]['gid'] == UPDATES[0][0], 'A newer announcement requires review'
    lookup = {item['gid']: item for item in items}
    evidence = []
    for gid, stamp, date, slug, title, paragraphs in UPDATES:
        item = lookup[gid]
        assert item['feedname'] == 'steam_community_announcements'
        assert item['date'] == stamp and title in item['title']
        assert item['url'] == source_url(gid)
        assert hashlib.sha256(item['contents'].encode()).hexdigest() == BODY_HASHES[gid], 'Announcement changed since review'
        evidence.append({'gid': gid, 'title': item['title'], 'url': item['url'], 'date': date, 'source_body_sha256': BODY_HASHES[gid]})
    return evidence

def apply(root):
    names = ['index.html', 'family-office-simulator.html', 'latest.html', 'sitemap.xml']
    before = {name: (root / name).read_text(encoding='utf-8') for name in names}
    news = before['latest.html']
    marker = '<div class="vi-wrap update-list">'
    assert news.count(marker) == 1
    ids = ['update-' + u[2] + '-' + u[3] for u in UPDATES]
    assert not any(f'id="{entry}"' in news for entry in ids), 'Already/partly applied; review required'
    entries = []
    for gid, stamp, date, slug, title, paragraphs in UPDATES:
        display = dt.date.fromisoformat(date).strftime('%B %d, %Y').replace(' 0', ' ')
        content = ''.join('<p>' + html.escape(p) + '</p>' for p in paragraphs)
        entries.append(f'<article id="update-{date}-{slug}" data-steam-gid="{gid}"><time datetime="{date}">{display}</time><div><h2>{html.escape(title)}</h2>{content}<a class="vi-inline-link" href="{source_url(gid)}" target="_blank" rel="noopener noreferrer">Full notes on Steam <span aria-hidden="true">↗</span></a></div></article>')
    news = news.replace(marker, marker + '\n' + '\n'.join(entries) + '\n', 1)
    old = 'Family Office Simulator release notes, hotfixes, and studio updates. Latest update: September 14, 2026.'
    new = 'Family Office Simulator update notes: Steam achievements, succession planning, refinancing, accounting, and save recovery. Updated September 21, 2026.'
    assert news.count(old) == 3
    after = dict(before)
    after['latest.html'] = news.replace(old, new)
    for name in ('index.html', 'family-office-simulator.html'):
        text = before[name]
        old = '<span class="vi-kicker">Latest from the studio · September 14, 2026</span><h2>FOS: closing reliability &amp; Marketplace improvements.</h2>'
        new = '<span class="vi-kicker">Latest from the studio · September 21, 2026</span><h2>FOS: Steam achievements &amp; save recovery.</h2><p>25 achievements, with credit for existing campaigns where the saved history proves a milestone.</p>'
        assert text.count(old) == 1
        text = text.replace(old, new)
        old_link = 'href="latest.html">Read the update'
        assert text.count(old_link) == 1
        text = text.replace(old_link, f'href="latest.html#{ids[0]}">Read the update')
        if name == 'family-office-simulator.html':
            old_copy = 'Hire staff, manage the workload, and establish the structures that carry the institution into its next generation.'
            new_copy = 'Hire staff, manage the workload, and plan who takes over next. Compare successor candidates, change the designated primary successor, or nominate an alternate without changing their underlying readiness.'
            assert text.count(old_copy) == 1
            text = text.replace(old_copy, new_copy)
        after[name] = text
    sitemap = before['sitemap.xml']
    for suffix in ('', 'family-office-simulator.html', 'latest.html'):
        old = f'<loc>https://vitalisinteractive.com/{suffix}</loc><lastmod>2026-09-15</lastmod>'
        assert sitemap.count(old) == 1
        sitemap = sitemap.replace(old, old.replace('2026-09-15', DATE))
    after['sitemap.xml'] = sitemap
    original_archive = before['latest.html'].split(marker, 1)[1].split('</section>', 1)[0]
    assert original_archive in after['latest.html'], 'Prior archive changed'
    for name, text in after.items():
        (root / name).write_text(text, encoding='utf-8')
    return {name: {'before_sha256': hashlib.sha256(before[name].encode()).hexdigest(), 'after_sha256': hashlib.sha256(after[name].encode()).hexdigest()} for name in names}

if __name__ == '__main__':
    evidence = verify_sources()
    files = apply(ROOT)
    out = ROOT / 'steam-review'; out.mkdir(exist_ok=True)
    report = {'verified_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'source': FEED, 'announcements': evidence, 'files': files, 'scope': 'Four public content files only; no layout, artwork, game build, newsletter, analytics, or hosting changes.'}
    (out / 'content-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
