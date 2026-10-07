"""Check local page/asset links and navigation after rebuilding the static site."""
from pathlib import Path
from collections import Counter
from urllib.parse import urlsplit, unquote
import json
import re
from bs4 import BeautifulSoup

site = Path(__file__).resolve().parents[1]
pages = {p.name: BeautifulSoup(p.read_text(), 'html.parser') for p in site.glob('*.html')}
errors = []
links = 0
for name, soup in pages.items():
    ids = [n['id'] for n in soup.select('[id]')]
    # Generated report widgets may use their own scoped IDs; verify all pages.
    for ident, count in Counter(ids).items():
        if count > 1:
            errors.append(f'{name}: duplicate id {ident}')
    for node in soup.select('[href], [src], [poster]'):
        for attr in ('href', 'src', 'poster'):
            value = node.get(attr)
            if not value:
                continue
            url = urlsplit(value)
            if url.scheme or url.netloc:
                continue
            path = unquote(url.path)
            target = (site / path) if path else (site / name)
            if not target.exists():
                errors.append(f'{name}: missing local {attr}: {value}')
                continue
            links += 1
            if url.fragment and target.name in pages:
                # Combined index also supports application routes, checked below.
                if target.name == 'index.html':
                    continue
                if pages[target.name].find(id=unquote(url.fragment)) is None:
                    errors.append(f'{name}: missing anchor {value}')

index = (site / 'index.html').read_text()
nav = json.loads(re.search(r'window.RFC_NAV=(.*?);</script>', index, re.S).group(1))
nav_pages = [page for category in nav for page in category['pages']]
for page in nav_pages:
    if page['file'] not in pages:
        errors.append(f'Navigation source missing: {page["file"]}')
    if not pages['index.html'].find(id='page-' + page['id']):
        errors.append(f'Navigation panel missing: {page["id"]}')

release = json.loads((site / 'WEB-RELEASE.json').read_text())['release']
for name, soup in pages.items():
    if name.startswith('example_workout'):
        continue
    for node in soup.select('link[rel="stylesheet"], script[src]'):
        value = node.get('href') or node.get('src')
        if not urlsplit(value).scheme and f'v={release}' not in value:
            errors.append(f'{name}: stale asset version: {value}')

print(json.dumps({'pages': len(pages), 'navigation_panels': len(nav_pages),
                  'local_references_checked': links, 'errors': errors}, indent=2))
raise SystemExit(bool(errors))
