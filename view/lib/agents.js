// Things that move by a timetable. An agent here is a vehicle on a published trip: it has a path, times at
// its stops, and a body. Where it is at a given second is worked out from the timetable alone (a steady
// speed between two stops), so this shows the service as scheduled, not vehicles as tracked.
//
//   const agents = makeAgents(THREE, transit, { X, Z, heightAt, SX, SY })
//   agents.group                         add to the scene
//   agents.tick(second_of_day, weekday, water_level_m) -> [{ k, r, n, x, y }]     weekday 0 is Monday
// `transit` is view/data/transit.json (view/tools/transit.py). `heightAt(x, y)` is the surface a wheeled
// vehicle stands on, in metres; boats ride the water level given to tick.
export function makeAgents(THREE, transit, { X, Z, heightAt, SX, SY }) {
  const group = new THREE.Group(), pools = { ferry: [], bus: [] }
  const white = new THREE.MeshStandardMaterial({ color: 0xf5f4ef, roughness: 0.55 }), glass = new THREE.MeshStandardMaterial({ color: 0x2d3d48, roughness: 0.3 }), busPaint = new THREE.MeshStandardMaterial({ color: 0xf0efe9, roughness: 0.6 }), band = new THREE.MeshStandardMaterial({ color: 0x1f6b3a, roughness: 0.6 })
  const hull = new THREE.Shape(); hull.moveTo(-25, -5.5); hull.lineTo(14, -5.5); hull.lineTo(25, 0); hull.lineTo(14, 5.5); hull.lineTo(-25, 5.5); hull.closePath()
  const hullGeo = new THREE.ExtrudeGeometry(hull, { depth: 3, bevelEnabled: false }); hullGeo.rotateX(-Math.PI / 2); hullGeo.translate(0, -0.8, 0)
  const make = { ferry() { const g = new THREE.Group()
      g.add(new THREE.Mesh(hullGeo, white)); const c1 = new THREE.Mesh(new THREE.BoxGeometry(34, 2.6, 9.4), glass); c1.position.set(-4, 3.5, 0); const c2 = new THREE.Mesh(new THREE.BoxGeometry(24, 2.4, 8), white); c2.position.set(-6, 6, 0)
      const wheel = new THREE.Mesh(new THREE.BoxGeometry(6, 2.2, 6), glass); wheel.position.set(3, 8.2, 0); g.add(c1, c2, wheel); return g },
    bus() { const g = new THREE.Group(); const body = new THREE.Mesh(new THREE.BoxGeometry(12.2, 2.9, 2.6), busPaint); body.position.y = 1.85; const stripe = new THREE.Mesh(new THREE.BoxGeometry(12.3, 0.5, 2.7), band); stripe.position.y = 1.0; const win = new THREE.Mesh(new THREE.BoxGeometry(11.6, 0.9, 2.66), glass); win.position.y = 2.4; g.add(body, stripe, win); return g } }
  for (const g of Object.values(make)) void g
  function where(trip, sec) {
    const t = trip.t, last = t.length - 1; if (sec < t[0][1] || sec > t[last][1]) return null
    let i = 0; while (i < last - 1 && t[i + 1][1] < sec) i++
    const span = t[i + 1][1] - t[i][1], d = span > 0 ? t[i][0] + (t[i + 1][0] - t[i][0]) * (sec - t[i][1]) / span : t[i][0], sh = transit.shapes[trip.s], n = sh.length - 1
    if (d < sh[0][2] || d > sh[n][2]) return null
    let lo = 0, hi = n; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (sh[m][2] <= d) lo = m; else hi = m }
    const a = sh[lo], b = sh[hi], u = b[2] > a[2] ? (d - a[2]) / (b[2] - a[2]) : 0, x = a[0] + (b[0] - a[0]) * u, y = a[1] + (b[1] - a[1]) * u
    if (x < 0 || y < 0 || x > SX || y > SY) return null
    // the heading from a little way along the path either side, so a vehicle does not twitch at each vertex
    let p = lo, q = hi; while (p > 0 && d - sh[p][2] < 15) p--; while (q < n && sh[q][2] - d < 15) q++
    return { x, y, ang: Math.atan2(sh[q][1] - sh[p][1], sh[q][0] - sh[p][0]), waiting: span > 0 && t[i + 1][0] === t[i][0] }
  }
  function tick(sec, weekday, level) {
    const used = { ferry: 0, bus: 0 }, out = []
    for (const trip of transit.trips) for (const off of [0, 86400]) {                         // a trip that began yesterday evening may still be running after midnight
      if (!(trip.d & (1 << ((weekday - (off ? 1 : 0) + 7) % 7)))) continue
      const w = where(trip, sec + off); if (!w) continue
      const pool = pools[trip.k]; if (used[trip.k] === pool.length) { const m = make[trip.k](); pool.push(m); group.add(m) }
      const m = pool[used[trip.k]++]; m.visible = true; m.position.set(X(w.x), trip.k === 'ferry' ? level : heightAt(w.x, w.y), Z(w.y)); m.rotation.y = w.ang
      out.push({ k: trip.k, r: trip.r, n: trip.n, x: w.x, y: w.y, waiting: w.waiting })
    }
    for (const k in pools) for (let i = used[k]; i < pools[k].length; i++) pools[k][i].visible = false
    return out
  }
  return { group, tick }
}
