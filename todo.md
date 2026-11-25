# Chores

Open work for this repository, one line each. Engine work that has to happen in esimv1
is marked (esimv1) and is also noted there.

## Done 24 November

- Rain lines on by default; zoning as a volume and evacuation zones as curtains; news as a layer with marks that open; nine milder propositions and a daily-life dial; floating homes painted, docks named from county addresses; 776 boats from the lidar (devlog 20261124).

## Next for boats and things that move (24 November)

- [x] Boats, building heights and trees from the September 2025 lidar where it covers (NOAA dataset 14673).
- [x] The 2018 anchored-out boats are gone from the picture.
- [ ] Live ferry and bus positions from the operator's GTFS-realtime feed, through a relay on the server.
- [ ] Vessels under way from AIS (archive to June 2026, or aisstream.io through a relay).
- [ ] Buses in the Waldo tunnel are drawn on the hill; holiday timetables are left out; the timetable file expires 12 December 2026.

## The demo, one day (Anselm, 2026-11-23)

His direction: propositions people say yes or no to, placed on the map where the issue is; "i just want to let people
actually play"; "some sense of impact - that you can do something - and different outcomes occur for real"; "accuracy is
less critical ... more like a game"; some kind of scoring across several bottom lines; no submitting of new proposals, no
tray of changes, no split screen. `devlog/20261123-propositions.md`.

1. [x] Propositions on the map: a chip where each issue is, a card with the proposition in words and yes or no.
2. [x] Water that goes where the ground lets it: flooding computed from the bay, on the lidar ground, at a chosen tide.
3. [x] Tides to try: today, this winter's king tide, the same with sea-level rise.
4. [x] First propositions with something to see: raise Gate 5 Road; remove the floating homes; cut down the trees; four storeys in the Marinship; ban tourists.
5. [x] Four dials (homes, money, nature, safety) that move, each with the reason in a sentence, marked as computed or as a rule of thumb.
5b. [x] The computed flood checked against the reports of 22 and 23 November; the week of the flood on the page, with hours of closed road per day and buildings with no dry road out (`devlog/20261124-the-week-of-the-flood.md`).
5b2. [ ] From that entry: read the Waldo Point sensor; use the Weather Service's forecast height; rain behind a high tide; place the unplaced flood reports; draw closed roads as closed; draw a raised road as raised.
5c. [x] Hydrology: mapped creeks and drainage lines computed from the lidar ground (`devlog/20261123-hydrology.md`). Next: rain in the flood, running down these lines.
6. [ ] More propositions: a tide gate at the Coloma Street canal, a wall along the Marinship, the 724 homes on the listed sites, close Bridgeway to cars, pave the hills.
7. [ ] Things that move: a ferry, cars, people, so a change like "ban tourists" can be seen.
8. [ ] The news beside the propositions: each chip shows what the papers said about its issue.
8b. [ ] Later, not now (Anselm, 23 November: "it is fine if we are not using svelte yet"; the page is for showing funders pretty visuals and ideas, and "will eventually be reworked into something more of an appliance"): the house stack (Svelte 5, Tailwind, Vite); personas and user stories in the devlog.
9. [ ] Watch it on a phone and tune: the tour, the chips, the weight of the trees.
10. [ ] Words: a proposition typed in plain language matched to one of the list.

## Next, in order (Anselm's four, 2026-11-22)
1. [x] Research, second pass, from primary pages: `devlog/20261122-sausalito-from-primary-pages.md`. Still open: the certified election result (25 November), who is mayor for 2027, the terms of the county's data, the older flood and subsidence studies.
2. [x] View tests: three looks on real ground (`view/`, `devlog/20261122-view-tests.md`). Anselm to choose.
   - [x] Building heights: Microsoft's estimates for 3,355 of 4,216 buildings.
   - [x] Checked against the lidar and replaced by measurements (Microsoft's were 0.4 m low at the median).
   - [x] Trees, now from the lidar points (public domain); the canopy model is no longer used.
   - [x] A wider window: 6 km square, with the harbors and Marin City (`devlog/20261122-a-wider-window.md`).
   - [ ] A try on a phone; named views for the harbors and Marin City; aerial photographs on the ground.
3. [x] (esimv1) The engine runs a project by path and a project names the engine it needs (`engine = "0.3.0"`); esimv1 was cut into a hub, `esimv1-core`, `esimv1-viewer` and scenario repositories on 2026-11-22. Here that waits for a manifest: the project folder will be a subfolder of this repository.
4. [ ] (esimv1) Object storage: a mirror of fetched sources first, baked runs second. Not needed until there are runs to publish or a second machine has to run a scenario.
5. [ ] (esimv1) Runs in real time on the player's device (Anselm, 2026-11-22: "probably requires some re-architecting"). The seams it needs: a run that loads a prepared bundle and never touches disk or network, a kernel that can be stepped and handed events between steps, and results kept in memory. Build those natively first, then try a WebAssembly build of one small scenario.

## The story

- [x] README tells what the model is and what it would let a resident try (first draft, 2026-11-22; renamed and brought up to date 2026-11-23).
- [ ] Check every row of `devlog/20261122-what-sausalito-is-deciding.md` against a primary page; most are search summaries.
- [ ] A licence file.
- [ ] Choose the first question. Not chosen yet; it is Anselm's to choose. Four candidates with what would test each: `devlog/20261123-questions-it-could-answer.md`.
- [x] The term: **The Sausalito Model** on the page, the README and the notes (Anselm, 23 November: "some people don't like 'playable'"). The folder, the repository name and dated devlog entries keep the old word. "Playable place" as the general term is his to keep or drop.

## The ground
- [ ] The window: city limits, plus how much of Richardson Bay, Marin City and the headlands.
- [ ] Elevation fine enough for the question (the engine's 30 m Copernicus grid is too coarse for shallow flooding). (esimv1: a lidar reader)
- [ ] Buildings with heights. Source to be chosen.
- [ ] Parcels and zoning, and their licence.

## The engine as a package
- [ ] (esimv1) Load and run a project that lives outside the esimv1 tree.
- [ ] (esimv1) A prepared bundle per scenario, so a run fetches nothing.
- [ ] (esimv1) Play: start at a chosen moment, set conditions, run to a limit, stop early, change and rerun from that moment.
- [ ] How this repository names the engine version it runs on.

## The view
- [ ] A solid style: lit terrain, buildings as bodies, water, sun position by date and hour.
- [ ] Decide what is copied from esimv1's viewer and what is imported.

- [x] Heights and trees from the 2018 lidar points: 4,194 of 4,216 buildings measured, trees from a public-domain source and now committed. `devlog/20261122-reading-the-lidar.md`.
- [ ] Roof shapes from the same points; a look at the 1,299 tree bodies over 45 m.
- [x] Water that moves, at the tide gauge's level, with the wind and sky from live observations: `devlog/20261122-water-tide-and-sky.md`. `view/lib/{tide,sky,water}.js` are written to be shared.
- [ ] A tide correction from San Francisco to Sausalito; fixed piers told apart from floating ones; a sea bed, so a low tide can be drawn.
- [ ] (esimv1) Let the catalog list live feeds a page reads, and let a scenario add its own entries.

- [ ] Collect the best ideas from residents: a way to keep, share and compare what people tried (Anselm, 2026-11-22: "we will eventually definitely collect best ideas from citizens - later").

## Directions from Anselm, 22 November 2026 (none started)
- [x] Its own address: https://sausalito.exe.xyz/ serves the view (22 November). A domain of its own, if wanted, is bound with the harness's `exe-domain`.
- [ ] A conversational interface. "the sausalito model should probably have a conversational interface". A person asks in words; the answer's numbers come from runs and from nothing else.
- [x] A layer of local news and media: the page asks the inhaler (`anselm/inhaler`, https://inhaler.exe.xyz/) and shows issues, facts around the date on the slider, and pins (`devlog/20261122-news-on-the-page.md`). Next: news beside a scenario's own timeline, once there is one.
- [ ] Words. "i should probably use the term scenario rather than model ... will want to make sure i am consistent in my language". The README and the essay say "model" throughout; change them once he settles it.

- [x] A clean page: panels closed behind three buttons, a one-line readout (23 November).
- [x] A "layers" button with fourteen public maps read from their publishers, and a card for a clicked building or spot (`devlog/20261123-layers-and-options.md`).
- [ ] More layers: census blocks, the housing sites lists, NOAA's flood depths, the bay floor, the county's tide sensor if its readings are public.
- [ ] The news panel is a list of text; show it better (on the timeline, on the map, by issue).
- [ ] Options in front of people: the ten notes in that entry. Waits on the first question.

- [x] A tour when the page is left alone, and a fourth, dark look (`devlog/20261123-a-tour-and-a-fourth-look.md`). Watch the tour run and tune it; a turn-rate limit and a bank, as in bay-area-twin.
- [ ] Group the layers panel by kind (ground and water, forces, living things, the built town, people and rules); a "layers apart" way of looking.

## Later
- [ ] Who maintains it. Tabled on 2026-11-22.
