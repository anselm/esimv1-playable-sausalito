#!/usr/bin/env bash
# Fetch NOAA's 2025 San Francisco Bay and Delta lidar for the window and grid it: cache/dsm2025.bin.
# Dataset 14673 (public domain), https://coast.noaa.gov/dataviewer/#/lidar/search/where:ID=14673/details/14673
# 67 tiles, 2.5 GB, about a minute to download and a quarter of a minute to grid. Needs GDAL (ogr2ogr), curl,
# and a Python with laspy, a LAZ backend and pyproj (PY, default the private venv). Then run view/prepare.py
# and view/tools/boats.py.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); C="$HERE/../../cache/lidar2025"; PY=${PY:-$HOME/.cache/sausalito-venv/bin/python}; mkdir -p "$C/laz"; cd "$C"
[ -s index.gpkg ] || curl -s -o index.gpkg https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/geoid18/14673/tileindex_ca2025_sanfran_bay_m14673.gpkg
read -r W S E N < <(python3 -c "import json;w=json.load(open('$HERE/../window.json'));print(w['west'],w['south'],w['east'],w['north'])")
rm -f tiles.geojson; ogr2ogr -f GeoJSON -t_srs EPSG:26910 -spat "$W" "$S" "$E" "$N" -spat_srs EPSG:4326 tiles.geojson index.gpkg
python3 - "$HERE/../window.json" <<'P'
import json, sys
d = json.load(open('tiles.geojson')); W = json.load(open(sys.argv[1]))
def bb(f):
    r = f['geometry']['coordinates'][0]; r = r[0] if isinstance(r[0][0], list) else r; xs = [p[0] for p in r]; ys = [p[1] for p in r]; return min(xs), min(ys), max(xs), max(ys)
keep = [f for f in d['features'] if bb(f)[2] > W['e0'] and bb(f)[0] < W['e1'] and bb(f)[3] > W['n0'] and bb(f)[1] < W['n1']]
open('urls.txt', 'w').write('\n'.join(f['properties']['url'] for f in keep) + '\n'); json.dump([[f['properties']['filename'], *bb(f)] for f in keep], open('boxes.json', 'w')); print(len(keep), 'tiles')
P
xargs -P 12 -n 1 sh -c 'f=laz/$(basename "$0"); [ -s "$f" ] || curl -s -o "$f" "$0"' < urls.txt
"$PY" "$HERE/lidar_surface.py" laz ../dsm2025.bin 6339 8
