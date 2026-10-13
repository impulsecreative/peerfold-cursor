#!/usr/bin/env python3
"""Side-by-side image: source on the left, Peerfold build on the right.
usage: sidebyside.py source.png build.png out.png [MAX_HEIGHT]
Both images are scaled to the same width. Labels are drawn on top."""
import sys
from PIL import Image, ImageDraw, ImageFont
a, b, out = sys.argv[1:4]
maxh = int(sys.argv[4]) if len(sys.argv) > 4 else 6000
A, B = Image.open(a).convert('RGB'), Image.open(b).convert('RGB')
w = min(A.width, B.width)
A = A.resize((w, int(A.height * w / A.width))); B = B.resize((w, int(B.height * w / B.width)))
h = min(max(A.height, B.height), maxh); gap, top = 24, 48
M = Image.new('RGB', (w * 2 + gap, h + top), '#ffffff'); d = ImageDraw.Draw(M)
try: f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
except Exception: f = ImageFont.load_default()
d.text((10, 12), 'Source', fill='#111', font=f); d.text((w + gap + 10, 12), 'Peerfold', fill='#111', font=f)
M.paste(A.crop((0, 0, w, min(A.height, h))), (0, top)); M.paste(B.crop((0, 0, w, min(B.height, h))), (w + gap, top))
M.save(out, optimize=True); print(out, M.size)
