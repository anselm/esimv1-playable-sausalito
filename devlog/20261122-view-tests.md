# View tests: the town as solid ground

22 November 2026. Claude (Fable 5.2), esimv1 room on canada1, session
`session_018TGCFiQHbUYn12HkNti2xk`. Anselm asked for visualization tests because
"wireframe is not the right look"; he is "leaning towards more of a solid style - perhaps
with sun position controls. showing buildings is important."

This is a picture of the ground. Nothing in it is simulated, and it does not use esimv1.

## What was built

`view/index.html`, one page drawn with three.js: the terrain as a lit surface, every
building as a solid body, roads and piers painted on the ground, the bay, and a sun
placed by a date slider and a clock slider, casting shadows. Three looks to choose
between, and five fixed viewpoints.

| Look | What it is |
|---|---|
| Daylight | Natural colours: olive hills, pale flats, blue water, light walls and varied roofs |
| Model | One pale material, like an architect's model; shape and shadow only |
| Paper | Cream land with contour lines, white roads, dark buildings; closest to a printed map |

![Daylight, from the bay](img/20261122-daylight-from-the-bay.jpg)
![Daylight, a summer evening: the sun is behind the ridge](img/20261122-daylight-evening.jpg)
![Paper, the Marinship](img/20261122-paper-marinship.jpg)
![Model, a summer morning](img/20261122-model-summer-morning.jpg)
![Model, 21 December at 15:30: the ridge's shadow has crossed the town](img/20261122-model-winter-afternoon.jpg)
![Model, plan view](img/20261122-model-plan.jpg)

## To run it

```
cd view && python3 -m http.server 5199
```

then open `http://localhost:5199/`. Query parameters set the start: `look` (day, model,
paper), `cam` (bay, downtown, marinship, hill, top), `day` (1 to 365), `hour`, and `bare`
to hide the panels. `node view/tools/shot.mjs <url> <out.png>` takes a headless picture.
It draws in about two seconds on canada1's graphics card. It has not been tried on a
phone.

## Data

- **Ground.** US Geological Survey 3DEP one-metre elevation from lidar, the 2018 survey
  (tiles x54y419 and x54y420 of CA_NoCal_Wildfires_B5b), public domain. Cut to a window
  4.5 km square and averaged to 4 m: `view/data/ground.bin`, 2.5 MB. The 2024 San
  Francisco survey has the same tile name but holds no data north of the Golden Gate.
- **Buildings, roads, piers.** OpenStreetMap through Overpass, as of 22 November 2026:
  4,216 buildings in the window (435 tagged as houseboats), 1,693 road and path lines,
  325 piers. © OpenStreetMap contributors, Open Database Licence.
- `view/prepare.py` rebuilds both files from the downloads in `cache/`, which is not in
  git (460 MB). It needs GDAL's command-line tools and numpy.

## What is wrong with it

- **Building heights are placeholders.** OpenStreetMap carries a height or a storey
  count for 36 of the 4,216 buildings. The rest are given a height by kind (6.5 m for a
  plain building, 4.5 m for a houseboat, and so on), so the town looks like rows of equal
  boxes and its shadows are not to be trusted. The fix is the lidar point cloud: the
  highest return over each footprint, less the ground. That is 30 or so files of about
  100 MB each and a reader we do not have yet.
- The bay is the survey's flattened water surface, a flat sheet at -0.3 m. There is no
  bathymetry, no tide and no wave.
- No trees. On the hillside they are much of what a person sees.
- The sun's position uses low-precision formulas and standard time all year. It has not
  been checked against an almanac.
- The window cuts off the floating-home harbors to the north and most of Marin City.

## Open

- Which look, or which mix of them.
- Whether the window should grow north and west.
- This page is a hand-written three.js file. Whether the eventual view is built here or
  as a part of esimv1's viewer is the open question in esimv1's devlog of the same day.
