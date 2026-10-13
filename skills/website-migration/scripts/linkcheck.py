#!/usr/bin/env python3
"""Static crawl of a live Peerfold site: every page 200, every internal link + #anchor resolves,
any leftover old-domain references, external link status, image hosts.
usage: linkcheck.py BASE OLD_DOMAIN paths.txt [out.json]
  BASE        e.g. https://<workspace>.peerfold.app/site   (address folder included)
  OLD_DOMAIN  e.g. example.com  (regex-searched in raw HTML, incl. JSON-LD / srcset)
  paths.txt   one page path per line ("/", "/about", ...) or "id path" lines (sites_list_pages dump)
Follows internal links it finds, so pages missing from paths.txt are crawled too."""
import requests, re, json, sys
from urllib.parse import urljoin, urlparse, urldefrag
from bs4 import BeautifulSoup
BASE, OLD, PF = sys.argv[1].rstrip('/'), sys.argv[2], sys.argv[3]
OUT = sys.argv[4] if len(sys.argv) > 4 else 'linkcheck.json'
host = urlparse(BASE).netloc; prefix = urlparse(BASE).path
S = requests.Session(); S.headers['User-Agent'] = 'Mozilla/5.0 linkcheck'
paths = [l.split()[-1] for l in open(PF) if l.strip()]
queue = [BASE + ('' if p == '/' else p) for p in paths]
seen, ids, links, old, ext, imgs = {}, {}, {}, [], set(), set()
while queue:
    u = queue.pop(0)
    if u in seen: continue
    r = S.get(u, timeout=30); seen[u] = r.status_code
    if r.status_code != 200 or 'text/html' not in r.headers.get('content-type', ''): continue
    soup = BeautifulSoup(r.text, 'html.parser')
    ids[u] = {e.get('id') for e in soup.find_all(id=True)}
    old += [(u, m.group(0)[:150]) for m in re.finditer(r'[^"\'\s<>]*' + re.escape(OLD) + r'[^"\'\s<>]*', r.text, re.I)]
    out = []
    for a in soup.find_all('a', href=True):
        full = urljoin(u, a['href']); out.append(full); pu = urlparse(full)
        if pu.netloc == host and pu.path.startswith(prefix):
            b, _ = urldefrag(full)
            if b not in seen and b not in queue: queue.append(b)
        elif pu.scheme in ('http', 'https'): ext.add(full)
    for i in soup.find_all(['img', 'source']):
        for k in ('src', 'srcset'):
            if i.get(k): imgs.add(urljoin(u, i[k].split()[0]))
    links[u] = out
bad, badanch = [], []
for u, out in links.items():
    for l in out:
        if urlparse(l).netloc != host: continue
        b, frag = urldefrag(l)
        if b not in seen: seen[b] = S.get(b, timeout=30).status_code
        if seen[b] != 200: bad.append((u, l, seen[b]))
        elif frag and frag not in ids.get(b, set()): badanch.append((u, l))
def st(x, head=True):
    try:
        r = S.head(x, timeout=20, allow_redirects=True) if head else None
        if r is None or r.status_code >= 400: r = S.get(x, timeout=20, allow_redirects=True)
        return r.status_code
    except Exception as e: return str(e)[:60]
extres = {e: st(e) for e in sorted(ext)}
imgres = {i: st(i) for i in sorted(imgs)}
rep = dict(pages=seen, broken=sorted(set(bad)), bad_anchors=sorted(set(badanch)), old_domain=sorted(set(old)),
           external=extres, img_hosts=sorted({urlparse(i).netloc for i in imgs}),
           bad_imgs={k: v for k, v in imgres.items() if v != 200})
json.dump(rep, open(OUT, 'w'), indent=1)
print('pages', len(seen), 'non200', [(u, s) for u, s in seen.items() if s != 200])
print('broken internal', len(rep['broken']), rep['broken'][:20])
print('bad anchors', sorted({l for _, l in rep['bad_anchors']}))
print(OLD, 'refs', sorted({x for _, x in rep['old_domain']}))
print('external non-200', {k: v for k, v in extres.items() if v != 200})
print('img hosts', rep['img_hosts'], 'bad imgs', rep['bad_imgs'])
