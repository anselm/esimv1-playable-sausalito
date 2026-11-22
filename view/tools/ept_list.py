"""List the nodes of an Entwine Point Tile (EPT) octree that touch a box, down to a depth.

  python3 ept_list.py <ept root url> <xmin> <ymin> <xmax> <ymax> <max depth>  >  urls.txt

The box is in the tree's own coordinates (ept.json, srs). A node at depth d holds the points
chosen on a grid of span cells across the node, so stopping at a depth is a thinning: at depth
10 of a 73 km cube with span 128 that is about one point per 0.56 m.
"""
import json, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

root, (x0, y0, x1, y1), maxd = sys.argv[1].rstrip('/'), map(float, sys.argv[2:6]), int(sys.argv[6])
get = lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'ept-list'}), timeout=60))
b = get(root + '/ept.json')['bounds']; size = b[3] - b[0]

def touches(key):
    d, x, y, z = map(int, key.split('-')); s = size / (1 << d)
    return d <= maxd and b[0] + x * s < x1 and b[0] + (x + 1) * s > x0 and b[1] + y * s < y1 and b[1] + (y + 1) * s > y0

out, todo = [], ['0-0-0-0']
with ThreadPoolExecutor(16) as pool:
    while todo:
        nxt = []
        for h in pool.map(lambda k: get(f'{root}/ept-hierarchy/{k}.json'), todo):
            for key, n in h.items():
                if not touches(key): continue
                if n == -1: nxt.append(key)
                elif n > 0: out.append(key)
        todo = nxt
for k in sorted(set(out)): print(f'{root}/ept-data/{k}.laz')
