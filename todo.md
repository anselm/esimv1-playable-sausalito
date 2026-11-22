# Chores

Open work for this repository, one line each. Engine work that has to happen in esimv1
is marked (esimv1) and is also noted there.

## Next, in order (Anselm's four, 2026-11-22)
1. [x] Research, second pass, from primary pages: `devlog/20261122-sausalito-from-primary-pages.md`. Still open: the certified election result (25 November), who is mayor for 2027, the terms of the county's data, the older flood and subsidence studies.
2. [x] View tests: three looks on real ground (`view/`, `devlog/20261122-view-tests.md`). Anselm to choose.
   - [x] Building heights: Microsoft's estimates for 3,355 of 4,216 buildings.
   - [ ] Check those heights against the lidar point cloud; 825 buildings (houseboats among them) are still placeholders.
   - [x] Trees, from the 2018 canopy height model (its licence is not stated: find the terms before publishing the derived file).
   - [ ] A wider window; a try on a phone; aerial photographs on the ground.
3. [ ] (esimv1) Run this repository as a project by path, with the engine version it needs named here. See the esimv1 devlog of 2026-11-22.
4. [ ] (esimv1) Object storage: a mirror of fetched sources first, baked runs second. Not needed until there are runs to publish or a second machine has to run a scenario.
5. [ ] (esimv1) Runs in real time on the player's device (Anselm, 2026-11-22: "probably requires some re-architecting"). The seams it needs: a run that loads a prepared bundle and never touches disk or network, a kernel that can be stepped and handed events between steps, and results kept in memory. Build those natively first, then try a WebAssembly build of one small scenario.

## The story

- [x] README tells what a playable Sausalito is and what it would let a resident try (first draft, 2026-11-22).
- [ ] Check every row of `devlog/20261122-what-sausalito-is-deciding.md` against a primary page; most are search summaries.
- [ ] A licence file.
- [ ] Choose the first question. Not chosen yet; it is Anselm's to choose.
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

- [ ] A height-above-ground raster from the 2018 lidar point cloud (first returns less the bare ground). It would measure building heights, fill the 825 placeholders where the survey saw them, and give trees from a public-domain source, so the tree file could be committed. No splat: the survey has no colour.
- [ ] Water that moves (Anselm, 2026-11-22: "more for just visual appeal than real 'simulation value'"): a shader on the bay, its level from the tide gauge and its chop from the measured wind where that is cheap. Label on the page what is measured and what is decoration.
- [ ] Real weather on the view: sky and light from the current observation.

## Later
- [ ] Who maintains it. Tabled on 2026-11-22.
