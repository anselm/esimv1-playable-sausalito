// The water level at a NOAA tide gauge, for a page to draw. No place is named here: give it a
// station number. Levels are metres above NAVD88, the datum the US lidar ground is measured in,
// so a level can be drawn straight onto that ground.
//
// Source: NOAA Center for Operational Oceanographic Products and Services, the CO-OPS data API
// (api.tidesandcurrents.noaa.gov). Public domain. It answers browsers from any origin.
// A measured level marked preliminary has not been through NOAA's checks.

const API = 'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter'
const ask = async (station, extra) => {
  const u = `${API}?station=${station}&time_zone=gmt&units=metric&format=json&application=playable-place&${extra}`
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
