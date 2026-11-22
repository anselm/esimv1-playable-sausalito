#!/usr/bin/env python3
"""Cut the view's data from the downloads in ../cache into ./data.

Needs GDAL's command-line tools and numpy. Inputs (see cache/README.md for where they come from):
  cache/dem_*.tif   USGS 3DEP one-metre elevation tiles (public domain)
  cache/osm_raw.json  an Overpass answer for buildings, highways and piers (OpenStreetMap, ODbL)
Outputs:
  data/ground.bin   elevation, little-endian int16 decimetres, row-major from the north edge
  data/town.json    the window, buildings, roads and piers in metres east and north of the window's south-west corner
Heights: a building's height is its OpenStreetMap `height` or `building:levels` x 3 m where tagged; otherwise a
placeholder by kind. About 40 of 4,455 buildings are tagged, so nearly every height in the view is a placeholder.
"""
import json, subprocess, sys, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); CACHE = os.path.join(HERE, "..", "cache"); OUT = os.path.join(HERE, "data")
E0, N0, E1, N1, RES = 542800, 4187800, 547300, 4192300, 4      # UTM zone 10N (EPSG:26910), metres
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
    elif "highway" in t: roads.append({"k": t["highway"], "n": t.get("name", ""), "p": xy})
    elif t.get("man_made") == "pier": piers.append({"area": xy[0] == xy[-1] and len(xy) > 3, "p": xy})
json.dump({"window": {"epsg": 26910, "e0": E0, "n0": N0, "e1": E1, "n1": N1, "res": RES, "nx": nx, "ny": ny, "water_m": round(water, 2)},
           "osm_base": d.get("osm3s", {}).get("timestamp_osm_base"), "heights_tagged": tagged,
           "buildings": buildings, "roads": roads, "piers": piers}, open(os.path.join(OUT, "town.json"), "w"), separators=(",", ":"))
print(f"ground {nx}x{ny} at {RES} m, water level {water:.2f} m; {len(buildings)} buildings ({tagged} with a tagged height), {len(roads)} roads, {len(piers)} piers")

# ---- trees, from a canopy height model -------------------------------------------------------------------
# cache/chm1.bin is 4500 x 4500 float32 at 1 m over the same window, heights in feet above ground, exported from
# the eight-county canopy height service at zenith.cnr.berkeley.edu (Marin's part is from lidar flown in 2018).
# In Marin it holds vegetation; buildings were classified out, so it cannot give building heights.
# One tree per 7 m cell where the canopy's top is 3 m or more, placed at the highest point in the cell, away
# from building footprints and water. This is a picture of the canopy, not an inventory of trees.
chm_path = os.path.join(CACHE, "chm1.bin")
if os.path.exists(chm_path):
    N = 4500; c = np.fromfile(chm_path, dtype="<f4").reshape(N, N) * 0.3048
    block = np.zeros((N, N), bool)
    for b in buildings:                                    # footprints, grown by 2 m, as a mask
        xs = [p[0] for p in b["p"]]; ys = [N - p[1] for p in b["p"]]
        x0, x1, y0, y1 = int(max(0, min(xs) - 2)), int(min(N, max(xs) + 3)), int(max(0, min(ys) - 2)), int(min(N, max(ys) + 3))
        if x1 > x0 and y1 > y0: block[y0:y1, x0:x1] = True
    gfull = np.repeat(np.repeat(g, RES, axis=0), RES, axis=1)   # the 4 m ground at 1 m, for the water mask
    block |= gfull <= water + 0.06
    c[block] = 0
    CELL = 7; n = N // CELL
    v = c[: n * CELL, : n * CELL].reshape(n, CELL, n, CELL).transpose(0, 2, 1, 3).reshape(n, n, CELL * CELL)
    arg = v.argmax(axis=2); top = v.max(axis=2)
    jj, ii = np.nonzero(top >= 3.0)
    px = ii * CELL + arg[jj, ii] % CELL + 0.5; py = jj * CELL + arg[jj, ii] // CELL + 0.5
    h = np.minimum(top[jj, ii], 60.0)
    out = np.stack([np.round(px * 10), np.round((N - py) * 10), np.round(h * 10)], axis=1).astype("<u2")   # x east, y north, height: decimetres
    out.tofile(os.path.join(OUT, "trees.bin"))
    print(f"trees {len(out)} (canopy 3 m or more), median height {np.median(h):.1f} m, tallest {h.max():.1f} m")
