# Cross-mechanism screen

This document answers a narrower question than "what could move an object?":

> Which known physical coupling mechanisms have a credible path toward portable,
> unprepared-environment, unmodified-target manipulation?

The calculations live in src/telek/mechanisms.py. They are deliberately simple
screening models, not hardware specifications. A mechanism can look numerically
strong and still fail Telek because it only pushes, only works on special
materials, is conspicuous, or cannot be made safe/portable.

## Reference case

For comparison, use the M4 geometry unless otherwise stated:

- target mass: 0.5 kg;
- target diameter: 0.10 m;
- range: 3 m;
- wearable emitter envelope: 0.30 m diameter;
- required force merely to counter gravity: 4.903 N.

Representative results from the current models:

| mechanism | reference assumption | force at target | margin vs 4.903 N | key failure mode |
|---|---|---:|---:|---|
| airborne acoustic radiation pressure | 40 kHz, 0.30 m aperture, weak-shock model ceiling | 0.00949 N | 0.00194x | model says far too little force at 3 m |
| round free air jet | 0.05 m nozzle, 100 m/s exit, centered target | 1.18 N | 0.240x | push-only, noisy, turbulent, disturbs everything in beam |
| optical radiation pressure | 1 kW optical power, perfect reflection | 6.67e-6 N | 1.36e-6x | photon momentum is intrinsically tiny per watt |
| electrostatic induced dipole | 0.15 m source radius, 3 MV/m source surface field, conducting-sphere target limit | 5.22e-7 N | 1.06e-7x | r^-5 and target polarizability; high-field/corona constraints |
| weak-material magnetic susceptibility | 0.15 m source radius, 2 T source-surface field, |chi|=1e-5 | 2.60e-10 N | 5.31e-11x | r^-7 and severe material dependence |

These values are not equally rigorous. The acoustic number is a model ceiling
under specific weak-shock/ray assumptions. The airflow result is an engineering
estimate. The electric and magnetic rows are idealized spherical/dipole screens.
The optical row is a momentum-flux bound.

## 1. Directed airflow: currently the raw-force leader

For an ambient-pressure round jet,

    thrust = rho A v^2
    kinetic power = 0.5 rho A v^3

The far-field capture model uses the standard self-similar turbulent round-jet
profile reported in engineering references such as Perry's Chemical Engineers'
Handbook:

    Uc/U0 ~ 6.2 D/x
    log10(Uc/U(r)) ~ 40 (r/x)^2

for the developed round jet. Integrating U^2 over a centered circular target
gives the momentum-capture fraction used by telek.mechanisms.

For the M4 reference target, a 5 cm nozzle would need about:

- 204 m/s exit velocity;
- 10.0 kW of ideal jet kinetic power;

to produce 4.903 N on a perfectly centered 10 cm target at 3 m in this model.

That is unexpectedly close in raw force compared with the field mechanisms,
but it does not reproduce general telekinesis. An open jet naturally pushes
away from the source; it does not give a clean pull, hold, or arbitrary 3-D
force vector. It is also conspicuous and couples strongly to nearby material.

Research implication: airflow is worth keeping as a baseline and possibly as
an M1/M2 "physical world moved at range" mechanism, but not as the final Force
mechanism unless a genuinely directional/bidirectional fluid architecture is
found.

## 2. Optical radiation pressure: clean steering, impossible momentum economy

For a passive target,

    F <= 2 P / c_light

under perfect normal reflection.

One newton therefore needs about 149.9 MW of incident optical power. Countering
the weight of the M4 0.5 kg object needs about 735 MW even before propagation,
capture, reflectivity, thermal damage, or safety losses.

This mechanism is eliminated for macroscopic Telek by the basic momentum-per-
energy ratio, not by current laser engineering.

## 3. Electrostatic induced-dipole force: attractive but range collapses

A neutral polarizable sphere in a nonuniform electric field experiences
dielectrophoretic force. In the point-dipole approximation,

    F_DEP = 2 pi eps0 a^3 K grad(E^2)

in air for a spherical target, where K is the polarizability / Clausius-Mossotti
factor. For an idealized charged spherical emitter with

    E(r) = E_surface (R/r)^2,

the force scales as r^-5.

The current reference uses K=1, the conducting-sphere limit, so it is deliberately
favorable. Even then the 3 m force is sub-micronewton. The model does not include
corona, leakage, environmental grounding, or exposure constraints.

This is interesting only at short range unless a radically different field
geometry changes the range scaling.

## 4. Magnetics: excellent on the right target, poor universal mechanism

For a weak linear magnetic material,

    F = chi V grad(B^2) / (2 mu0).

The screening source is a dipole-like field,

    B(r) = B_surface (R/r)^3,

which makes the weak-material force scale as r^-7.

A ferromagnetic steel target can respond orders of magnitude more strongly than
the |chi|=1e-5 reference case. That does not rescue magnetics as Telek's universal
mechanism because CRITERIA.md does not permit choosing or modifying the target
to make the effect work.

Magnetics remain relevant for a conditional "Force on metal" mode, not for the
core arbitrary-object goal.

## 5. Acoustic radiation pressure: retain, but downgrade the certainty

The current weak-shock model places a strong source-power-independent ceiling
on delivered 20-40 kHz radiation-pressure force at meter scales. It is evidence
against M4 ultrasound, not a theorem covering every nonlinear acoustic field.

Before closing this path, the project should attack the assumptions directly:

1. implement or import a KZK/full diffraction-nonlinearity calculation;
2. compare the model with published high-amplitude focused-air measurements;
3. examine structured/Bessel/parametric fields and difference-frequency ideas;
4. separate radiation pressure from streaming, which belongs in the airflow
   momentum budget.

## Current ranking

For raw force on ordinary objects at meters:

1. directed airflow;
2. airborne acoustics (if the weak-shock model survives validation);
3. electrostatics;
4. optical radiation pressure;
5. weak-material magnetics.

For actual Star-Wars-like semantics, none wins. Airflow lacks pull/hold and
selectivity; acoustic force is too weak in the current model; electrostatic and
magnetic fields collapse with range/material constraints; optical momentum is
energetically hopeless.

That means the next breakthrough should be searched for in one of two ways:

- find a known coupling mechanism omitted from this table that has much better
  range scaling and bidirectionality; or
- find a way to turn the strongest existing portable mechanism (fluid momentum)
  into a selective bidirectional interaction without preparing the target.

## Source provenance for formulas

- Atmospheric acoustics: ISO 9613-1 for absorption; nonlinear model derivation
  and caveats are in docs/PHYSICS.md.
- Round turbulent jet correlations: Perry's Chemical Engineers' Handbook,
  Fluid and Particle Dynamics, turbulent free-jet characteristics; the commonly
  reported round-jet potential core is about 6.2 nozzle diameters and developed
  centerline velocity decays approximately as 1/x.
- Dielectrophoresis: standard induced-dipole result for a spherical particle,
  F_DEP = 2 pi epsilon_medium a^3 Re(K) grad(E^2).
- Magnetic susceptibility force: standard weak-linear-material result,
  F = chi V grad(B^2)/(2 mu0).
- Photon radiation pressure: passive-target momentum flux, F <= 2P/c.
