# Telek

Telek is an R&D project aimed at getting as close as physically possible to **portable, real-world telekinesis**: deliberate, discreet hand intent causing ordinary physical objects to move at a distance.

The project is intentionally stricter than gesture control, smart-home automation, or a staged demo. Read [`CRITERIA.md`](CRITERIA.md) before proposing or implementing anything; it defines what counts.

## Current thesis

The input problem is comparatively tractable: wrist-worn EMG can provide a low-motion, deliberate command channel. The hard problem is the actuator: transferring useful momentum to an **unmodified object in an unprepared environment** from a portable system.

The first actuator family being modeled is **airborne phased ultrasound / acoustic radiation force**, because it can exert real contactless force on non-magnetic matter and can, in principle, synthesize steerable pressure fields. Telek does **not** assume that today's ultrasonic hardware is powerful enough. The initial software exists to quantify that gap rather than hand-wave it.

## Repository map

- [`CRITERIA.md`](CRITERIA.md) — project constitution / acceptance criteria.
- [`HANDOFF.md`](HANDOFF.md) — context for the next AI or human contributor.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system architecture and module boundaries.
- [`docs/PHYSICS.md`](docs/PHYSICS.md) — actuator physics, assumptions, and open questions.
- `src/telek/` — executable physics/control model.
- `tests/` — regression tests for the model.

## Quick start

Requires Python 3.11+.

```bash
python -m pip install -e .
telek hold --mass 0.5
telek force --power 1000
python -m pytest
```

Example interpretation: `telek hold --mass 0.5` reports the *ideal lower-bound* incident acoustic power needed merely to counter gravity for a 500 g object. It is not a hardware design value; real systems incur coupling, focusing, reflection, geometry, propagation, thermal, and safety losses.

## Current milestone

**M0 — quantify the gap.** Build a trustworthy digital model that can answer: for a desired object mass, acceleration, range, aperture, and power budget, what would the actuator have to achieve? Keep ideal limits separate from engineering estimates and measured data.

The next contributor should start with [`HANDOFF.md`](HANDOFF.md).
