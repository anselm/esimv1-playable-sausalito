// Public map layers about the town, asked of their publishers when a layer is switched on. Nothing
// here is copied into this repository: several of these carry no stated licence, so the page reads
// them where they are published. A layer is a hosted feature service (ArcGIS REST), a field to
// colour and label by, and a sentence saying what it is and whose it is.
//
//   fetchLayer(def, [west, south, east, north]) -> [{ type: 'area' | 'line' | 'point', rings | line | point, props }]   in lon, lat
const MARIN = 'https://services6.arcgis.com/T8eS7sop5hLmgRRH/ArcGIS/rest/services/'
const hue = (s) => { let h = 0; for (const c of String(s)) h = (h * 31 + c.charCodeAt(0)) % 360; return h }
const ramp = (order, colours) => (v) => colours[Math.max(0, order.indexOf(v))] || '#999999'

export const LAYERS = [
  { id: 'zoning', name: 'Zoning', url: MARIN + 'Zoning_of_Sausalito/FeatureServer/123', field: 'Zoning', by: "Sausalito's zoning map as hosted by Marin County, 2023",
    colour: (v) => /^R/.test(v) ? `hsl(${48 - Math.min(30, parseFloat(String(v).split('-')[1]) || 0) * 4} 85% 60%)` : /^C/.test(v) ? '#e2574c' : /^(I|W)$/.test(v) ? '#8e6bbf' : /^(OS|PP|PR|OA)$/.test(v) ? '#58a55c' : /^PI$/.test(v) ? '#4f86c6' : '#999999',
    say: (v) => ({ R: 'residential', C: 'commercial', I: 'industrial', W: 'waterfront', OS: 'open space', PP: 'public park', PI: 'public and institutional', OA: 'open area', PR: 'public recreation', H: 'houseboats' }[String(v).split('-')[0].replace(/[RW-]?$/, (m) => m)] || ({ CR: 'commercial residential', CC: 'central commercial', CW: 'commercial waterfront', CN: 'neighbourhood commercial', CS: 'commercial service' }[String(v).split('-')[0]]) || '') },
  { id: 'plan', name: 'General plan', url: MARIN + 'General_Plan_of_Sausalito/FeatureServer/0', field: 'GeneralPlan', by: "Sausalito's general plan land uses as hosted by Marin County",
    colour: (v) => /Residential/.test(v) && !/Mixed/.test(v) ? `hsl(${/High/.test(v) ? 28 : /Low/.test(v) ? 52 : 40} 85% 60%)` : /Commercial|Mixed/.test(v) ? '#e2574c' : /Open|Park/.test(v) ? '#58a55c' : /Waterfront|Industrial/.test(v) ? '#8e6bbf' : /Public/.test(v) ? '#4f86c6' : '#999999' },
  { id: 'fema', name: 'Flood insurance zones', url: MARIN + 'FEMA_NFHL_06041C/FeatureServer/19', field: 'FLD_ZONE', where: "SFHA_TF='T'", by: 'FEMA National Flood Hazard Layer, Marin County panel: areas with a one percent chance of flooding in a year',
    colour: (v) => /^V/.test(v) ? '#1f5fbf' : '#4f9be0', say: (v) => /^V/.test(v) ? 'coastal, with waves' : /^A/.test(v) ? 'one percent a year' : '' },
  { id: 'slr20', name: 'Sea level rise, 20 inches', url: MARIN + 'Sea_Level_Rise_%E2%80%93_20_inches/FeatureServer/0', field: 'SLR', by: "Marin County's sea-level-rise area for 20 inches, its own layer", colour: () => '#2f8fd0' },
  { id: 'slr60', name: 'Sea level rise, 5 feet', url: MARIN + 'Sea_Level_Rise_%E2%80%93_5_feet/FeatureServer/0', field: 'SLR', by: "Marin County's sea-level-rise area for 5 feet, its own layer", colour: () => '#1b5fa8' },
  { id: 'evac', name: 'Evacuation zones', url: MARIN + 'Zonehaven_Marin_zones_240801/FeatureServer/0', field: 'zone_id', by: 'Evacuation zones (Zonehaven) as hosted by Marin County, August 2024, with its estimate of residents',
    colour: (v) => `hsl(${hue(v)} 55% 60%)`, say: (v, p) => p.est_popula ? `about ${Math.round(p.est_popula).toLocaleString('en')} residents` : '' },
  { id: 'liq', name: 'Liquefaction', url: MARIN + 'Liquefaction/FeatureServer/0', field: 'Liquefaction', by: 'Liquefaction susceptibility as hosted by Marin County',
    colour: ramp(['VL', 'L', 'M', 'H', 'VH', 'W'], ['#f3e9c0', '#f0d37a', '#eda84a', '#e0683a', '#b8312f', '#00000000']), say: (v) => ({ VL: 'very low', L: 'low', M: 'moderate', H: 'high', VH: 'very high', W: 'water' }[v] || '') },
  { id: 'slide', name: 'Landslides', url: MARIN + 'Landslide/FeatureServer/0', field: 'LSCat', by: 'Mapped landslides as hosted by Marin County; the meaning of its categories was not found', colour: () => '#a0522d' },
  { id: 'fire', name: 'Fire hazard', url: MARIN + 'Fire_Hazard_Severity_Zones/FeatureServer/0', field: 'Haz_Class', by: 'Fire hazard severity zones as hosted by Marin County',
    colour: ramp(['Moderate', 'High', 'Very High'], ['#f2d04b', '#ee8b3a', '#d0362c']) },
  { id: 'tsunami', name: 'Tsunami hazard area', url: MARIN + 'Marin_County_Tsunami/FeatureServer/1', field: 'Evacuate', by: "California Geological Survey's tsunami hazard area as hosted by Marin County", colour: () => '#2aa7a0' },
  { id: 'parks', name: 'Parks and open space', url: MARIN + 'Parks/FeatureServer/0', field: 'ParkName', by: 'Parks as hosted by Marin County', colour: () => '#58a55c', say: (v, p) => String(p.ParkType || '').replace(/_/g, '').trim() },
  { id: 'parcels', name: 'Parcels', url: MARIN + 'Parcels/FeatureServer/0', field: 'Parcel', by: "Marin County's parcels; lines only. The county gives them as they are, with no stated licence", colour: () => null, thin: true },
  { id: 'bus', name: 'Bus routes', url: MARIN + 'Bus_Route_Golden_Gate_Transit/FeatureServer/0', field: 'Name', by: 'Golden Gate Transit bus routes as hosted by Marin County', colour: () => '#c2410c' },
  { id: 'schools', name: 'Schools', url: MARIN + 'Schools/FeatureServer/0', field: 'Name', by: 'Schools as hosted by Marin County', colour: () => '#7c3aed', say: (v, p) => [p.Grade, p.District].filter(Boolean).join(', ') },
]

export async function fetchLayer(def, [w, s, e, n]) {
  const out = []
  for (let offset = 0, more = true; more && offset < 20000;) {
    const u = `${def.url}/query?where=${encodeURIComponent(def.where || '1=1')}&geometry=${w},${s},${e},${n}&geometryType=esriGeometryEnvelope&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=*&outSR=4326&geometryPrecision=6&resultOffset=${offset}&resultRecordCount=2000&f=geojson`
    const r = await fetch(u); if (!r.ok) throw new Error(`${def.name}: ${r.status}`)
    const g = await r.json(); if (g.error) throw new Error(`${def.name}: ${g.error.message}`)
    for (const f of g.features || []) { const t = f.geometry?.type, c = f.geometry?.coordinates, props = f.properties || {}
      if (t === 'Polygon') out.push({ type: 'area', rings: c, props })
      else if (t === 'MultiPolygon') for (const poly of c) out.push({ type: 'area', rings: poly, props })
      else if (t === 'LineString') out.push({ type: 'line', line: c, props })
      else if (t === 'MultiLineString') for (const l of c) out.push({ type: 'line', line: l, props })
      else if (t === 'Point') out.push({ type: 'point', point: c, props }) }
    more = !!(g.exceededTransferLimit || g.properties?.exceededTransferLimit); offset += (g.features || []).length; if (!(g.features || []).length) more = false
  }
  return out
}
