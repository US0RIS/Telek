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
telek gap                      # milestones vs shock-saturation bound
telek saturation --freq 40000 --range 1 --aperture-area 0.07 --target-area 0.008
telek link --freq 40000 --range 0.25 --aperture-diameter 0.2 --target-diameter 0.04 \
    --electrical-power 50 --efficiency 0.1 --max-acoustic-power 10 --mass 0.01
python -m pytest
```

Example interpretation: `telek hold --mass 0.5` reports the *ideal lower-bound* incident acoustic power needed merely to counter gravity for a 500 g object. It is not a hardware design value; real systems incur coupling, focusing, reflection, geometry, propagation, thermal, and safety losses.

## Current headline result

Nonlinear shock saturation in air caps the acoustic intensity that can arrive at range `L`, however strong the source: `I_sup = pi^2 rho c^5 / (3 beta^2 omega^2 L^2)` (about 207 W/m^2 at 1 m, 40 kHz). With a wearable aperture this rules out M4 (500 g at 3 m) for airborne acoustic radiation pressure by 2-3 orders of magnitude, makes M3 marginal, and leaves M2 open. See `docs/PHYSICS.md` for the derivation and its stated loopholes.

## Current milestone

**M0 — quantify the gap.** Build a trustworthy digital model that can answer: for a desired object mass, acceleration, range, aperture, and power budget, what would the actuator have to achieve? Keep ideal limits separate from engineering estimates and measured data.

The next contributor should start with [`HANDOFF.md`](HANDOFF.md).
