# The Sausalito Model (folder: playable-sausalito)

Project-specific orientation only. House policy (devlog, git, UX, writing,
deploy) comes from the harness and is not repeated here.

## What this is

The Sausalito Model (its name since 2026-11-23, when Anselm said "some people don't like 'playable'"; before that, Playable
Sausalito; the repository is `esimv1-sausalito-model` since 2026-11-24; the folder and the dated devlog entries keep the old word). A model of
Sausalito, California, that people can try things on: a simulation of the town that a resident or
an official can set conditions on, run forward and compare. It is public, free and open
source. It is also the first scenario kept outside the esimv1 repository, so it tests
esimv1 as a simulation core that other projects depend on. As of 2026-11-22 it is a
sketch: a story, an essay and a chore list, with no simulation yet. Not deployed.

## Where things are

- Code: this folder. Repo: `anselm/esimv1-sausalito-model` (public; created 2026-11-22 as `playable-sausalito`, then `esimv1-playable-sausalito`, renamed 2026-11-24 on Anselm's word "Rename repo"; GitHub redirects the old names; the folder keeps its name).
- Devlog: `devlog/` (dated entries; read the tail first).
- Chores: `todo.md`. Engine chores marked (esimv1) are done in
  `~/projects/2026/earth-simulator-1`, which has its own room and rules.
- Everything written goes in `devlog/` as dated entries; there is no `docs/` folder
  (Anselm, 2026-11-22). An essay there keeps the stamp lines esimv1's docs use.
- Deploy: none yet; see `project.toml`.

## Project-specific facts

- This repository holds scenario content only: manifest, record tables, pages, essays.
  Any new Rust module goes in esimv1 (Anselm, 2026-11-22).
- The repository is public. Nothing about pitching, fundraising or private
  conversations belongs in it; Anselm keeps those notes himself.
- The first question the model answers has not been chosen. Do not build the scenario
  ahead of Anselm's word on it (2026-11-22: "i don't want you to run ahead on the actual
  scenario").
- `devlog/20261122-a-town-and-its-playable-model.md` is a machine draft of an essay that is his to
  rewrite.

## Live (since 2026-11-22)

https://sausalito.exe.xyz/ (exe.dev VM `sausalito`, unit `sausalito.service`, port 8000, public) serves `view/` through
`deploy/serve.mjs`. `deploy/deploy.sh` puts the current folder there; it is run by hand on Anselm's say and a push does
not deploy. Anselm: "i want to be able to show off the sausalito model live on the web even in the early stages".

## Interface

Open the harness's `house-ux` skill before changing the page. It was not opened for the first two days and the page had to
be reworked on 2026-11-23 (`devlog/20261123-house-style.md`): one floating menu button at the top right, one panel open at a
time, corners of 4 px or less, checked by screenshot in light and dark (`DARK=1 node view/tools/shot.mjs ...`). The page is
still one HTML file with its own CSS, not Svelte and Tailwind; that move waits until the demo's shape settles.


- 24 November 2026 (`devlog/20261124-volumes-news-propositions-boats.md`): a layer in `view/lib/layers.js` may set `form` (`volume`, `curtain`, `labels`), `height_m` and `flat`; news is the layer `news` (no menu button); the panel is called propositions, never a game (Anselm), and its propositions are moderate ones with a `life` dial; `view/tools/boats.py` writes `view/data/boats.bin` from `cache/dsm1.bin` (rerun after `prepare.py`).
