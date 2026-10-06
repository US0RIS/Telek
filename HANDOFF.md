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

## Immediate next work

Prefer work that reduces uncertainty in the actuator bottleneck. Good next steps, roughly in order:

1. Add an **engineering acoustic model** distinct from the ideal bound: aperture, focusing gain/loss, atmospheric absorption, target acoustic impedance/reflection coefficient, geometry, duty cycle, and transducer efficiency. Keep every parameter explicit.
2. Build a **mechanism comparison model** for airborne ultrasound, directed airflow, electrostatics, magnetics, optical radiation pressure, and any credible exotic-but-demonstrated coupling mechanism. Score each against `CRITERIA.md` without assuming favorable targets.
3. Add a **literature evidence table** with measured payload/range/pressure/intensity/aperture values and citations. Do not mix papers using surrounding arrays/chambers with portable single-sided architectures.
4. Build the closed-loop simulation: target state + noisy pose observations + force-command controller + actuator saturation.
5. Only after the actuator model is informative, add EMG hardware adapters. Preserve the generic intent API so Meta-like sEMG, CTRL-labs-style hardware, or future bands can plug in.

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
