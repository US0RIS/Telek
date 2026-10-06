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

## Current best understanding

- **Airborne acoustic radiation pressure cannot reach M4 from a wearable aperture.** At 3 m the saturation ceiling gives ~0.01-0.04 N from a 0.3 m aperture (20-40 kHz) against 4.9 N needed; at 40 kHz the aperture would have to be ~36 m^2. This holds for any transducer power or efficiency, within the stated model (see loopholes in `docs/PHYSICS.md`).
- **M3 is marginal**: sliding a 100 g object at 1 m only clears the bound near 20 kHz (audible edge) with a 0.3 m aperture; lifting it does not clear the bound.
- **M2 is open**: not saturation-limited. It is decided by source power, efficiency, diffraction and real-array losses, i.e. by engineering data and experiment.
- Ultrasound therefore remains the best-understood candidate for M1/M2 but is very unlikely to be the M4 mechanism. The mechanism comparison (next item) is now the highest-value work.
- Saturated wave momentum becomes acoustic streaming (wind). Any claim that streaming rescues ultrasound must be evaluated as an airflow mechanism, with airflow's selectivity problems.

## Immediate next work

Prefer work that reduces uncertainty in the actuator bottleneck. Good next steps, roughly in order:

1. **Mechanism comparison model** (`telek.mechanisms`?) for directed airflow / streaming jets, electrostatics, magnetics (eddy-current on conductors included), optical radiation pressure, and any credible demonstrated coupling. Each needs the same treatment ultrasound now has: a source-independent physical ceiling at range plus an explicit engineering chain. Score against `CRITERIA.md` without favorable targets. Airflow/streaming should be next, since it is where saturated acoustic momentum goes.
2. **Attack the saturation bound's loopholes** quantitatively: (a) find published focused-beam measurements in air at high amplitude and compare with `I_sup`; (b) check whether a KZK-type diffraction+nonlinearity model changes the conclusion by more than a small factor; (c) parametric/difference-frequency schemes.
3. **Literature evidence table** (`data/` + loader) with measured payload/range/pressure/aperture values and citations, separating single-sided portable architectures from enclosing arrays/chambers. Use it to calibrate `electroacoustic_efficiency` and `max_acoustic_power_w` for commodity 40 kHz arrays instead of guessing.
4. Closed-loop simulation: target state + noisy pose observations + force-command controller + actuator saturation, using `LinkBudget.force_n` as the actuator ceiling.
5. Only after the actuator model is informative, add EMG hardware adapters. Preserve the generic intent API.

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
