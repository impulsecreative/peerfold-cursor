#!/usr/bin/env python3
"""Crop people photos to a square with the face centered.
usage: square_crop.py in.jpg out.jpg [SIZE]
Uses OpenCV face detection if installed; else crops at 22% from the top,
which suits most head-and-shoulders photos. Check every result by eye."""
import sys
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]; size = int(sys.argv[3]) if len(sys.argv) > 3 else 800
im = Image.open(src).convert('RGB'); w, h = im.size; s = min(w, h)
cx, cy = w / 2, h * 0.22 + s / 2 if h > w else h / 2
try:
    import cv2, numpy as np
    g = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2GRAY)
    faces = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml').detectMultiScale(g, 1.1, 5)
    if len(faces):
        x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3]); cx, cy = x + fw / 2, y + fh / 2
except Exception: pass
l = min(max(cx - s / 2, 0), w - s); t = min(max(cy - s / 2, 0), h - s)
im.crop((int(l), int(t), int(l) + s, int(t) + s)).resize((size, size)).save(dst, quality=88)
print(dst, size)
