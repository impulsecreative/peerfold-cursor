#!/usr/bin/env python3
"""Contact sheet of page screenshots (top 1200px of each).
usage: montage.py "Title" out.png /path1 /path2 ...   (reads shots/<path__x>.png made by shot.py)"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
title, out, paths = sys.argv[1], sys.argv[2], sys.argv[3:]
cols, tw, th, lab, pad = 6, 360, 300, 34, 12
rows = (len(paths) + cols - 1) // cols
M = Image.new('RGB', (cols * (tw + pad) + pad, rows * (th + lab + pad) + pad + 50), '#e9eef3'); d = ImageDraw.Draw(M)
try:
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
    fb = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
except Exception: f = fb = ImageFont.load_default()
d.text((pad, 14), title, fill='#223269', font=fb)
for i, p in enumerate(paths):
    im = Image.open(f"shots/{os.environ.get('SHOT_PREFIX','')}{p.strip('/').replace('/', '__') or 'home'}.png").convert('RGB').crop((0, 0, 1440, 1200)).resize((tw, th))
    x = pad + (i % cols) * (tw + pad); y = 50 + pad + (i // cols) * (th + lab + pad)
    M.paste(im, (x, y)); d.rectangle([x, y + th, x + tw, y + th + lab], fill='white')
    d.text((x + 6, y + th + 9), p if len(p) < 44 else p[:41] + '…', fill='#222', font=f)
M.save(out, optimize=True); print(out, M.size)
