// The sky now over a point in the United States, for a page to light a scene by: the latest
// observation from the nearest National Weather Service station that has one.
//
// Source: api.weather.gov (NOAA National Weather Service). Public domain. It answers browsers from
// any origin. Stations report about once an hour; some fields are often empty.

const get = async (u) => { const r = await fetch(u, { headers: { Accept: 'application/geo+json' } }); if (!r.ok) throw new Error(`${u}: ${r.status}`); return r.json() }
// the share of the sky covered, from the densest reported layer (the aviation words, as eighths)
const COVER = { SKC: 0, CLR: 0, FEW: 0.2, SCT: 0.45, BKN: 0.75, OVC: 1, VV: 1 }

// -> { station, name, at: Date, text, cloud (0..1 or null), visibility_m, temp_c, wind: { speed_ms, from_deg } | null }
export async function skyNow(lat, lon, tryStations = 10) {
  const pt = await get(`https://api.weather.gov/points/${lat.toFixed(4)},${lon.toFixed(4)}`)
  const st = await get(pt.properties.observationStations)
  // the nearest stations are often small ones that report no sky; ask several at once and take
  // the nearest that says how much of the sky is covered, else the nearest that says anything
  const got = await Promise.all(st.features.slice(0, tryStations).map(async (f) => {
    try {
      const o = (await get(`${f.id}/observations/latest`)).properties
      const layers = (o.cloudLayers || []).map((l) => COVER[l.amount]).filter((v) => v != null)
      return {
        station: f.properties.stationIdentifier, name: f.properties.name, at: new Date(o.timestamp), text: o.textDescription || '',
        cloud: layers.length ? Math.max(...layers) : null, visibility_m: o.visibility?.value ?? null, temp_c: o.temperature?.value ?? null,
        wind: o.windSpeed?.value != null && o.windDirection?.value != null ? { speed_ms: o.windSpeed.value / 3.6, from_deg: o.windDirection.value } : null,
      }
    } catch (e) { return null }
  }))
  const pick = got.find((g) => g && g.cloud != null) || got.find((g) => g && g.text) || got.find((g) => g)
  if (!pick) throw new Error('no weather station near this point answered')
  return pick
}

// Warnings and advisories in force or announced for a point, from the same service.
// -> [{ event, headline, from: Date, to: Date, text, url }]
export async function alertsNow(lat, lon) {
  const j = await get(`https://api.weather.gov/alerts/active?point=${lat.toFixed(4)},${lon.toFixed(4)}`)
  return (j.features || []).map((f) => f.properties).map((p) => ({ event: p.event, headline: p.headline, from: new Date(p.onset || p.effective), to: new Date(p.ends || p.expires), text: p.description || '', url: `https://forecast.weather.gov/MapClick.php?lat=${lat.toFixed(4)}&lon=${lon.toFixed(4)}` }))
}
