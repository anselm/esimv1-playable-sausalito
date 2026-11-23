# Chores

Open work for this repository, one line each. Engine work that has to happen in esimv1
is marked (esimv1) and is also noted there.

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

- [x] README tells what a playable Sausalito is and what it would let a resident try (first draft, 2026-11-22).
- [ ] Check every row of `devlog/20261122-what-sausalito-is-deciding.md` against a primary page; most are search summaries.
- [ ] A licence file.
- [ ] Choose the first question. Not chosen yet; it is Anselm's to choose. Four candidates with what would test each: `devlog/20261123-questions-it-could-answer.md`.
- [ ] Settle the term: "playable Sausalito", "playable place", or another.

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
- [ ] A "layers" button: parcels, zoning, housing sites, flood maps, evacuation zones, hazards, census, each fetched from its publisher; a card for a clicked building or lot.

## Later
- [ ] Who maintains it. Tabled on 2026-11-22.
