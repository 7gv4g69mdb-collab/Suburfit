"""Write ocean.js: the sea around Adelaide (Gulf St Vincent, Encounter Bay, the Port River) as one polygon for the price map,
so the water shows in a clear blue like Google or Apple Maps. Land is every ABS suburb/locality in SA; the sea is what's left.
Run once; the coastline doesn't change with prices. Needs numpy, scipy, Pillow and contourpy (comes with matplotlib)."""
import json, os
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
import contourpy
HERE = os.path.dirname(os.path.abspath(__file__))
W, E, S, N = 136.6, 140.0, -36.3, -33.6          # area the blue sea covers (the map is kept inside this)
RES = 0.00035                                      # grid size in degrees, about 35 m
TOL = 0.00025                                      # simplify tolerance, about 25 m

rings = [r for v in json.load(open(os.path.join(HERE, "abs_sal_sa_shapes.json"))).values() for r in v]
s = open(os.path.join(HERE, "shapes.js")).read()
rings += [r for v in json.loads(s[s.index("{"):s.rindex("}") + 1]).values() for r in v]   # budget-tool suburbs live here

w, h = int((E - W) / RES) + 1, int((N - S) / RES) + 1
img = Image.new("L", (w, h), 0); dr = ImageDraw.Draw(img)
px = lambda x, y: ((x - W) / RES, (N - y) / RES)
for r in rings:
    if len(r) >= 3: dr.polygon([px(x, y) for x, y in r], fill=1)
land = np.array(img, dtype=bool)
land = ndimage.binary_closing(land, iterations=3, border_value=0) | land       # close slivers between suburbs
water = ~land
lab, n = ndimage.label(water)
edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
sea = np.isin(lab, list(edge))                                                 # only water joined to the open sea
sea = ndimage.binary_opening(sea, iterations=1)                                # drop 1-pixel specks
pad = np.pad(sea.astype(float), 1, constant_values=1.0)                         # treat the outside as sea, so edges close
gen = contourpy.contour_generator(z=pad, fill_type="OuterOffset")
polys, offs = gen.filled(0.5, 2.0)

def simplify(pts, tol):
    if len(pts) < 4: return pts
    keep = [False] * len(pts); keep[0] = keep[-1] = True; stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop(); (x1, y1), (x2, y2) = pts[a], pts[b]; dx, dy = x2 - x1, y2 - y1; L = (dx * dx + dy * dy) ** 0.5 or 1e-12
        best, bi = 0, None
        for i in range(a + 1, b):
            d = abs(dy * (pts[i][0] - x1) - dx * (pts[i][1] - y1)) / L
            if d > best: best, bi = d, i
        if bi is not None and best > tol: keep[bi] = True; stack += [(a, bi), (bi, b)]
    return [p for p, k in zip(pts, keep) if k]

out = []
for poly, off in zip(polys, offs):
    for a, b in zip(off[:-1], off[1:]):
        ring = [(round(N - (y - 1) * RES, 4), round(W + (x - 1) * RES, 4)) for x, y in poly[a:b]]   # [lat, lng]
        ring = [(min(max(la, S), N), min(max(lo, W), E)) for la, lo in ring]
        m = len(ring) // 2
        ring = simplify(ring[:m + 1], TOL) + simplify(ring[m:], TOL)[1:]   # closed ring: do each half
        if len(ring) >= 4: out.append(ring)
js = "  const OCEAN = " + json.dumps(out, separators=(",", ":")) + ";"
open(os.path.join(HERE, "ocean.js"), "w").write(js)
print(len(out), "rings,", sum(len(r) for r in out), "points,", round(len(js) / 1024), "KB")
