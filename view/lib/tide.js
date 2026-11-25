// The water level at a NOAA tide gauge, for a page to draw. No place is named here: give it a
// station number. Levels are metres above NAVD88, the datum the US lidar ground is measured in,
// so a level can be drawn straight onto that ground.
//
// Source: NOAA Center for Operational Oceanographic Products and Services, the CO-OPS data API
// (api.tidesandcurrents.noaa.gov). Public domain. It answers browsers from any origin.
// A measured level marked preliminary has not been through NOAA's checks.

const API = 'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter'
const ask = async (station, extra) => {
  const u = `${API}?station=${station}&time_zone=gmt&units=metric&format=json&application=the-sausalito-model&${extra}`
  const r = await fetch(u); if (!r.ok) throw new Error(`tide gauge ${station}: ${r.status}`)
  const j = await r.json(); if (j.error) throw new Error(`tide gauge ${station}: ${j.error.message}`)
  return j
}
const utc = (t) => new Date(t.replace(' ', 'T') + ':00Z')

// The latest measured level, and the wind at the gauge when it has an anemometer.
// -> { station, name, at: Date, level_m, preliminary, wind: { speed_ms, from_deg, gust_ms } | null }
export async function tideNow(station) {
  const [lv, wd] = await Promise.all([
    ask(station, 'product=water_level&datum=NAVD&date=latest'),
    ask(station, 'product=wind&date=latest').catch(() => null),
  ])
  const d = lv.data[lv.data.length - 1], w = wd?.data?.[wd.data.length - 1]
  return {
    station, name: lv.metadata?.name ?? String(station), at: utc(d.t), level_m: +d.v, preliminary: d.q === 'p',
    wind: w && w.s !== '' ? { speed_ms: +w.s, from_deg: +w.d, gust_ms: w.g === '' ? null : +w.g } : null,
  }
}

// The predicted (astronomical) level at an instant: NOAA's harmonic prediction, which leaves out
// weather. Hourly values are fetched a day at a time, kept, and read between by a straight line.
const days = new Map()
export async function tidePredicted(station, when) {
  const day = new Date(Date.UTC(when.getUTCFullYear(), when.getUTCMonth(), when.getUTCDate()))
  const key = `${station}:${day.toISOString().slice(0, 10)}`
  if (!days.has(key)) {
    const ymd = day.toISOString().slice(0, 10).replaceAll('-', '')
    days.set(key, ask(station, `product=predictions&datum=NAVD&interval=h&begin_date=${ymd}%2000:00&range=25`).then((j) => j.predictions.map((p) => +p.v)))
  }
  const v = await days.get(key), h = (when - day) / 3600000, i = Math.min(v.length - 2, Math.floor(h)), u = h - i
  return { station, at: when, level_m: v[i] * (1 - u) + v[i + 1] * u, predicted: true }
}

// A stretch of days around now on one six-minute grid: what the gauge measured, what the tide table said, and
// what to expect next. The expected level is the table plus the gap the gauge has been running above or below it
// over its last tide cycle (12.4 hours of readings): a storm surge carried forward unchanged, which is a
// rule of thumb and not a forecast. A weather service's own forecast, when there is one, is better.
// -> { station, t0: ms, step: ms, table[], measured[] (NaN where there is none), last: index of the newest
//      reading, surge_m, at(Date) -> { level_m, kind: 'measured' | 'expected' | 'table' } | null }
export async function tideWeek(station, { back_h = 96, ahead_h = 72, now = new Date() } = {}) {
  const stamp = (d) => d.toISOString().slice(0, 16).replace(/-/g, '').replace('T', '%20'), a = new Date(now.getTime() - back_h * 3600000), b = new Date(now.getTime() + ahead_h * 3600000)
  const [tb, ms] = await Promise.all([
    ask(station, `product=predictions&datum=NAVD&begin_date=${stamp(a)}&end_date=${stamp(b)}`),
    ask(station, `product=water_level&datum=NAVD&begin_date=${stamp(a)}&end_date=${stamp(now)}`).catch(() => ({ data: [] })),
  ])
  const step = 360000, t0 = utc(tb.predictions[0].t).getTime(), table = tb.predictions.map((p) => +p.v), measured = new Array(table.length).fill(NaN)
  let last = -1; for (const d of ms.data) { if (d.v === '') continue; const i = Math.round((utc(d.t).getTime() - t0) / step); if (i >= 0 && i < table.length) { measured[i] = +d.v; if (i > last) last = i } }
  let sum = 0, n = 0; for (let i = Math.max(0, last - 123); i <= last; i++) if (!Number.isNaN(measured[i])) { sum += measured[i] - table[i]; n++ }
  const surge_m = n ? sum / n : 0
  const level = (i) => i <= last && !Number.isNaN(measured[i]) ? [measured[i], 'measured'] : i > last && last >= 0 ? [table[i] + surge_m, 'expected'] : [table[i], 'table']
  return { station, t0, step, table, measured, last, surge_m, level,
    at(when) { const u = (when.getTime() - t0) / step, i = Math.floor(u); if (i < 0 || i >= table.length - 1) return null
      const [v0, k0] = level(i), [v1] = level(i + 1); return { level_m: v0 + (v1 - v0) * (u - i), kind: k0 } } }
}
