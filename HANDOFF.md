# Telek contributor handoff

## Read this first

Telek is not a smart-home project and not a staged magic trick. The user is trying to determine how close technology can get to **the Force as literal remote manipulation of matter**, with one hard constraint added during project definition:

> A considerable idea cannot be constrained to an isolated/prepared location or depend on things we already set up there.

That requirement is captured formally in `CRITERIA.md` and should not be softened without an explicit user decision.

## Product/research intent

The desired interaction is deliberately understated: a wrist muscle/EMG interface detects small intentional hand/finger gestures, and the physical world responds. Large theatrical gestures are unnecessary. EMG is the current preferred intent sensor because it can detect motor intent with less visible motion than camera/IMU-only gesture recognition.

However, **gesture recognition is not the main unsolved problem**. The bottleneck is portable remote momentum transfer into arbitrary, unmodified macroscopic objects.

## Current best lead

The current first lead is airborne phased ultrasound / acoustic radiation force. Reasons:

- real momentum transfer through air;
- does not fundamentally require ferromagnetic targets;
- beam/field shape can be electronically controlled;
- acoustic trapping, levitation, translation and torque are established phenomena at smaller scales.

Do not infer that current systems meet Telek's payload/range requirements. They do not. Treat ultrasound as a mechanism whose scaling gap must be quantified.

## Work completed in the foundation pass

1. Defined non-negotiable project criteria and milestones in `CRITERIA.md`.
2. Defined a modular architecture in `docs/ARCHITECTURE.md`.
3. Added a conservative acoustic-physics module exposing ideal momentum-flux bounds.
4. Added a gesture-to-force-command abstraction that is independent of specific EMG hardware.
5. Added tests intended to prevent unit/sign/assumption errors.
6. Added a CLI for fast feasibility calculations.

## Work completed in the second pass (engineering + nonlinear model)

1. `telek.atmosphere`: air state and ISO 9613-1 absorption (checked against the standard's 1 kHz table value; ~1.32 dB/m at 40 kHz).
2. `telek.nonlinear`: lossless weak-shock mean-square pressure for an initially sinusoidal plane wave, and the **shock-saturation supremum** `I_sup(L) = pi^2 rho c^5 / (3 beta^2 omega^2 L^2)`, extended to converging/collimated/diverging ray tubes as `P_delivered <= I_sup(L) * max(A_ap, A_t)`.
3. `telek.linkbudget`: explicit electrical -> acoustic -> absorption -> diffraction-capture -> saturation-cap -> force chain, with a reported limiting factor.
4. `telek.gap` / `telek gap`: CRITERIA milestones vs the saturation bound.
5. Derivation, assumptions and loopholes in `docs/PHYSICS.md`; 28 new tests.

## Work completed in the third pass (cross-mechanism screen)

1. Added `telek.mechanisms` with explicit screening models for directed airflow, optical radiation pressure, electrostatic induced-dipole coupling, and weak-material magnetic susceptibility.
2. Added `telek screen` for an apples-as-possible comparison at a common target mass/range/size.
3. Added `docs/MECHANISMS.md` with derivations, caveats, reference numbers, and directionality/target-scope failures.
4. Corrected the acoustic language: the shock result is a **weak-shock model ceiling**, not a universal impossibility theorem.
5. Added regression tests for the new scaling laws and inverse calculations.

## Current best understanding

- **The current weak-shock acoustic model puts M4 2-3 orders of magnitude short.** At 3 m it gives ~0.01-0.04 N from a 0.3 m aperture (20-40 kHz) against 4.9 N needed; at 40 kHz the modeled area requirement is ~36 m^2. This is strong negative evidence inside the model, not a universal proof across every nonlinear beam geometry.
- **M3 is marginal**: sliding a 100 g object at 1 m only clears the bound near 20 kHz (audible edge) with a 0.3 m aperture; lifting it does not clear the bound.
- **M2 is open**: not saturation-limited. It is decided by source power, efficiency, diffraction and real-array losses, i.e. by engineering data and experiment.
- **Directed airflow is the raw-force leader in the first mechanism screen.** A centered 5 cm round jet at 100 m/s is estimated at ~1.18 N on a 10 cm target 3 m away with ~1.18 kW ideal jet kinetic power. Matching the 4.903 N M4 weight benchmark would require ~204 m/s and ~10 kW ideal kinetic power in the same model. That is surprisingly close numerically, but it is push-only, noisy, turbulent, and non-selective.
- **Optical radiation pressure is eliminated by momentum economy** for macroscopic M4: perfect reflection needs ~735 MW of incident optical power merely to equal 4.903 N.
- **Electrostatic induced-dipole and generic weak-material magnetic forces collapse with range** in the current idealized screens (r^-5 and r^-7 respectively). Magnetics can be excellent on ferromagnetic targets, but that fails the arbitrary-target criterion.
- Ultrasound remains the best-understood candidate for M1/M2 and the only modeled mechanism here with plausible structured push/pull semantics, but its M4 case must survive full diffraction/nonlinearity validation.
- Saturated acoustic momentum that becomes streaming belongs in the airflow budget; do not count it twice.

## Immediate next work

Prefer work that reduces uncertainty in the actuator bottleneck. Good next steps, roughly in order:

1. **Attack the acoustic weak-shock loopholes quantitatively.** Implement or validate against a KZK/full diffraction-nonlinearity model; compare against published high-amplitude focused-air measurements; test structured/Bessel/parametric/difference-frequency cases. The next model should try to falsify the current 2-3-order M4 shortfall, not merely restate it.
2. **Deepen airflow beyond the simple round-jet baseline.** Evaluate pulsed jets/vortex rings, suction/entrainment, opposed or steerable jet geometries, and whether any portable fluid architecture can provide a genuine pull or hold without target preparation. Keep collateral disturbance/selectivity explicit.
3. **Search for omitted coupling mechanisms.** In particular: electrohydrodynamic/ionic flow (count momentum honestly as airflow), eddy-current forces on arbitrary conductors, microwave/RF radiation pressure or near-field forces, plasma/shock impulse, and hybrid fields. Reject mechanisms that only look good after choosing a favorable target.
4. **Literature evidence table** (`data/` + loader) with measured payload/range/pressure/aperture/force values and citations, separating single-sided portable architectures from enclosing arrays/chambers.
5. Closed-loop simulation after a mechanism has a credible force envelope. Only after that add EMG hardware adapters; preserve the generic intent API.

## Important reasoning constraints

- Do not answer the actuator problem by renaming it (e.g. "we need a portable tractor beam"). Identify an actual coupling mechanism and quantify it.
- Do not "solve" portability by putting infrastructure in the room.
- Do not "solve" arbitrary objects by adding magnets/tags to the object.
- Do not optimize software latency while the force budget is orders of magnitude short.
- Do not bury negative results. A rigorous proof that a mechanism cannot reach a milestone within plausible power/aperture limits is valuable progress.
- Distinguish **upper-bound physics** from **device engineering** and **experimental measurements** at all times.

## Safety / experimental discipline

This repository starts as modeling software. Any future hardware backend should default to simulation, require explicit arming, enforce independently configured energy/force/duty-cycle limits, and fail closed if sensing or interlocks are unavailable. Do not make a model-generated trajectory directly drive a high-energy actuator.

## Definition of a useful turn

Leave the repository more falsifiable than you found it: add code, data, tests, or an experiment design that can rule mechanisms in or out against quantitative Telek milestones. Update this handoff when your work changes the project's best current understanding.
