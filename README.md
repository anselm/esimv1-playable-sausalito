# Playable Sausalito

A playable model of Sausalito, California: a simulation of the town that anyone can set
conditions on, run forward, and compare with what would have happened otherwise.

**Where it stands (22 November 2026): a sketch.** This repository holds the idea, a
first reading of the town and a list of work. There is no simulation here yet.

## The idea

A town makes a few large decisions each decade and lives with them for generations:
where homes go, what to do about a shoreline, how visitors arrive. Residents and
officials can argue about these in advance. They cannot try them.

A playable model lets them try. A person picks a moment, sets conditions, and presses
play. The town runs forward for a season or for thirty years, and the model reports what
changed, for whom, and at what cost. Then the person changes one thing and runs it
again.

Here is the kind of thing it should make possible. This example is invented to show the
shape, and no part of it has been computed:

> A resident picks the year 2040 and a high tide on a stormy day. The road to the
> working waterfront is under water, and so is the pipe beneath it. They try raising
> the road. The flooding there stops, the water goes somewhere else, and the model says
> where, what it cost, and which agency would have to agree. They try leaving the road
> and moving the pipe instead, and compare the two.

A flood map already shows where the water would stand, and Sausalito has several. A
playable model shows the choices and what follows from each of them.

It is not a forecast. Each run answers "what follows if these assumptions hold", with
the assumptions and their sources shown beside the result.

## What the town is deciding

A first reading found these subjects in front of the town in 2025 and 2026: a state
requirement to plan for 724 new homes, the future of the Marinship working waterfront,
a shoreline plan for rising water, the end of the anchorage on Richardson Bay, visitors
and parking, the stability of the hillside, and the neighbours just over the city line.
Most of the levers are held by someone other than the city.

The reading, its sources and how far to trust each claim are in
[devlog/20261122-what-sausalito-is-deciding.md](devlog/20261122-what-sausalito-is-deciding.md).
Much of it comes from search summaries and has to be checked against primary pages.

Which of these the model takes up first has not been decided.

## How it will be built

The simulation runs on [esimv1](https://github.com/anselm/esimv1), an open simulation
engine in which a scenario is a manifest of modules on one clock, every run can be
repeated exactly, and each module states its sources and its known faults. This is the
first scenario kept outside that engine's own repository, so it also tests the engine as
something other projects can depend on.

This repository holds what is particular to Sausalito: the scenario, its data tables,
its pages and its notes. The work ahead is in [todo.md](todo.md).

## For any town

[A town and its playable model](devlog/20261122-a-town-and-its-playable-model.md) is a
draft essay on the questions outside the code: which decision to start from, who holds
each lever, counting more than one bottom line, trust, who is left out of a model, and
who keeps it alive.

## Free and open

Everything here is free and open source, and contributions are welcome. A licence file
has not been added yet.

## Notes

Dated working notes are in [devlog/](devlog/), beginning with
[how the project started](devlog/20261122-init.md).
