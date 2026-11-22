<!-- author: Claude (machine draft, for Anselm to rewrite) -->
<!-- ordered-by: Anselm -->
<!-- written: 2026-11-22 -->
<!-- revised: 2026-11-22 -->
<!-- revision: 1 -->
# A town and its playable model

This page is for any town thinking about a playable model of itself. Sausalito is the
town this repository works on, but the questions here are not about Sausalito. They are
the questions that sit outside the code and decide whether the code is worth writing.

## What a playable model is

A map shows where things are. A dashboard shows what was measured. A playable model
computes what happens next. A person picks a moment, sets some conditions (a seawall
here, two hundred homes there, a ferry every twenty minutes), presses play, and watches
the town run forward under those conditions for a season or for thirty years. Then they
change a condition and run it again.

The purpose is rehearsal. A town makes a few large decisions each decade and lives with
them for generations. It can argue about them in advance, but it cannot try them. A
model lets residents and officials try a decision, see who gains and who pays, and be
surprised before the surprise is expensive.

A playable model is not a forecast. Each run answers "what follows if these assumptions
hold", and the assumptions are on the page. A town should refuse any model that hides
them.

## Start from what the town is already deciding

A model of everything is a promise nobody can keep. A useful first model takes one
decision that is already in front of the council and is hard for a resident to picture:
where new housing goes, what to do about a shoreline that floods, how visitors arrive.
The town should be able to say the question in one sentence before anyone writes code.

Then list the real choices. They are the options under discussion, in the words used at
the meeting, and the option of doing nothing. A resident should recognise each one. A
panel of sliders that nobody proposed is not a choice.

## Find out who holds each lever

A town controls less than its residents think. In most places the state sets housing
targets, a regional body governs the shoreline, a transport agency owns the main road,
and special districts run the water, the sewers and the fire engines. A model that lets
a player change something the town cannot change teaches the wrong lesson.

So each choice in the model carries the name of the body that can make it. This is
often the most useful thing a resident learns: which meeting to go to.

## Count more than one bottom line

Every choice in a town moves several accounts at once: homes, travel time, flooded
days, the city budget, the bay, the view, the character of a street. A model should
report them side by side and say who bears each cost. It should not add them into one
score, because the weights in a score are a political decision, and that decision
belongs to the town and not to the model's builders.

It should also say when something breaks instead of bending. A road that floods ten
days a year is a nuisance. A road that floods sixty days a year stops being a road, and
the businesses on it close. That difference between stretching and tearing needs a
stated threshold for each account, with a reason for the number. Where the model cannot
represent a kind of breaking at all, the page should say so.

## Trust runs both ways

Residents will ask whether a model the city supports is built to sell the city's plan.
Officials will ask whether a model they do not control will be used against them. The
same three practices answer both:

- The code and the data are open, and anyone can rerun any result.
- Every assumption is stated beside the result that depends on it, with its source or
  the word "guess".
- Known faults are published and kept current.

A model that is wrong in public can be corrected. One that is trusted and wrong cannot.

## Who is in the model, and who is left out

The people easiest to model are the ones with records: owners of parcels, registered
voters, licensed businesses. A town also holds renters, people who live on boats, people
who work there and sleep elsewhere, people with no address, and neighbours just over the
city line who share its roads and floods. The bay, the hillside and the species in them
are affected too and attend no meetings. A model should say which of these it
represents, and ask the people concerned how they wish to be represented.

Privacy needs a decision before any data is loaded. Parcel records are public, but a
household is not. A model can work on blocks and totals instead of named homes, and it
does not need to record what any resident tried.

## Does the town speak?

It is tempting to give the model a voice and let a town answer questions about itself.
A town is in some sense alive: it has habits, memory and interests that outlast any
council. But a voice needs someone to authorise it. Until a town has decided who that
is, the model should show and compute, and people should do the speaking.

## Cost and upkeep

Everything in this repository is free and open source. That does not make a model free
to build or to run. The costs are people's time, computing, data that someone has to
keep current, and the hosting of a public site. A town that wants one can pay for those
directly, give them in kind (its data, its staff's knowledge, a room for a workshop), or
support an organisation that does the work.

Upkeep is the open question. A model that looked current and is five years stale is
worse than none. Who keeps a town's model alive after the first decision has been made
is not answered here yet.

## Further reading

- [How to write your own digital twin](https://esimv1.exe.xyz/docs/guides/writing-a-digital-twin),
  the general guide this page leans on, especially its sections on bottom lines and on
  what surrounds a simulation.
- [digitaltwins.wiki](https://digitaltwins.wiki), a collection of tools, data and
  examples from the field.
- Bret Victor, [Explorable Explanations](https://worrydream.com/ExplorableExplanations/)
  (2011). "Playable" is a step on from "explorable": the reader does not only vary a
  number in an explanation, they run a place forward.
