#!/usr/bin/env python3
"""Cut the view's data from the downloads in ../cache into ./data.

Needs GDAL's command-line tools and numpy. Inputs (see cache/README.md for where they come from):
  cache/dem_*.tif   USGS 3DEP one-metre elevation tiles (public domain)
  cache/osm_raw.json  an Overpass answer for buildings, highways and piers (OpenStreetMap, ODbL)
Outputs:
  data/ground.bin   elevation, little-endian int16 decimetres, row-major from the north edge
  data/town.json    the window, buildings, roads and piers in metres east and north of the window's south-west corner
Heights: a building's height is its OpenStreetMap `height` or `building:levels` x 3 m where tagged (t = 1), else
Microsoft's estimate for the footprint at the same place (t = 2), else a placeholder by kind (t = 0).
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

# OpenStreetMap: project every vertex in one call
d = json.load(open(os.path.join(CACHE, "osm_raw.json")))
ways = [e for e in d["elements"] if e["type"] == "way" and len(e.get("geometry", [])) >= 2]
pts = "\n".join(f'{p["lon"]} {p["lat"]}' for e in ways for p in e["geometry"])
out = subprocess.run("gdaltransform -s_srs EPSG:4326 -t_srs EPSG:26910", shell=True, input=pts, capture_output=True, text=True, check=True).stdout.split("\n")
it = iter(out)
def num(s):
    try: return float(str(s).split()[0].replace("m", ""))
    except Exception: return None
PLACEHOLDER = {"houseboat": 4.5, "shed": 3, "garage": 3, "garages": 3, "roof": 3, "carport": 3, "commercial": 8, "retail": 6, "industrial": 9, "warehouse": 9, "apartments": 10, "hotel": 10, "church": 10, "religious": 10, "school": 7}
buildings, roads, piers, tagged = [], [], [], 0
for e in ways:
    xy = []
    for _ in e["geometry"]:
        a = next(it).split(); xy.append([round(float(a[0]) - E0, 1), round(float(a[1]) - N0, 1)])
    t = e.get("tags", {})
    inside = any(0 <= x <= E1 - E0 and 0 <= y <= N1 - N0 for x, y in xy)
    if not inside: continue
    if "building" in t:
        if len(xy) < 4: continue
        h = num(t.get("height")); lv = num(t.get("building:levels"))
        if h is None and lv is not None: h = lv * 3.0
        known = h is not None
        if not known: h = PLACEHOLDER.get(t["building"], 6.5)
        tagged += known
        buildings.append({"k": t["building"], "h": round(h, 1), "t": 1 if known else 0, "p": xy[:-1] if xy[0] == xy[-1] else xy})
    elif "highway" in t:
        r = {"k": t["highway"], "n": t.get("name", ""), "p": xy}
        ln = num(t.get("lanes"))
        if ln: r["l"] = int(ln)                                   # lanes, where the map says
        if t.get("oneway") == "yes": r["o"] = 1
        if t.get("bridge") and t.get("bridge") != "no": r["b"] = 1
        if t.get("tunnel") and t.get("tunnel") != "no": r["u"] = 1
        roads.append(r)
    elif t.get("man_made") == "pier": piers.append({"area": xy[0] == xy[-1] and len(xy) > 3, "p": xy})
# ---- heights from Microsoft's Global ML Building Footprints (CDLA Permissive 2.0) -----------------------------
# cache/ms_qk023010203.csv.gz is the quadkey file covering the window (one GeoJSON feature per line, height in
# metres, -1 where Microsoft has none; listed in its dataset-links.csv). Microsoft estimated these heights; the
# method and date are not stated per building. An OpenStreetMap building takes the height of the Microsoft
# footprint that contains its centre, or failing that the nearest one within 12 m.
import gzip
ms_path = os.path.join(CACHE, "ms_qk023010203.csv.gz"); from_ms = 0
if os.path.exists(ms_path):
    ms = []
    for line in gzip.open(ms_path, "rt"):
        f = json.loads(line); hgt = f["properties"].get("height", -1); ring = f["geometry"]["coordinates"][0]
        if hgt is None or hgt <= 0: continue
        lon, lat = ring[0]
        if not (-122.52 <= lon <= -122.455 and 37.83 <= lat <= 37.885): continue
        ms.append((hgt, ring))
    pts = "\n".join(f"{x} {y}" for _, ring in ms for x, y in ring)
    proj = iter(subprocess.run("gdaltransform -s_srs EPSG:4326 -t_srs EPSG:26910", shell=True, input=pts, capture_output=True, text=True, check=True).stdout.split("\n"))
    polys = []
    for hgt, ring in ms:
        xy = []
        for _ in ring: a = next(proj).split(); xy.append((float(a[0]) - E0, float(a[1]) - N0))
        polys.append((hgt, xy, sum(p[0] for p in xy) / len(xy), sum(p[1] for p in xy) / len(xy)))
    grid = {}
    for i, (_, xy, cx, cy) in enumerate(polys): grid.setdefault((int(cx // 50), int(cy // 50)), []).append(i)
    def inside(x, y, xy):
        c = False; n = len(xy)
        for i in range(n):
            x1, y1 = xy[i]; x2, y2 = xy[(i + 1) % n]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
        return c
    for b in buildings:
        if b["t"]: continue
        cx = sum(p[0] for p in b["p"]) / len(b["p"]); cy = sum(p[1] for p in b["p"]) / len(b["p"])
        near = [i for dx in (-1, 0, 1) for dy in (-1, 0, 1) for i in grid.get((int(cx // 50) + dx, int(cy // 50) + dy), [])]
        hit = next((i for i in near if inside(cx, cy, polys[i][1])), None)
        if hit is None and near:
            j = min(near, key=lambda i: (polys[i][2] - cx) ** 2 + (polys[i][3] - cy) ** 2)
            if (polys[j][2] - cx) ** 2 + (polys[j][3] - cy) ** 2 <= 144: hit = j
        if hit is not None: b["h"] = round(float(polys[hit][0]), 1); b["t"] = 2; from_ms += 1
    hs = sorted(b["h"] for b in buildings if b["t"] == 2)
    print(f"heights: {from_ms} of {len(buildings)} from Microsoft ({len(polys)} Microsoft footprints with a height in the window); median {hs[len(hs)//2]} m, 95th percentile {hs[int(len(hs)*.95)]} m, tallest {hs[-1]} m")

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
    above = np.fromfile(dsm_path, dtype="<f4").reshape(N1M, N1M) - dem1          # NaN where no return fell
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
        b["h"] = round(min(h, 80.0), 1); b["t"] = 3; from_lidar += 1
    def versus(kind, name):
        d = np.array([o - l for t, o, l in pairs if t == kind])
        if len(d): print(f"  {name} less lidar, {len(d)} buildings: median {np.median(d):+.1f} m, half within {np.percentile(np.abs(d), 50):.1f} m, nine tenths within {np.percentile(np.abs(d), 90):.1f} m")
    hs = sorted(b["h"] for b in buildings if b["t"] == 3)
    print(f"heights: {from_lidar} of {len(buildings)} measured from lidar; median {hs[len(hs)//2]} m, 95th percentile {hs[int(len(hs)*.95)]} m, tallest {hs[-1]} m")
    versus(2, "Microsoft's estimate"); versus(1, "OpenStreetMap's tag"); versus(0, "the placeholder")
    left = [b for b in buildings if b["t"] != 3]
    print(f"  not measured: {len(left)} ({sum(b['k'] == 'houseboat' for b in left)} houseboats); of all {sum(b['k'] == 'houseboat' for b in buildings)} houseboats {sum(b['k'] == 'houseboat' and b['t'] == 3 for b in buildings)} measured")
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

json.dump({"window": {"epsg": 26910, "e0": E0, "n0": N0, "e1": E1, "n1": N1, "res": RES, "nx": nx, "ny": ny, "water_m": round(water, 2), "anchor": WIN["anchor"]},
           "osm_base": d.get("osm3s", {}).get("timestamp_osm_base"), "heights_tagged": tagged, "heights_microsoft": from_ms, "heights_lidar": from_lidar,
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
