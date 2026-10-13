#!/usr/bin/env python3
"""Download source images and prepare them for upload.
usage: prep_images.py images.json [out_dir] [--bg '#ffffff']
images.json: list of {"src":..., "alt":...} (styles.py output works).
- SVG is rendered to PNG (needs cairosvg).
- Transparent images are flattened onto --bg (Peerfold draws a grey
  placeholder behind transparent images). Use the color of the section
  the image sits on.
- Width is capped at 2000px. Writes out_dir/index.json."""
import json, os, re, sys, io, hashlib, urllib.parse, requests
from PIL import Image
args = [a for a in sys.argv[1:]]
bg = '#ffffff'
if '--bg' in args: i = args.index('--bg'); bg = args[i + 1]; del args[i:i + 2]
src = json.load(open(args[0])); out_dir = args[1] if len(args) > 1 else 'img'
os.makedirs(out_dir, exist_ok=True)
rgb = tuple(int(bg.lstrip('#')[k:k + 2], 16) for k in (0, 2, 4)) + (255,)
idx = {}
for item in src:
    u = item['src']
    if not u or u.startswith('data:') or u in idx: continue
    name = urllib.parse.unquote(u.split('?')[0].rsplit('/', 1)[-1])
    stem = re.sub(r'[^a-zA-Z0-9]+', '-', name.rsplit('.', 1)[0]).strip('-').lower()[:50] + '-' + hashlib.md5(u.encode()).hexdigest()[:5]
    r = requests.get(u, headers={'User-Agent': 'Mozilla/5.0'}, timeout=60)
    if r.status_code != 200: print('FAIL', u, r.status_code); continue
    try:
        if name.lower().endswith('.svg'):
            import cairosvg; im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=r.content, output_width=1000)))
        else: im = Image.open(io.BytesIO(r.content))
    except Exception as e: print('ERR', u, e); continue
    im = im.convert('RGBA')
    if im.width > 2000: im = im.resize((2000, int(im.height * 2000 / im.width)))
    flat = Image.new('RGBA', im.size, rgb); flat.alpha_composite(im); flat = flat.convert('RGB')
    photo = name.lower().endswith(('.jpg', '.jpeg', '.webp'))
    fn = f'{out_dir}/{stem}.' + ('jpg' if photo else 'png')
    flat.save(fn, quality=85) if photo else flat.save(fn, optimize=True)
    idx[u] = {'file': fn, 'w': flat.width, 'h': flat.height, 'alt': item.get('alt', '')}
    print(fn, flat.size)
json.dump(idx, open(f'{out_dir}/index.json', 'w'), indent=1)
