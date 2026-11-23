#!/usr/bin/env python3
"""Fetch buildings, roads, piers and waterways for the window from OpenStreetMap, into cache/osm_raw.json.

Asks the Overpass mirrors in turn, with a pause that grows after each refusal. The data is
(c) OpenStreetMap contributors, under the Open Database License.
"""
import json, os, sys, time, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__)); W = json.load(open(os.path.join(HERE, "..", "window.json")))
box = f'{W["south"]},{W["west"]},{W["north"]},{W["east"]}'
q = f'[out:json][timeout:120];(way["building"]({box});way["highway"]({box});way["man_made"="pier"]({box});way["waterway"]({box}););out tags geom;'
for i, m in enumerate(["https://overpass-api.de/api/interpreter", "https://overpass.private.coffee/api/interpreter", "https://overpass.kumi.systems/api/interpreter"] * 2):
    try:
        r = urllib.request.urlopen(urllib.request.Request(m, data=urllib.parse.urlencode({"data": q}).encode(), headers={"User-Agent": "playable-place view tools"}), timeout=180)
        d = json.loads(r.read())
        if d.get("elements"):
            json.dump(d, open(os.path.join(HERE, "..", "..", "cache", "osm_raw.json"), "w")); print(len(d["elements"]), "ways from", m); sys.exit(0)
    except Exception as e: print(m, "did not answer:", str(e)[:80])
    time.sleep(5 * (i + 1))
sys.exit("no Overpass mirror answered")
