#!/usr/bin/env python3
"""Cut the view's data from the downloads in ../cache into ./data.

Needs GDAL's command-line tools and numpy. Inputs (see cache/README.md for where they come from):
  cache/dem_*.tif   USGS 3DEP one-metre elevation tiles (public domain)
  the town's buildings, roads, shore works and waterways, read from the data warehouse (data.earthlight.cloud;
                    OpenStreetMap, ODbL, with Microsoft's height estimates, CDLA Permissive 2.0)
Outputs:
  data/ground.bin   elevation, little-endian int16 decimetres, row-major from the north edge
  data/town.json    the window, buildings, roads and piers in metres east and north of the window's south-west corner
Heights: a building arrives from the warehouse with one height: its OpenStreetMap `height` or `building:levels`
x 3 m where tagged (t = 1), else Microsoft's estimate for the footprint at the same place (t = 2), else a guess from
its neighbours or its kind and size (t = 0). The lidar then replaces what it can measure (t = 3 or 4).
"""
import json, subprocess, sys, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); CACHE = os.path.join(HERE, "..", "cache"); OUT = os.path.join(HERE, "data")
WIN = json.load(open(os.path.join(HERE, "window.json")))                 # the window: UTM zone 10N (EPSG:26910), metres
E0, N0, E1, N1, RES = WIN["e0"], WIN["n0"], WIN["e1"], WIN["n1"], WIN["res"]
os.makedirs(OUT, exist_ok=True)

def sh(cmd): subprocess.run(cmd, shell=True, check=True, cwd=CACHE)

# ground: the 2018 survey everywhere; nodata (open bay) becomes the flattened water level
vrts = []
for f in ["dem_y419_2018", "dem_y419_2018q", "dem_y420_2018"]:
    nd = subprocess.run(f"gdalinfo {f}.tif | grep -m1 NoData | sed 's/.*=//'", shell=True, cwd=CACHE, capture_output=True, text=True).stdout.strip()
    sh(f'gdalbuildvrt -q -overwrite -srcnodata "{nd}" -vrtnodata -9999 {f}.vrt {f}.tif'); vrts.append(f + ".vrt")
sh(f"gdalwarp -q -overwrite -te {E0} {N0} {E1} {N1} -tr {RES} {RES} -r average -dstnodata -9999 -ot Float32 {' '.join(vrts)} town.tif")
sh("gdal_translate -q -of ENVI -ot Float32 town.tif town.bin")
nx, ny = (E1 - E0) // RES, (N1 - N0) // RES
g = np.fromfile(os.path.join(CACHE, "town.bin"), dtype="<f4").reshape(ny, nx)
water = float(np.min(g[g > -9999])); g[g <= -9999] = water
np.round(g * 10).astype("<i2").tofile(os.path.join(OUT, "ground.bin"))

# ---- the town's features, from the data warehouse ---------------------------------------------------------
# https://data.earthlight.cloud (made with github.com/anselm/esimv1-data) holds this window's buildings, roads,
# shore works and waterways as products with fixed addresses; a product is never changed once made, so the four
# lines below fix what this script reads. The buildings are OpenStreetMap's outlines, each already given one
# height and a note of where it came from: the map's own `height` or `building:levels` tag (t = 1), Microsoft's
# estimate for the footprint at the same place (t = 2), or a guess from neighbouring buildings or the building's
# kind and size (t = 0). The lidar below then replaces whichever of those it can measure. ESIM_DATA_STORE may
# name another copy of the store, a folder or an address.
import gzip, urllib.request
STORE = os.environ.get("ESIM_DATA_STORE", "https://data.earthlight.cloud").rstrip("/")
PRODUCTS = {
    "buildings": "buildings/massing/sausalito/2026-11-27/buildings.geojson.gz",
    "roads": "roads/osm/sausalito/2026-11-28/roads.geojson.gz",
    "shore": "shore/osm/sausalito/2026-11-28/shore.geojson.gz",
    "water": "water/osm/sausalito/2026-11-28/water.geojson.gz",
}
def product(key):
    rel = PRODUCTS[key]; kept = os.path.join(CACHE, "warehouse", rel.replace("/", "_"))
    if not os.path.exists(kept):
        os.makedirs(os.path.dirname(kept), exist_ok=True)
        if STORE.startswith("http"): data = urllib.request.urlopen(urllib.request.Request(STORE + "/" + rel, headers={"User-Agent": "sausalito-model-prepare/1"}), timeout=120).read()
        else: data = open(os.path.join(STORE, rel), "rb").read()
        open(kept, "wb").write(data)
    return json.load(gzip.open(kept))["features"]
feats = {k: product(k) for k in PRODUCTS}
def line_of(f): return f["geometry"]["coordinates"][0] if f["geometry"]["type"] == "Polygon" else f["geometry"]["coordinates"]
# project every vertex in one call
allf = [f for k in PRODUCTS for f in feats[k]]
pts = "\n".join(f"{p[0]} {p[1]}" for f in allf for p in line_of(f))
out = subprocess.run("gdaltransform -s_srs EPSG:4326 -t_srs EPSG:26910", shell=True, input=pts, capture_output=True, text=True, check=True).stdout.split("\n")
it = iter(out)
def local(f):
    xy = []
    for _ in line_of(f): a = next(it).split(); xy.append([round(float(a[0]) - E0, 1), round(float(a[1]) - N0, 1)])
    return xy
def inside(xy): return any(0 <= x <= E1 - E0 and 0 <= y <= N1 - N0 for x, y in xy)
T = {"survey": 1, "tag": 1, "levels": 1, "ml": 2}
buildings, roads, piers, creeks = [], [], [], []
for f in feats["buildings"]:
    xy = local(f); q = f["properties"]
    if not inside(xy) or len(xy) < 4 or q.get("height_m") is None: continue
    buildings.append({"k": q.get("kind") or "yes", "h": round(q["height_m"], 1), "t": T.get(q.get("height_source"), 0), "p": xy[:-1] if xy[0] == xy[-1] else xy})
for f in feats["roads"]:
    xy = local(f); q = f["properties"]
    if not inside(xy): continue
    r = {"k": q["class"], "n": q.get("name") or "", "p": xy}
    if q.get("lanes"): r["l"] = int(q["lanes"])               # lanes, where the map says
    if q.get("oneway"): r["o"] = 1
    if q.get("bridge"): r["b"] = 1
    if q.get("tunnel"): r["u"] = 1
    roads.append(r)
for f in feats["shore"]:
    xy = local(f)
    if inside(xy) and f["properties"]["kind"] == "pier": piers.append({"area": xy[0] == xy[-1] and len(xy) > 3, "p": xy})
for f in feats["water"]:
    xy = local(f); q = f["properties"]
    if inside(xy): creeks.append({"k": q["kind"], "n": q.get("name") or "", "u": 1 if q.get("tunnel") else 0, "p": xy})
tagged = sum(b["t"] == 1 for b in buildings); from_ms = sum(b["t"] == 2 for b in buildings)
print(f"warehouse: {len(buildings)} buildings ({tagged} with a tagged height, {from_ms} with Microsoft's, {len(buildings) - tagged - from_ms} guessed), {len(roads)} roads, {len(piers)} piers, {len(creeks)} waterways")

# ---- heights measured from the lidar point cloud ----------------------------------------------------------
# cache/dsm1.bin is the highest lidar return in each one-metre cell (view/tools/lidar_surface.py, from the
# 2018 survey's points, US Geological Survey, public domain). Less the one-metre bare ground it is the height
# of whatever stands there. A building's height is the median of that over the cells inside its footprint
# that stand 2 m or more above the ground, when they are at least three tenths of the footprint; so a
# pitched roof is drawn at about its mid-slope and a tree over one corner does not lift the box.
# A footprint where the lidar saw nothing standing (built since 2018, or drawn off its true place) keeps
# the height it had.
N1M = E1 - E0; above = None; bmask = None; from_lidar = 0
dsm_path = os.path.join(CACHE, "dsm1.bin")
if os.path.exists(dsm_path):
    if not os.path.exists(os.path.join(CACHE, "dem1.bin")):
        sh(f"gdalwarp -q -overwrite -te {E0} {N0} {E1} {N1} -tr 1 1 -r bilinear -dstnodata -9999 -ot Float32 {' '.join(vrts)} dem1.tif")
        sh("gdal_translate -q -of ENVI -ot Float32 dem1.tif dem1.bin")
    dem1 = np.fromfile(os.path.join(CACHE, "dem1.bin"), dtype="<f4").reshape(N1M, N1M)
    dem1 = np.where(dem1 < -1000, water, dem1)
    top = np.fromfile(dsm_path, dtype="<f4").reshape(N1M, N1M); newer = np.zeros((N1M, N1M), bool); water25 = None
    # A newer flight where there is one: NOAA's 2025 San Francisco Bay and Delta lidar (dataset 14673, public
    # domain; flown 27 September 2025 here, three tiles on 30 August), gridded the same way into dsm2025.bin.
    # It covers the town and the shore but not the western hills, so inside its tiles the surface is 2025's
    # and elsewhere it stays 2018's. The bare ground stays the 2018 survey's everywhere. Over water inside the
    # tiles, heights are taken above the water as that flight saw it (the median of its returns over open
    # water), since a floating home rides the tide.
    p25 = os.path.join(CACHE, "dsm2025.bin"); boxes = os.path.join(CACHE, "lidar2025", "boxes.json")
    if os.path.exists(p25) and os.path.exists(boxes):
        top25 = np.fromfile(p25, dtype="<f4").reshape(N1M, N1M)
        for _, x0, y0, x1, y1 in json.load(open(boxes)):
            c0, c1, r0, r1 = int(max(0, x0 - E0)), int(min(N1M, x1 - E0)), int(max(0, N1 - y1)), int(min(N1M, N1 - y0))
            if c1 > c0 and r1 > r0: newer[r0:r1, c0:c1] = True
        wet1 = np.repeat(np.repeat(g <= water + 0.06, RES, axis=0), RES, axis=1)
        open_water = wet1 & newer & np.isfinite(top25) & (top25 < water + 3.5)
        water25 = float(np.median(top25[open_water])); top = np.where(newer, top25, top); dem1 = np.where(wet1 & newer, water25, dem1)
        print(f"2025 lidar: {newer.mean() * 100:.0f}% of the window is inside its tiles; its water stood at {water25:.2f} m NAVD88 (the 2018 survey's lowest ground is {water:.2f} m)")
    above = top - dem1                                                           # NaN where no return fell
    bmask = np.zeros((N1M, N1M), bool); pairs = []
    for b in buildings:
        xs = np.array([q[0] for q in b["p"]]); ys = N1M - np.array([q[1] for q in b["p"]])     # rows count from the north edge
        c0, c1, r0, r1 = int(max(0, np.floor(xs.min()))), int(min(N1M, np.ceil(xs.max()))), int(max(0, np.floor(ys.min()))), int(min(N1M, np.ceil(ys.max())))
        if c1 <= c0 or r1 <= r0: continue
        gx, gy = np.meshgrid(np.arange(c0, c1) + 0.5, np.arange(r0, r1) + 0.5); ins = np.zeros(gx.shape, bool)
        for i in range(len(xs)):
            x1, y1, x2, y2 = xs[i], ys[i], xs[(i + 1) % len(xs)], ys[(i + 1) % len(xs)]
            if y1 == y2: continue
            ins ^= ((y1 > gy) != (y2 > gy)) & (gx < (x2 - x1) * (gy - y1) / (y2 - y1) + x1)
        bmask[r0:r1, c0:c1] |= ins
        v = above[r0:r1, c0:c1][ins]; v = v[np.isfinite(v)]
        if len(v) < 4: continue
        up = v[v >= 2.0]
        if len(up) < 0.3 * ins.sum(): continue
        h = float(np.median(up)); pairs.append((b["t"], b["h"], h))
        b["h"] = round(min(h, 80.0), 1); b["t"] = 4 if newer[min(N1M - 1, (r0 + r1) // 2), min(N1M - 1, (c0 + c1) // 2)] else 3; from_lidar += 1
    def versus(kind, name):
        d = np.array([o - l for t, o, l in pairs if t == kind])
        if len(d): print(f"  {name} less lidar, {len(d)} buildings: median {np.median(d):+.1f} m, half within {np.percentile(np.abs(d), 50):.1f} m, nine tenths within {np.percentile(np.abs(d), 90):.1f} m")
    hs = sorted(b["h"] for b in buildings if b["t"] >= 3)
    print(f"heights: {sum(b['t'] == 4 for b in buildings)} from the 2025 flight; {from_lidar} of {len(buildings)} measured from lidar; median {hs[len(hs)//2]} m, 95th percentile {hs[int(len(hs)*.95)]} m, tallest {hs[-1]} m")
    versus(2, "Microsoft's estimate"); versus(1, "OpenStreetMap's tag"); versus(0, "the placeholder")
    left = [b for b in buildings if b["t"] < 3]
    print(f"  not measured: {len(left)} ({sum(b['k'] == 'houseboat' for b in left)} houseboats); of all {sum(b['k'] == 'houseboat' for b in buildings)} houseboats {sum(b['k'] == 'houseboat' and b['t'] >= 3 for b in buildings)} measured")
tagged = sum(b["t"] == 1 for b in buildings); from_ms = sum(b["t"] == 2 for b in buildings)

# Bridge decks: a road the map calls a bridge is not on the bare ground. Its deck's height at each vertex is
# read from the lidar's top surface (the median of the 5 m around the vertex), so the page can lift it.
decks = 0
if above is not None:
    top1 = above + dem1
    for r in roads:
        if not r.get("b"): continue
        z = []
        for x, y in r["p"]:
            c, rr = int(x), int(N1M - y)
            w = top1[max(0, rr - 2):rr + 3, max(0, c - 2):c + 3]; w = w[np.isfinite(w)]
            z.append(round(float(np.median(w)), 1) if len(w) else None)
        if all(v is not None for v in z): r["z"] = z; decks += 1
    print(f"bridges: {sum(1 for r in roads if r.get('b'))} road pieces are bridges, {decks} with a deck height from lidar; {sum(1 for r in roads if r.get('u'))} are tunnels")

# ---- where rain runs: drainage lines computed from the ground ------------------------------------------------
# Every cell of the four-metre ground is given the neighbour its water would leave by, found by letting water
# rise from the bay and the window's edges and noting from which side each cell is first reached (the
# "priority flood" of Barnes, Lehman and Mulla 2014), which also carries water across hollows. The area draining
# through each cell is then summed downhill. Lines are drawn where 2 hectares or more drain through. This is the
# bare ground's shape: in town most of these run in pipes and culverts, and no pipe is known to this file.
import heapq
flat = g.ravel(); n_cells = flat.size; down = np.full(n_cells, -1, np.int64); done = np.zeros(n_cells, bool); order = []
sea = water + 0.07; heap = []
for k in np.nonzero(flat <= sea)[0]: done[k] = True
edge = np.zeros((ny, nx), bool); edge[0, :] = edge[-1, :] = edge[:, 0] = edge[:, -1] = True
seeds = np.nonzero((flat <= sea) | edge.ravel())[0]
for k in seeds: done[k] = True; heapq.heappush(heap, (float(flat[k]), int(k)))
NB = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
while heap:
    z, k = heapq.heappop(heap); order.append(k); j, i = divmod(k, nx)
    for dj, di in NB:
        jj, ii = j + dj, i + di
        if 0 <= jj < ny and 0 <= ii < nx:
            m = jj * nx + ii
            if not done[m]: done[m] = True; down[m] = k; heapq.heappush(heap, (max(float(flat[m]), z + 1e-4), m))
acc = np.ones(n_cells, np.float64)
for k in reversed(order):
    if down[k] >= 0: acc[down[k]] += acc[k]
CH = 2.0 * 10000 / (RES * RES)                             # cells in 2 hectares
chan = (acc >= CH) & (flat > sea); has_up = np.zeros(n_cells, bool)
for k in np.nonzero(chan)[0]:
    if down[k] >= 0 and chan[down[k]]: has_up[down[k]] = True
drains, used = [], np.zeros(n_cells, bool)
for k in sorted(np.nonzero(chan & ~has_up)[0], key=lambda c: -acc[c]):
    path, c = [], int(k)
    while c >= 0 and flat[c] > sea:
        path.append(c)
        if used[c]: break
        used[c] = True; c = int(down[c])
    if c >= 0 and flat[c] <= sea: path.append(c)
    if len(path) >= 6:
        pts = [[round((c % nx + 0.5) * RES, 1), round((ny - (c // nx) - 0.5) * RES, 1)] for c in path[::2] + [path[-1]]]
        drains.append({"a": round(float(acc[path[-2] if len(path) > 1 else path[-1]]) * RES * RES / 10000, 1), "p": pts})
print(f"drainage: {len(drains)} lines where 2 ha or more drain through; the largest carries {max(d['a'] for d in drains):.0f} ha; {len(creeks)} mapped waterways ({sum(c['u'] for c in creeks)} in culverts or tunnels)")

json.dump({"creeks": creeks, "drains": drains, "window": {"epsg": 26910, "e0": E0, "n0": N0, "e1": E1, "n1": N1, "res": RES, "nx": nx, "ny": ny, "water_m": round(water, 2), "anchor": WIN["anchor"], "south": WIN["south"], "west": WIN["west"], "north": WIN["north"], "east": WIN["east"]},
           "osm_base": "2026-11-28", "products": PRODUCTS, "heights_tagged": tagged, "heights_microsoft": from_ms, "heights_lidar": from_lidar, "heights_lidar_2025": sum(b["t"] == 4 for b in buildings), "water_2025_m": None if 'water25' not in dir() or water25 is None else round(water25, 2),
           "buildings": buildings, "roads": roads, "piers": piers}, open(os.path.join(OUT, "town.json"), "w"), separators=(",", ":"))
print(f"ground {nx}x{ny} at {RES} m, water level {water:.2f} m; {len(buildings)} buildings ({tagged} with a tagged height), {len(roads)} roads, {len(piers)} piers")

# ---- trees ------------------------------------------------------------------------------------------------
# From the lidar surface when it is there: what stands 3 m or more above the ground outside building
# footprints (grown by 2 m) and off the water. Otherwise from cache/chm1.bin, the eight-county canopy height
# model (feet; zenith.cnr.berkeley.edu), whose terms of use are not stated, so its trees are not committed.
# One tree per 7 m cell, at the highest point in the cell, where at least a fifth of the cell stands 2 m up
# (a power line or a mast is a thin thing and is left out). A picture of the canopy, not an inventory of trees.
chm_path = os.path.join(CACHE, "chm1.bin"); N = N1M; c = None
if above is not None:
    c = np.nan_to_num(above, nan=0.0); block = bmask.copy(); source = "lidar"
    for _ in range(2):                                     # grow the footprints by two cells
        g2 = block.copy(); g2[1:] |= block[:-1]; g2[:-1] |= block[1:]; g2[:, 1:] |= block[:, :-1]; g2[:, :-1] |= block[:, 1:]; block = g2
elif os.path.exists(chm_path):
    c = np.fromfile(chm_path, dtype="<f4").reshape(N, N) * 0.3048; block = np.zeros((N, N), bool); source = "canopy model"
    for b in buildings:                                    # footprints' boxes, grown by 2 m
        xs = [p[0] for p in b["p"]]; ys = [N - p[1] for p in b["p"]]
        x0, x1, y0, y1 = int(max(0, min(xs) - 2)), int(min(N, max(xs) + 3)), int(max(0, min(ys) - 2)), int(min(N, max(ys) + 3))
        if x1 > x0 and y1 > y0: block[y0:y1, x0:x1] = True
if c is not None:
    gfull = np.repeat(np.repeat(g, RES, axis=0), RES, axis=1)   # the 4 m ground at 1 m, for the water mask
    wet = gfull <= water + 0.06
    for _ in range(3):                                     # and three cells from the water's edge: boats, floats, pilings
        w2 = wet.copy(); w2[1:] |= wet[:-1]; w2[:-1] |= wet[1:]; w2[:, 1:] |= wet[:, :-1]; w2[:, :-1] |= wet[:, 1:]; wet = w2
    c[block | wet] = 0
    CELL = 7; n = N // CELL
    v = c[: n * CELL, : n * CELL].reshape(n, CELL, n, CELL).transpose(0, 2, 1, 3).reshape(n, n, CELL * CELL)
    arg = v.argmax(axis=2); top = v.max(axis=2); cover = (v >= 2.0).mean(axis=2)
    jj, ii = np.nonzero((top >= 3.0) & (cover >= 0.2))
    px = ii * CELL + arg[jj, ii] % CELL + 0.5; py = jj * CELL + arg[jj, ii] // CELL + 0.5
    h = np.minimum(top[jj, ii], 60.0)
    out = np.stack([np.round(px * 10), np.round((N - py) * 10), np.round(h * 10)], axis=1).astype("<u2")   # x east, y north, height: decimetres
    out.tofile(os.path.join(OUT, "trees.bin"))
    print(f"trees {len(out)} from the {source} (3 m or more), median height {np.median(h):.1f} m, tallest {h.max():.1f} m")
