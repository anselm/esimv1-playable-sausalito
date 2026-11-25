// Where the bay goes on a grid of ground heights, and which buildings lose their dry road out.
// No place is named here. Heights are metres on one datum; the grid is row-major with row 0 at the north.
//
// Two things are computed and both can be wrong in ways a report can catch:
//  - reachLevels: for every cell, the lowest water level at which the bay reaches it over the surface. Water
//    arrives from cell to cell, so low ground behind higher ground stays dry. Pipes, culverts, pumps, walls
//    thinner than a cell, rain and waves are not in it.
//  - makeAccess: a road closes when the water reaches it and stands deeper than `wade` on it. A building has a
//    way out while its nearest road still connects, by roads that are open, either to the largest part of the
//    network or to a road that leaves the grid. What the roads beyond the grid do is not known.

// -> Float32Array: the level at which each cell is first reached (the sea's own cells hold `sea`; cells never
//    reached below `top` hold Infinity). A cell is under water at level L when its value is below L.
export function reachLevels(ground, nx, ny, sea, top = 6) {
  const n = nx * ny, thr = new Float32Array(n).fill(Infinity), nb = Math.ceil((top - sea) * 10) + 2
  const buckets = Array.from({ length: nb }, () => []), slot = (v) => Math.min(nb - 1, Math.max(0, Math.ceil((v - sea) * 10 - 1e-4)))
  for (let k = 0; k < n; k++) if (ground[k] <= sea) { thr[k] = sea; buckets[0].push(k) }
  const tryCell = (m, L) => { const v = Math.max(L, ground[m]); if (v < thr[m] && v <= top) { thr[m] = v; buckets[slot(v)].push(m) } }
  for (let b = 0; b < nb; b++) { const q = buckets[b]
    for (let j = 0; j < q.length; j++) { const k = q[j], L = thr[k]; if (slot(L) !== b) continue
      const i = k % nx; if (i > 0) tryCell(k - 1, L); if (i < nx - 1) tryCell(k + 1, L); if (k >= nx) tryCell(k - nx, L); if (k < n - nx) tryCell(k + nx, L) }
    buckets[b] = null }
  return thr
}

// roads: [{ p: [[x, y], ...], fixed: true for a bridge or tunnel }], x east and y north in metres from the grid's
// south-west corner, drivable roads only. places: [{ x, y, reach }] (reach: how far its road may be, metres).
// -> { update(ground, thr), cutAt: Float32Array per place (Infinity: never below `hi`; NaN: no road when dry),
//      closed(level) -> metres of road closed, cut(level) -> number of places cut off, first(n) -> the lowest
//      level at which n places are cut off }
export function makeAccess({ roads, places, nx, ny, res, sea, wade = 0.15, lo = 1, hi = 4, step = 0.05 }) {
  const SX = nx * res, SY = ny * res, cell = (x, y) => Math.min(ny - 1, Math.max(0, Math.floor((SY - y) / res))) * nx + Math.min(nx - 1, Math.max(0, Math.floor(x / res)))
  const ids = new Map(), px = [], py = [], id = (p) => { const key = Math.round(p[0] * 10) * 1e6 + Math.round(p[1] * 10); let i = ids.get(key); if (i === undefined) { i = px.length; ids.set(key, i); px.push(p[0]); py.push(p[1]) } return i }
  const sa = [], sb = [], sl = [], sk = [], sf = []
  for (const r of roads) for (let i = 0; i + 1 < r.p.length; i++) { const a = r.p[i], b = r.p[i + 1]; sa.push(id(a)); sb.push(id(b)); sl.push(Math.hypot(b[0] - a[0], b[1] - a[1])); sk.push(cell((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)); sf.push(r.fixed ? 1 : 0) }
  const N = px.length, S = sa.length, edge = new Uint8Array(N); for (let i = 0; i < N; i++) if (px[i] < 40 || py[i] < 40 || px[i] > SX - 40 || py[i] > SY - 40) edge[i] = 1
  // each place's nearest road point, by a 50 m hash
  const G = 50, hash = new Map(); for (let i = 0; i < N; i++) { const key = Math.floor(px[i] / G) * 4096 + Math.floor(py[i] / G); if (!hash.has(key)) hash.set(key, []); hash.get(key).push(i) }
  const at = new Int32Array(places.length).fill(-1)
  places.forEach((pl, j) => { const span = Math.ceil(pl.reach / G), gx = Math.floor(pl.x / G), gy = Math.floor(pl.y / G); let best = pl.reach * pl.reach
    for (let a = gx - span; a <= gx + span; a++) for (let b = gy - span; b <= gy + span; b++) for (const i of hash.get(a * 4096 + b) || []) { const d = (px[i] - pl.x) ** 2 + (py[i] - pl.y) ** 2; if (d < best) { best = d; at[j] = i } } })
  const close = new Float32Array(S), par = new Int32Array(N), len = new Float64Array(N), out = new Uint8Array(N)
  const find = (x) => { while (par[x] !== x) { par[x] = par[par[x]]; x = par[x] } return x }
  // which road points still have a way out when every road that closes at or below `level` is closed
  const ways = (level) => { for (let i = 0; i < N; i++) par[i] = i; len.fill(0); out.fill(0)
    for (let s = 0; s < S; s++) if (close[s] > level) { const a = find(sa[s]), b = find(sb[s]); if (a !== b) par[a] = b }
    for (let s = 0; s < S; s++) if (close[s] > level) len[find(sa[s])] += sl[s]
    let main = 0; for (let i = 0; i < N; i++) if (len[i] > len[main]) main = i
    out[main] = 1; for (let i = 0; i < N; i++) if (edge[i]) out[find(i)] = 1 }
  const levels = []; for (let L = lo; L <= hi + 1e-9; L += step) levels.push(Math.round(L * 100) / 100)
  const me = { cutAt: new Float32Array(places.length), levels, closedAt: close, wade,
    update(ground, thr) {
      for (let s = 0; s < S; s++) { const k = sk[s]; close[s] = sf[s] || ground[k] <= sea ? Infinity : Math.max(thr[k], ground[k] + wade) }
      ways(-Infinity); for (let j = 0; j < at.length; j++) me.cutAt[j] = at[j] >= 0 && out[find(at[j])] ? Infinity : NaN
      for (const L of levels) { ways(L); for (let j = 0; j < at.length; j++) if (me.cutAt[j] === Infinity && !out[find(at[j])]) me.cutAt[j] = L }
      return me },
    closed(level) { let m = 0; for (let s = 0; s < S; s++) if (close[s] <= level) m += sl[s]; return m },
    cut(level) { let c = 0; for (let j = 0; j < at.length; j++) if (me.cutAt[j] <= level) c++; return c },
    first(n) { for (const L of levels) if (me.cut(L) >= n) return L; return Infinity },
  }
  return me
}
