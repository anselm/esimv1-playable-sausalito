# The week of the flood on the page

24 November 2026, evening. Claude (Fable 5.2) in the esimv1 room on canada1, on Anselm's word:

> Our model fails to reflect the current crisis on the ground

He is right, and the reason was mostly not the flood computation.

## What was wrong

- **The page opens on the present moment.** Flooding this week lasts a few hours around each morning's high water. Opened in the afternoon, the page showed a low tide and a dry town.
- **The tide choices were below what happened.** The highest choice short of sea-level rise was "a king tide" at 2.22 m, the tide table's figure for 24 December. The San Francisco gauge (NOAA 9414290) measured more than that on three mornings running:

  | Day | Measured high, m NAVD88 | Tide table | Gap |
  |---|---|---|---|
  | Sat 21 Nov | 2.21 | 1.86 | 0.35 |
  | Sun 22 Nov | 2.35 | 1.97 | 0.38 |
  | Mon 23 Nov | 2.44 | 2.07 | 0.37 |
  | Tue 24 Nov | 2.53 | 2.13 | 0.39 |

  A chosen date and hour used the tide table alone, so the storm was left out of every moment except "now".
- **Nothing said how long.** The page could show water at one level. It could not say which hours of a day a road was under it, or who was cut off.
- **The reports had no place on the map.** The inhaler holds 57 facts about flooding, tides and closures, but most name only "Sausalito" and so have no mark.

## What changed

- `view/lib/tide.js`, `tideWeek`: the gauge's last four days and the tide table for those days and the next three, on one six-minute grid. The expected level ahead is the table plus the mean gap over the gauge's last 12.4 hours of readings. That is a rule of thumb, not a forecast. This evening it gives 2.51 m for Wednesday's high; the Weather Service's own figure, 8.5 ft above MLLW, is about 2.61 m.
- `view/lib/sky.js`, `alertsNow`: the Weather Service's alerts for the point. The page lists the flood ones and opens their text on a click.
- `view/lib/flood.js`, new:
  - `reachLevels` gives every cell the lowest level at which the bay reaches it over the ground. The picture of the water is the same as before; it is now a comparison per cell, so the level can be dragged.
  - `makeAccess` closes a road where water stands 15 cm deep on it (a figure recalled from flood driving guidance, unchecked), and counts a building as having no dry road out when its nearest road no longer connects by open roads to the largest part of the network or to a road leaving the window.
- The strip at the bottom left replaces the one-line readout: the week's curve (table thin, measured solid, expected dashed), red where the water is above the level at which 25 buildings lose their road out, the hours above that level for each day, the highest reading and the next high as links, and the alerts. Dragging the chart moves the whole picture to that moment.
- Buildings with no dry road out are drawn red. A click on a building says at what level its road closes and for how many hours on each day of the week.
- The propositions panel gains "this week's highest" as a tide, and a daily-life line for buildings cut off. Raising Gate 5 Road recomputes the reach and the access.
- `?when=high`, `?when=next` or `?when=<time>` opens the page at that moment of the week.

## What it says tonight

At Tuesday's 2.53 m: 12.3 km of road under 15 cm of water or more, and 788 buildings with no dry road out, 325 of them floating homes. A floating home on South Forty Dock loses its road at 2.20 m: 2.2 hours on Sunday, 2.8 on Monday, 3.4 on Tuesday, and about 3.7 expected on Wednesday.

Buildings with no dry road out, by level (prototype in Python on the same data):

| Level, m | Buildings | Of which floating homes | Streets newly cut |
|---|---|---|---|
| 2.0 | 42 | 2 | Cardinal Road |
| 2.2 | 273 | 136 | Yellow Ferry Harbor, West Kappas Marina, South Forty Pier |
| 2.4 | 458 | 213 | Gate 6 Road, Robin Road, Starling Road |
| 2.5 | 738 | 275 | Peninsula Road, West Shore Road, Gate 6 1/2 Road |

The page's count at 2.53 m is higher than the table's 2.5 m row because the page lets a floating home look 220 m for its road.

## Against this week's reports

This is the chore "check the computed flood against where water was reported".

- 22 November, 2.35 m. Reported: bay water reaching Bridgeway at Gate 5 and pooling at the Highway 101 exit, which police closed (Marin Independent Journal, as read by the inhaler). Computed: 284 m of Gate 5 Road and 210 m of motorway ramp wet. Agrees.
- 23 November, 2.44 m. Reported: the on-ramp from Bridgeway to northbound 101 flooded. Computed: 384 m of ramp wet. Agrees.
- 23 November. Reported: the Gate 5 Road parking lots stayed dry because a private drive and a drainage canal had been raised. The model's ground is the 2018 survey and does not have that work, so it floods them. Disagrees, for a known reason.
- 22 November. Reported: two inches of rain in two hours filled the storm drains. The model has no rain and no drains.

Nothing above was checked street by street, and nobody who was there has looked at the red buildings.

## Limits

- The gauge is San Francisco's. No correction is made for Richardson Bay, and the county's new sensor at Waldo Point Harbor is not read.
- Water travels over the surface only: no storm drains, culverts, pumps, rain or waves. Bay water that comes up through a drain is missed, and so is a pond behind an embankment.
- The ground is the 2018 survey at 4 m. A wall narrower than that, or work done since, is absent.
- "No dry road out" uses the nearest drivable road in OpenStreetMap. Roads beyond the window are assumed open. The 15 cm depth is one number for every vehicle.
- The expected level carries today's gap forward unchanged.
- On a phone the strip starts as the line and the chart; a tap on the line opens the rest. Not tried on a real phone.

## Next

- Read the Waldo Point sensor if the county publishes it, and compare it with San Francisco's gauge.
- Use the Weather Service's forecast height in place of the carried gap when an alert states one.
- Rain: water arriving down the drainage lines while the tide holds the outfalls shut.
- Give the unplaced flood reports a place, or list them in the strip.
- Draw closed roads as closed, not only the buildings behind them.

## Later the same evening: it still looked like nothing

Anselm, after the first pass:

> But they say they have extreme flooding - none of our displays indicate anything going on
> Why is there such a large delta between our business as usual map and what I hear from people there ?

Two faults of display, both fixed:

- The page still opened on the present moment, a low tide at dusk. It now opens on the latest high water when that high closed roads and the present level does not, and says so in the strip's first line with a link back to now. `?flood=0` turns that off.
- At high water the flooded streets could hardly be seen. Shallow water over land was drawn as the same dark sheet as the bay, 10 to 40 cm of it over grey road. Flooded ground now has its own lit colour (`floodMesh`), stronger where deeper.

What the display now shows honestly is how small the computed flood is: a fringe along the shore, Gate 5 and Gate 6 roads, the 101 ramps. The rest of the gap is in the model, not the display:

- No rain. This week's reports pair the tides with heavy rain, and a tide above the outfalls holds that rain in the streets.
- No drains. Bay water comes up through storm drains onto ground the surface route never reaches.
- No waves or local wind set-up, and the level is San Francisco's.
- The picture is of where water stands, not of what it does: a closed ramp, a home reached only by wading, a business that cannot open.

We also do not know where the person he heard from lives, or whether it is inside the window.
