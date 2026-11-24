# Volumes, news as a layer, milder propositions, and the boats

24 November 2026. Claude (Fable 5.2) in the esimv1 room on canada1, session
https://claude.ai/code/session_018TGCFiQHbUYn12HkNti2xk.

## What Anselm asked

- "Turn on the 'where the rain runs' by default."
- "It would be nice to show zoning as vertical curtains or polyhedra with volume that extends above the
  ground rather than just as lines on the ground - everything has a sameness when it is all represented
  the same way as lines."
- "The news markers are pretty ugly - and they cannot be clicked on ... Also news is just a layer, not a
  separate thing by itself."
- "rather than 'a game' I would say 'Propositions'. The dramatic propositions are too extreme (which I did
  ask for initially but I feel they are too much)." Limit floating homes, not remove them; urban greening
  that "use[s] up city resources to maintain"; policies to reduce tourist impacts that "would reduce
  revenue - would the quality of life improvements be worth it?"
- "we only show a few rough blocks visually for the floating homes. Is there any more detail on this?"
- "Towns do face many issues - not all are ecological", with two links (Quorum's list of local policy
  issues; Politico's 2023 survey of fifty mayors, which would not load from here).

## What changed on the page

**Layers have three forms now.** A wash on the ground (flood zones, liquefaction, fire hazard: things that
are about the ground), a volume (zoning) and a curtain (evacuation zones). The zoning volume is 32 feet
tall, with a translucent lid that is the ground's own shape lifted. 32 feet is the limit that summaries of
Sausalito's code give for most districts; it was read in third-party summaries and one table, not in the
official tables district by district. A building standing through the lid is taller than that. Open space
and park zones stay flat. Layers can declare `form`, `height_m` and `flat` in `view/lib/layers.js`.

**News is a row in the layers panel**, on by default. Each place the inhaler's facts name is a small round
mark on a thin stem; the number is how many facts name it; a click opens a card with what was said and the
sources. The list of issues is reached from that row ("read the issues"). 13 places today.

**Propositions**, not a game. Nine, each a yes or no: raise Gate 5 Road; retire one floating-home berth in
ten; plant street trees on the flat streets (drawn: one every 14 m on streets below 14 m; costs the
budget); let the Marinship rise from 32 to 47 feet (what Measure X asked, by the city's summary); cap tour
buses and rental bikes; build the 724 homes of the housing plan; replace the oldest sewer mains; fund
shelter and services; a $300 parcel tax. A fifth dial, daily life, carries the quality-of-life side.
The last four have no place on the map and no chip. Apart from the flood and the counts marked ●, every
effect is a rule of thumb or a judgement written by hand, and says so.

**Floating homes.** OpenStreetMap gives 444 outlines with no detail (one has a house number). Marin
County's address points give every dock's addresses: Liberty 72, Issaquah 70, South 40 49, East Pier 42,
West Pier 40, Main 35, Van Damme 24, A Dock 23, Yellow Ferry 22 and others. A new layer labels the docks
with those counts, and a click on a floating home gives its nearest county address. Walls are painted in
eight colours and an unmeasured home gets a low height that varies; both are decoration. Not found: any
public table of the homes themselves (size, age, berth). The harbors' own berth maps, the assessor's roll
(floating homes are taxed as property) and oblique aerial photographs are where more would come from.

**Boats.** `view/tools/boats.py` reads the lidar surface over the water and takes each connected patch of
returns 0.8 m or more above it, away from buildings and piers, as one boat: 776 of them, median length
12 m, 346 with a return over 6 m (drawn with a mast; the rest get a cabin). Boats that touch count as one,
so marinas are undercounted and their hulls run long. The anchored boats out in Richardson Bay in 2018
show as they were then; many have since been removed, and the page does not know that.

## Other issues towns face

Quorum's list for 2026: AI governance, expiring federal infrastructure money, zoning reform and missing
middle housing, digital accessibility, state limits on local taxes, climate resilience in land use, public
safety and trust, homelessness, schools and workforce, immigration. Of these the page now touches housing,
the budget, infrastructure and homelessness as propositions with hand-written effects. Nothing is computed
for them. What would make each computable: the housing element's site list (homes on the map), the city
budget by line (a real budget dial), the sewer district's pipe ages, the school district's enrolment.

## Not done

- No proposition beyond the road changes the flood.
- The lid is one height for every district; per-district limits are not read.
- Curtains and lids are not sorted against the water's transparency from every angle.
- Seen in screenshots, light and dark, wide and phone width; not on a real phone.

## Later the same day: the hand, and the news itself

Anselm: "it is a bit hard to move the focal point in the 3d view, i can zoom in but i cannot pan ... what
if we zoom to where the mouse is? or what are conventions here?" The controls now follow the convention of
web maps: drag moves the ground, the wheel or a pinch zooms toward the pointer, right-drag or two fingers
turns the view, arrow keys move, a double click goes to the spot. Zoom toward a pointer was checked with
synthetic wheel events; dragging and touch were not checked by hand.

Anselm: "for news - i am less interested in the named places and more interested in the actual news itself
about that place". Each mark now carries the newest report's own words beside it where there is room (the
newest reports get the room first), the full sentence on hover, and all reports on a click.
