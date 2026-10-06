# Physics notes: remote force candidates

This document records the current physical model. It is deliberately conservative about what is demonstrated versus merely allowed by physics.

## Acoustic radiation force

A propagating acoustic wave carries momentum. For incident acoustic power `P` on a target, the axial force has an ideal upper-bound scale

`F <= 2 P / c`

for perfect reflection of a normally incident beam, where `c` is the speed of sound. Perfect absorption gives the lower momentum-transfer scale `F = P / c` for the same incident power.

This is a **momentum-flux bound**, not a transducer specification. `P` here means acoustic power that actually reaches/interacts with the target. Electrical input power must be higher, often much higher.

At `c = 343 m/s`, the ideal reflected-beam lower bound on incident acoustic power required to produce 1 N is:

`P >= F c / 2 = 171.5 W`

Merely countering gravity for a mass `m` requires `F = m g`, so a 0.5 kg target needs 4.903 N upward and therefore at least about 841 W of *incident acoustic power* under the same extremely favorable assumptions.

Real systems must additionally contend with:

- electro-acoustic conversion efficiency;
- finite aperture and diffraction;
- field synthesis/focusing efficiency;
- atmospheric absorption;
- target size and geometry;
- reflection/transmission/absorption at the target;
- force components not aligned with the desired vector;
- heating and allowable exposure;
- nonlinear propagation at high sound pressure;
- stability of the acoustic trap/field;
- reaction forces on the wearable platform.

The code currently implements only the ideal momentum-flux layer so later engineering models cannot accidentally obscure the fundamental floor.

## Why phased arrays remain interesting

A phased aperture can alter wavefront geometry without mechanically steering the source. In principle this enables electronic movement of focal regions, vortices, and other pressure structures. That maps naturally to Telek's need for a spatially programmable force field.

The open question is **force density at useful standoff from a portable aperture**, not whether small-object acoustic manipulation exists.

## Other candidates to compare

### Directed airflow
Pros: strong momentum coupling to arbitrary surfaces; mature components.
Cons: visually/audibly obvious, divergent, poor selectivity, strong disturbance of surrounding material. May still be competitive for very light targets and should be modeled quantitatively rather than dismissed.

### Magnetics
Pros: high force and mature field control.
Cons: target-material dependence violates the arbitrary-unmodified-target goal for many objects; gradients decay rapidly with distance. Useful benchmark but unlikely universal mechanism.

### Electrostatics
Pros: contactless force; potentially compact high-voltage generation.
Cons: target charge/polarizability, breakdown, humidity, range and safety constraints. Requires quantitative evaluation.

### Optical radiation pressure
Pros: exceptional steerability and range in principle.
Cons: `F ~ P/c_light`, making macroscopic force energetically extreme; likely useful mainly as a lower-priority bound/contrast.

## Research discipline

For every proposed actuator, calculate at minimum:

1. target force required (`m(g+a)` when lifting/accelerating vertically);
2. fundamental momentum/field-energy floor;
3. coupling coefficient to an unmodified target;
4. propagation/range loss;
5. emitter aperture/geometry requirement;
6. electrical power and thermal budget;
7. reaction force and wearable ergonomics;
8. expected off-target field/exposure;
9. whether the setup still satisfies `CRITERIA.md`.
