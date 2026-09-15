#!/usr/bin/env python3
"""Download only existing official Steam artwork; never generate replacements.

Run on the review branch. Metadata, image hashes and original dimensions are
recorded. Failure to retrieve any game's verified capsule is a hard failure.
"""
from __future__ import annotations
import hashlib
import html
import io
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'assets' / 'games'
GAMES = {
    'fos': (4820790, 'Family Office Simulator'),
    'mso': (5070740, 'Main Street Operator'),
    'dp': (5158570, 'Dealer Principal'),
}
MAX_BYTES = 16000000

def retrieve(url: str) -> bytes:
    host = urlparse(url).hostname or ''
    if not (host == 'store.steampowered.com' or host.endswith('.steamstatic.com')):
        raise ValueError('Unapproved asset host')
    with urlopen(Request(url, headers={'User-Agent': 'VitalisWebsiteAssetReview/1.0'}), timeout=25) as response:
        final = urlparse(response.geturl()).hostname or ''
        if not (final == 'store.steampowered.com' or final.endswith('.steamstatic.com')):
            raise ValueError('Unapproved redirect host')
        data = response.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError('Response exceeds size limit')
        return data

def save_image(url: str, target: Path, minimum=(300, 150)) -> dict:
    raw = retrieve(url)
    im = Image.open(io.BytesIO(raw))
    im.load()
    if im.width < minimum[0] or im.height < minimum[1] or im.width * im.height > 40000000:
        raise ValueError(f'Unusable dimensions {im.size}')
    original_size = im.size
    im = im.convert('RGB')
    # Format conversion only. No cropping, retouching, recoloring or generated pixels.
    im.thumbnail((1920, 1200), Image.Resampling.LANCZOS)
    im.save(target, 'WEBP', quality=94, method=6)
    return {'source_url': url, 'source_sha256': hashlib.sha256(raw).hexdigest(),
            'path': str(target.relative_to(ROOT)), 'width': im.width, 'height': im.height,
            'original_width': original_size[0], 'original_height': original_size[1],
            'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            'treatment': 'aspect-preserving resize and WebP compression only'}

def get_metadata(appid: int, expected: str) -> tuple[dict, str]:
    data = {}
    errors = []
    for suffix in ('&cc=us&l=english', '&l=english'):
        url = f'https://store.steampowered.com/api/appdetails?appids={appid}' + suffix
        try:
            response = json.loads(retrieve(url))
            result = response.get(str(appid), {})
            if result.get('success'):
                data = result['data']
                if expected.casefold() not in data.get('name', '').casefold():
                    raise RuntimeError(f'App identity mismatch for {appid}')
                return data, ''
        except Exception as exc:
            errors.append(str(exc))
    url = f'https://store.steampowered.com/app/{appid}/?l=english&cc=us'
    try:
        page = retrieve(url).decode('utf-8')
        title = re.search(r'<title>(.*?)</title>', page, re.S | re.I)
        if not title or expected.casefold() not in html.unescape(title.group(1)).casefold():
            raise RuntimeError(f'Could not verify store-page identity: {appid}')
        data = {'name': expected, 'steam_appid': appid}
        return data, page
    except Exception as exc:
        errors.append(str(exc))
    raise RuntimeError(f'No verified official metadata for {appid}: ' + '; '.join(errors))

def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    all_data = {}
    for key, (appid, name) in GAMES.items():
        metadata, page = get_metadata(appid, name)
        images = []
        for field in ('capsule_image', 'header_image', 'capsule_imagev5'):
            candidate = metadata.get(field)
            if candidate and f'/{appid}/' in candidate:
                images.append(candidate)
        if page:
            images.extend(html.unescape(url) for url in re.findall(r'https://[^\s\"<>]+/(?:header|capsule_616x353)(?:_2x)?\.jpg[^\s\"<>]*', page)
                          if f'/{appid}/' in url)
        # These are official legacy CDN aliases, used only after app identity verification.
        for prefix in ('https://shared.fastly.steamstatic.com/store_item_assets/steam/apps',
                       'https://cdn.akamai.steamstatic.com/steam/apps'):
            images.extend([f'{prefix}/{appid}/capsule_616x353.jpg', f'{prefix}/{appid}/header.jpg'])
        accepted = []
        for number, url in enumerate(dict.fromkeys(images)):
            temporary = DEST / f'{key}-candidate-{number}.webp'
            try:
                item = save_image(url, temporary, (460, 215))
                accepted.append(item)
            except Exception as exc:
                print(f'Asset candidate unavailable: {key} {url}: {exc}', flush=True)
        if not accepted:
            raise RuntimeError(f'No official capsule could be retrieved for {name}')
        selected = max(accepted, key=lambda item: item['width'] * item['height'])
        final = DEST / f'{key}-capsule.webp'
        (ROOT / selected['path']).replace(final)
        for item in accepted:
            leftover = ROOT / item['path']
            if leftover.exists():
                leftover.unlink()
        selected['path'] = str(final.relative_to(ROOT))
        entry = {'appid': appid, 'name': metadata['name'], 'capsule': selected, 'screenshots': [],
                 'store_url': f'https://store.steampowered.com/app/{appid}/',
                 'short_description': metadata.get('short_description', ''),
                 'coming_soon': metadata.get('release_date', {}).get('coming_soon'),
                 'retrieved_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
        for number, shot in enumerate(metadata.get('screenshots', [])[:3], 1):
            url = shot.get('path_full', '')
            if f'/{appid}/' not in url:
                continue
            try:
                entry['screenshots'].append(save_image(url, DEST / f'{key}-gameplay-{number}.webp', (600, 300)))
            except Exception as exc:
                print(f'Optional public gameplay image unavailable: {key}: {exc}', flush=True)
        all_data[key] = entry
        print(f'CAPSULE VERIFIED {key}: {selected["source_url"]} ({selected["width"]}x{selected["height"]})', flush=True)
    (DEST / 'sources.json').write_text(json.dumps(all_data, indent=2) + '\n', encoding='utf-8')
    print('All three games have verified official capsule artwork. No substitute art used.', flush=True)
    return 0

if __name__ == '__main__':
    sys.exit(main())
