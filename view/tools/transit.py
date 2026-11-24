#!/usr/bin/env python3
"""The timetable as things that move: view/data/transit.json from Golden Gate Transit's public schedule feed.

Downloads the feed (GTFS, https://realtime.goldengate.org/gtfsstatic/GTFSTransitData.zip) to ../cache/gtfs.zip
unless it is there, and keeps every trip whose path crosses the view's window: the ferries and the buses.
For each, the path inside the window in window metres with the distance along the whole path at each
vertex, and the times at the stops either side of and inside the window. Between two stops a vehicle is
taken to move at a steady speed along the path, which is the timetable's account and not a tracked position.
A trip runs on the weekdays its service calendar gives; the feed's exceptions for holidays are left out.
Run: python3 view/tools/transit.py        (standard library only)
"""
import csv, io, json, math, os, sys, urllib.request, zipfile
HERE = os.path.dirname(os.path.abspath(__file__)); VIEW = os.path.join(HERE, ".."); CACHE = os.path.join(VIEW, "..", "cache")
URL = "https://realtime.goldengate.org/gtfsstatic/GTFSTransitData.zip"; ZIP = os.path.join(CACHE, "gtfs.zip")
W = json.load(open(os.path.join(VIEW, "window.json"))); E0, N0, E1, N1 = W["e0"], W["n0"], W["e1"], W["n1"]
if not os.path.exists(ZIP):
    req = urllib.request.Request(URL, headers={"User-Agent": "timetable-reader/0.1"}); open(ZIP, "wb").write(urllib.request.urlopen(req, timeout=120).read())
z = zipfile.ZipFile(ZIP)
def rows(name): return csv.DictReader(io.TextIOWrapper(z.open(name), "utf-8-sig"))
def utm10(lat, lon):                                       # WGS84 to UTM zone 10 north (Krueger series)
    a, f, k0 = 6378137.0, 1 / 298.257223563, 0.9996; e2 = f * (2 - f); n = f / (2 - f); phi = math.radians(lat); lam = math.radians(lon + 123)
    A = a / (1 + n) * (1 + n * n / 4 + n ** 4 / 64); al = [n / 2 - 2 * n * n / 3 + 5 * n ** 3 / 16, 13 * n * n / 48 - 3 * n ** 3 / 5, 61 * n ** 3 / 240]
    t = math.sinh(math.atanh(math.sin(phi)) - math.sqrt(e2) * math.atanh(math.sqrt(e2) * math.sin(phi))); xi = math.atan2(t, math.cos(lam)); eta = math.atanh(math.sin(lam) / math.sqrt(1 + t * t))
    E, N = eta, xi
    for j in (1, 2, 3): E += al[j - 1] * math.cos(2 * j * xi) * math.sinh(2 * j * eta); N += al[j - 1] * math.sin(2 * j * xi) * math.cosh(2 * j * eta)
    return 500000 + k0 * A * E - E0, k0 * A * N - N0
SX, SY = E1 - E0, N1 - N0; inside = lambda p, m=0: -m < p[0] < SX + m and -m < p[1] < SY + m
routes = {r["route_id"]: r for r in rows("routes.txt")}
stops = {s["stop_id"]: utm10(float(s["stop_lat"]), float(s["stop_lon"])) for s in rows("stops.txt")}
shp = {}
for r in rows("shapes.txt"): shp.setdefault(r["shape_id"], []).append((int(r["shape_pt_sequence"]), float(r["shape_pt_lat"]), float(r["shape_pt_lon"])))
shapes = {}
for sid, pts in shp.items():
    xy = [utm10(la, lo) for _, la, lo in sorted(pts)]
    if not any(inside(p) for p in xy): continue
    d = [0.0]
    for a, b in zip(xy, xy[1:]): d.append(d[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    shapes[sid] = (xy, d)
days = {}
for c in rows("calendar.txt"): days[c["service_id"]] = sum(1 << i for i, k in enumerate(["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]) if c[k] == "1")
trips = {t["trip_id"]: t for t in rows("trips.txt") if t["shape_id"] in shapes and days.get(t["service_id"])}
times = {}
sec = lambda s: sum(int(v) * m for v, m in zip(s.split(":"), (3600, 60, 1)))
for st in rows("stop_times.txt"):
    if st["trip_id"] in trips and st["departure_time"]: times.setdefault(st["trip_id"], []).append((int(st["stop_sequence"]), st["stop_id"], sec(st["arrival_time"] or st["departure_time"]), sec(st["departure_time"])))
out_shapes, index, out_trips = [], {}, []
for tid, t in trips.items():
    xy, d = shapes[t["shape_id"]]; knots = []; at = 0
    for _, stop, arr, dep in sorted(times.get(tid, [])):
        sx, sy = stops[stop]; best, bi = 1e18, at                      # the nearest vertex at or after the last stop's
        for i in range(at, len(xy)):
            q = (xy[i][0] - sx) ** 2 + (xy[i][1] - sy) ** 2
            if q < best: best, bi = q, i
        at = bi; knots.append((d[bi], arr)); 
        if dep != arr: knots.append((d[bi], dep))
    if len(knots) < 2: continue
    ins = [i for i, p in enumerate(xy) if inside(p, 150)]; lo, hi = d[ins[0]], d[ins[-1]]
    a = max([i for i, k in enumerate(knots) if k[0] <= lo] or [0]); b = min([i for i, k in enumerate(knots) if k[0] >= hi] or [len(knots) - 1])
    if t["shape_id"] not in index:
        index[t["shape_id"]] = len(out_shapes); out_shapes.append([[round(xy[i][0], 1), round(xy[i][1], 1), round(d[i])] for i in range(max(0, ins[0] - 1), min(len(xy), ins[-1] + 2))])
    r = routes[t["route_id"]]
    out_trips.append({"r": r["route_short_name"], "n": r["route_long_name"], "k": "ferry" if r["route_type"] == "4" else "bus", "s": index[t["shape_id"]], "d": days[t["service_id"]], "t": [[round(k[0]), k[1]] for k in knots[a:b + 1]]})
feed = next(rows("calendar.txt"))
json.dump({"source": URL, "valid": [min(c["start_date"] for c in rows("calendar.txt")), max(c["end_date"] for c in rows("calendar.txt"))], "shapes": out_shapes, "trips": out_trips}, open(os.path.join(VIEW, "data", "transit.json"), "w"), separators=(",", ":"))
from collections import Counter
print(f"{len(out_trips)} trips on {len(out_shapes)} paths cross the window:", dict(Counter(f'{t["k"]} {t["r"]}' for t in out_trips)), "valid", min(c["start_date"] for c in rows("calendar.txt")), "to", max(c["end_date"] for c in rows("calendar.txt")))
