#!/usr/bin/env python3
"""Boats as the newest lidar saw them: view/data/boats.bin from cache/dsm2025.bin (NOAA's 2025 San Francisco Bay
and Delta lidar, flown 27 September 2025 here), or from cache/dsm1.bin (2018) when that is all there is.
The 2025 flight covers the shore and the harbors but not the middle of Richardson Bay, so nothing is drawn
out there; the harbormaster counted two boats anchored out in August 2026.

Over the water (the 4 m ground at the bay's level), outside building outlines and away from piers, every
connected patch of one-metre cells where the highest lidar return stands 0.8 m or more above the water is
taken as one moored boat: where it is, how long and wide (the patch's principal axes), which way it lies,
and how tall its tallest return is (a mast, usually). Patches under 6 m2 (a piling, a buoy, a bird) or over
500 m2 (a ship, a float, a missed building) are left out. Boats that touch are counted as one.
A record is six little-endian uint16: x east, y north, length, width, height (all decimetres), heading (tenths of a degree from east, 0 to 1799).
Run from anywhere: python3 view/tools/boats.py   (needs numpy; after view/prepare.py)
"""
import json, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); VIEW = os.path.join(HERE, ".."); CACHE = os.path.join(VIEW, "..", "cache")
town = json.load(open(os.path.join(VIEW, "data", "town.json"))); W = town["window"]
nx, ny, RES, water = W["nx"], W["ny"], W["res"], W["water_m"]; N = nx * RES
g = np.fromfile(os.path.join(VIEW, "data", "ground.bin"), dtype="<i2").reshape(ny, nx) / 10
wet = np.repeat(np.repeat(g <= water + 0.06, RES, axis=0), RES, axis=1)
new = town.get("water_2025_m") is not None and os.path.exists(os.path.join(CACHE, "dsm2025.bin"))
top = np.fromfile(os.path.join(CACHE, "dsm2025.bin" if new else "dsm1.bin"), dtype="<f4").reshape(N, N)
level = town.get("water_2025_m") if town.get("water_2025_m") is not None and os.path.exists(os.path.join(CACHE, "dsm2025.bin")) else water
block = np.zeros((N, N), bool)
def box(xs, ys, grow):
    return int(max(0, min(xs) - grow)), int(min(N, max(xs) + grow + 1)), int(max(0, N - max(ys) - grow)), int(min(N, N - min(ys) + grow + 1))
def inside(px, py, poly):
    c = np.zeros(px.shape, bool); n = len(poly)
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        if y0 == y1: continue
        c ^= ((y0 > py) != (y1 > py)) & (px < (x1 - x0) * (py - y0) / (y1 - y0) + x0)
    return c
for b in town["buildings"]:                              # outlines, grown by 2 m (7 m round a floating home: its decks, floats and skiffs are not boats)
    xs = [p[0] for p in b["p"]]; ys = [p[1] for p in b["p"]]; c0, c1, r0, r1 = box(xs, ys, 8)
    if c1 <= c0 or r1 <= r0: continue
    cc, rr = np.meshgrid(np.arange(c0, c1) + 0.5, N - (np.arange(r0, r1) + 0.5))
    m = inside(cc, rr, b["p"])
    for _ in range(7 if b["k"] == "houseboat" else 2): m2 = m.copy(); m2[1:] |= m[:-1]; m2[:-1] |= m[1:]; m2[:, 1:] |= m[:, :-1]; m2[:, :-1] |= m[:, 1:]; m = m2
    block[r0:r1, c0:c1] |= m
for p in town["piers"]:                                  # piers and floats, 2.5 m either side of their line
    pts = p["p"] + ([p["p"][0]] if p.get("area") else [])
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        for t in np.linspace(0, 1, n):
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t; c, r = int(x), int(N - y)
            block[max(0, r - 2):r + 3, max(0, c - 2):c + 3] = True
    if p.get("area"):
        xs = [q[0] for q in p["p"]]; ys = [q[1] for q in p["p"]]; c0, c1, r0, r1 = box(xs, ys, 1)
        if c1 > c0 and r1 > r0:
            cc, rr = np.meshgrid(np.arange(c0, c1) + 0.5, N - (np.arange(r0, r1) + 0.5)); block[r0:r1, c0:c1] |= inside(cc, rr, p["p"])
up = np.nan_to_num(top - level, nan=0.0)
mask = wet & ~block & (up >= 0.8) & (up < 40)
seen = np.zeros((N, N), bool); out = []
rows, cols = np.nonzero(mask)
for r0, c0 in zip(rows.tolist(), cols.tolist()):
    if seen[r0, c0]: continue
    stack = [(r0, c0)]; seen[r0, c0] = True; cells = []
    while stack:
        r, c = stack.pop(); cells.append((r, c))
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                rr, cc = r + dr, c + dc
                if 0 <= rr < N and 0 <= cc < N and mask[rr, cc] and not seen[rr, cc]: seen[rr, cc] = True; stack.append((rr, cc))
    if not 6 <= len(cells) <= 500: continue
    a = np.array(cells, float); x = a[:, 1] + 0.5; y = N - (a[:, 0] + 0.5); mx, my = x.mean(), y.mean()
    cov = np.cov(np.stack([x - mx, y - my])); val, vec = np.linalg.eigh(cov); ax = vec[:, 1]
    along = (x - mx) * ax[0] + (y - my) * ax[1]; across = -(x - mx) * ax[1] + (y - my) * ax[0]
    length = along.max() - along.min() + 1; width = across.max() - across.min() + 1
    if length > 45 or length < 3.5: continue
    h = float(up[a[:, 0].astype(int), a[:, 1].astype(int)].max())
    out.append((mx, my, length, min(width, length), h, np.degrees(np.arctan2(ax[1], ax[0])) % 180))
o = np.array([[round(x * 10), round(y * 10), round(l * 10), round(w * 10), round(min(h, 40) * 10), round(d * 10) % 1800] for x, y, l, w, h, d in out], dtype="<u2")
o.tofile(os.path.join(VIEW, "data", "boats.bin"))
L = np.array([b[2] for b in out]); H = np.array([b[4] for b in out])
print(f"from the {2025 if new else 2018} flight, water at {level:.2f} m;", f"boats {len(out)}: length median {np.median(L):.1f} m, nine tenths under {np.percentile(L, 90):.1f} m; tallest return median {np.median(H):.1f} m, {int((H > 6).sum())} over 6 m (masts)")
