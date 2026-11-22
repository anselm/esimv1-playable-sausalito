"""Grid lidar points to a surface: the highest return in each one-metre cell of the window.

  python lidar_surface.py <folder of .laz in EPSG:3857> <out.bin>

Writes float32, one cell per metre of the window (view/window.json), row 0 at the north edge, metres NAVD88, NaN where no point fell;
and <out>.count.bin, uint16 points per cell. Points classed as noise (7, 18) are left out.
Needs laspy with a LAZ backend and pyproj (kept in a private venv, not a project dependency).
"""
import sys, glob, numpy as np, laspy
from pyproj import Transformer
from concurrent.futures import ProcessPoolExecutor

import json, os
_W = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'window.json')))
E0, N0, E1, N1 = _W['e0'], _W['n0'], _W['e1'], _W['n1']          # the window, UTM zone 10 north (EPSG:26910)
NX, NY = E1 - E0, N1 - N0

def one(path):
    las = laspy.read(path)
    cls = np.asarray(las.classification)
    keep = (cls != 7) & (cls != 18)
    x, y = Transformer.from_crs(3857, 26910, always_xy=True).transform(np.asarray(las.x)[keep], np.asarray(las.y)[keep])
    z = np.asarray(las.z)[keep]; c = cls[keep]
    col = np.floor(x - E0).astype(np.int64); row = np.floor(N1 - y).astype(np.int64)
    ok = (col >= 0) & (col < NX) & (row >= 0) & (row < NY)
    idx = row[ok] * NX + col[ok]; z = z[ok].astype(np.float32); c = c[ok]
    if not len(idx): return None
    o = np.argsort(idx, kind='stable'); idx = idx[o]; z = z[o]; c = c[o]
    u, start, n = np.unique(idx, return_index=True, return_counts=True)
    top = np.maximum.reduceat(z, start)
    # class counts for the report: 1 unclassified, 2 ground, 9 water, 17 bridge deck
    return u, top, n, np.bincount(c, minlength=32)[:32]

if __name__ == '__main__':
    files = sorted(glob.glob(sys.argv[1] + '/*.laz'))
    top = np.full(NX * NY, -np.inf, np.float32); cnt = np.zeros(NX * NY, np.uint32); classes = np.zeros(32, np.int64)
    with ProcessPoolExecutor(24) as pool:
        for r in pool.map(one, files, chunksize=16):
            if r is None: continue
            u, t, n, cl = r
            top[u] = np.maximum(top[u], t); cnt[u] += n.astype(np.uint32); classes += cl
    top[~np.isfinite(top)] = np.nan
    top.tofile(sys.argv[2]); np.minimum(cnt, 65535).astype(np.uint16).tofile(sys.argv[2] + '.count.bin')
    have = cnt > 0
    print(f'{len(files)} files, {int(cnt.sum()):,} points in the window, {have.mean() * 100:.1f}% of cells have a point, {cnt.sum() / have.sum():.2f} points per covered cell')
    print('classes', {i: int(v) for i, v in enumerate(classes) if v})
