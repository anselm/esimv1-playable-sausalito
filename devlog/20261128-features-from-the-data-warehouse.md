# The town's features come from the data warehouse

28 November 2026. Claude (Fable 5.2), working from the esimv1 room on canada1 (session 018TGCFiQHbUYn12HkNti2xk),
on Anselm's word there: "Now that we have the data warehouse every single project should switch to it and we
should commit and push".

## What changed

`view/prepare.py` no longer reads an OpenStreetMap answer or Microsoft's footprint file from `cache/`. It reads
four products from the public data warehouse at <https://data.earthlight.cloud> (made with
github.com/anselm/esimv1-data), each named by its address in the script:

- `buildings/massing/sausalito/2026-11-27`: OpenStreetMap's outlines, each with one height and where it came from
- `roads/osm/sausalito/2026-11-28`
- `shore/osm/sausalito/2026-11-28` (the piers)
- `water/osm/sausalito/2026-11-28` (creeks and culverts)

The matching of Microsoft's heights to OpenStreetMap outlines, which this script used to do, is now done once in
the warehouse by the same rule (the footprint holding the building's middle, else the nearest within 12 m). The
lidar steps are unchanged and still replace every height they can measure. `view/tools/osm_fetch.py` is removed.
About sixty lines of the script went; `cache/osm_raw.json` (7 MB) and `cache/ms_qk023010203.csv.gz` (24 MB) are no
longer needed.

## What it did to the page's data

| | before | after |
|---|---|---|
| buildings | 6,449 | 6,479 |
| measured by lidar | 6,256 | 6,284 |
| left on Microsoft's estimate | 127 | 139 |
| left on a guess | 66 | 56 |
| roads | 2,580 | 2,581 |
| piers | 347 | 381 |
| mapped waterways | 94 | 95 |

The differences are the map's date (the old answer was fetched on 23 November) and one rule: the warehouse also
takes buildings drawn as multipolygon relations, which the old query did not. A building the lidar cannot
measure and Microsoft has no estimate for now gets the warehouse's guess (from neighbouring buildings of similar
size, or from its kind and area) where it used to get a fixed height by kind.

The page was opened locally after the change and looked at in light at desktop width and dark at phone width:
terrain, buildings, trees, the flood strip and the markers draw as before.

## Not done

- The deployed copy at sausalito.exe.xyz still serves the data prepared on 24 November. It changes at the next
  deploy, which is Anselm's call.
- The ground (USGS one-metre elevation), the two lidar flights, the transit feed and the boats are still fetched
  and cut by this repository's own tools. The warehouse has no rasters or lidar products yet.
- The one-way flag on roads exists in warehouse roads products only from 28 November, which is why the roads
  product is a day newer than the buildings.
