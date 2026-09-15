#!/usr/bin/env python3
"""Browser checks and screenshots for the real multipage candidate, not a mockup.
Third-party tracking/form endpoints are stubbed; no forms are submitted.
"""
from __future__ import annotations
import functools
import hashlib
import http.server
import json
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'review' / 'website-multipage-03'
WIDTHS = (320, 390, 768, 1024, 1440, 1920)

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}/'
    pages = sorted(path.name for path in ROOT.glob('*.html'))
    report = {'pages': pages, 'widths': list(WIDTHS), 'checks': [], 'failures': [],
              'limits': 'Chromium checks only. External analytics and Brevo form are stubbed to avoid real tracking/subscriptions. This is not a full accessibility certification.',
              'screenshots': {}}
    def check(label, ok, detail=None):
        record = {'check': label, 'pass': bool(ok)}
        if detail is not None:
            record['detail'] = detail
        report['checks'].append(record)
        if not ok:
            report['failures'].append(record)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(device_scale_factor=1, reduced_motion='reduce')
        context.route('https://tracker.metricool.com/**', lambda route: route.fulfill(status=200, content_type='application/javascript', body='window.beTracker={t:function(){}};'))
        context.route('https://*.sibforms.com/**', lambda route: route.fulfill(status=200, content_type='text/html', body='<html lang="en"><title>Newsletter review</title><body>Existing Brevo signup. External submission disabled during automated review.</body></html>'))
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        for width in WIDTHS:
            page.set_viewport_size({'width': width, 'height': 950})
            for name in pages:
                errors.clear()
                response = page.goto(base + name, wait_until='networkidle')
                page.evaluate('''async () => {
                    for (const img of document.images) {
                        img.loading = 'eager';
                        try { await img.decode(); } catch (_) {}
                    }
                }''')
                prefix = f'{name} @ {width}px'
                check(prefix + ': HTTP 200', response.status == 200)
                check(prefix + ': one h1', page.locator('main h1').count() == 1)
                check(prefix + ': no horizontal overflow', page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'))
                missing = page.evaluate('Array.from(document.images).filter(i => !i.complete || i.naturalWidth === 0).map(i => i.getAttribute("src"))')
                check(prefix + ': all local images decoded', not missing, missing)
                check(prefix + ': no JavaScript errors', not errors, list(errors))
                check(prefix + ': six real navigation destinations', page.locator('nav[aria-label="Primary navigation"] a[href$=".html"]').count() == 6)
                check(prefix + ': no game-dialog UI', page.locator('dialog,[role="dialog"]').count() == 0)
                if name == 'index.html' and width in (390, 1440):
                    filename = 'home-mobile.png' if width == 390 else 'home-desktop.png'
                    page.screenshot(path=str(OUT / filename), full_page=True)
                    report['screenshots'][filename] = hashlib.sha256((OUT / filename).read_bytes()).hexdigest()
                if width == 1440 and name in ('games.html', 'family-office-simulator.html', 'main-street-operator.html', 'dealer-principal.html', 'latest.html'):
                    filename = name.replace('.html', '.png')
                    page.screenshot(path=str(OUT / filename), full_page=True)
                    report['screenshots'][filename] = hashlib.sha256((OUT / filename).read_bytes()).hexdigest()
        page.set_viewport_size({'width': 390, 'height': 844})
        page.goto(base, wait_until='networkidle')
        button = page.locator('[data-menu]')
        nav = page.locator('[data-nav]')
        check('Mobile navigation starts closed', button.get_attribute('aria-expanded') == 'false' and not nav.is_visible())
        button.click()
        check('Mobile navigation opens', button.get_attribute('aria-expanded') == 'true' and nav.is_visible())
        nav.locator('a').first.focus()
        page.keyboard.press('Escape')
        check('Escape closes menu and restores focus', button.get_attribute('aria-expanded') == 'false' and button.evaluate('(element) => element === document.activeElement'))
        button.click()
        nav.get_by_role('link', name='Games', exact=True).click()
        check('Games link opens a separate page', page.url.endswith('/games.html'))
        page.get_by_role('link', name='Explore Main Street Operator', exact=True).click()
        check('MSO opens its own page', page.url.endswith('/main-street-operator.html'))
        page.go_back()
        check('Browser Back returns to Games', page.url.endswith('/games.html'))
        page.get_by_role('link', name='Explore Dealer Principal', exact=True).click()
        check('DP opens its own page', page.url.endswith('/dealer-principal.html'))
        check('DP wishlist targets owner-supplied Steam page', page.locator('main a[href="https://store.steampowered.com/app/5158570/Dealer_Principal_The_Dealership_Simulator/"]').count() > 0)
        page.goto(base + 'family-office-simulator.html')
        check('FOS Steam destination correct', page.locator('main a[href="https://store.steampowered.com/app/4820790/Family_Office_Simulator/"]').count() > 0)
        page.goto(base + 'main-street-operator.html')
        check('MSO Steam destination correct', page.locator('main a[href="https://store.steampowered.com/app/5070740/Main_Street_Operator/"]').count() > 0)
        page.goto(base + 'latest.html')
        check('September 14 update present', page.locator('time[datetime="2026-09-14"]').count() == 1)
        page.goto(base + 'dispatch.html')
        check('Original newsletter provider retained', page.locator('iframe[src^="https://fdca8306.sibforms.com/"]').count() == 1)
        browser.close()
    server.shutdown()
    report['passed'] = len(report['checks']) - len(report['failures'])
    report['total'] = len(report['checks'])
    report['status'] = 'PASS' if not report['failures'] else 'FAIL'
    (OUT / 'browser-results.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'{report["status"]}: {report["passed"]}/{report["total"]} scoped browser checks')
    for failure in report['failures']:
        print(json.dumps(failure))
    return 1 if report['failures'] else 0

if __name__ == '__main__':
    raise SystemExit(main())
