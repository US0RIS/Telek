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

`telek.acoustics` implements only this ideal momentum-flux layer, so the engineering models below cannot accidentally obscure the fundamental floor.

## Engineering link budget (`telek.linkbudget`)

Classification: **optimistic engineering estimate**. Chain, each factor explicit:

`F = (1+|R|^2) cos(theta) * min( eta_ea P_elec (capped by P_ac,max) * T_abs(L) * eta_cap , P_sat )  / c`

| factor | model | class |
|---|---|---|
| `eta_ea`, `P_elec`, `P_ac,max` | user inputs | engineering assumption |
| `T_abs(L) = 10^(-alpha L/10)` | ISO 9613-1 (`alpha` ~ 1.32 dB/m at 40 kHz, 20 C, 50 % RH) | engineering estimate |
| `eta_cap` | encircled energy of a paraxial focal Airy pattern, `1 - J0(x)^2 - J1(x)^2`, `x = pi D d / (2 lambda L)` | physical model (ideal aperture) |
| `1+|R|^2` | normal-incidence passive target that lets nothing exit its back face; `~2` for any solid or liquid in air | physical bound |
| `P_sat` | shock-saturation supremum (below) | weak-shock model ceiling |

Not modeled (all make real devices worse or less predictable): grating lobes,
phase quantization, element directivity, standing waves between wearer and
target, trap stability, nonuniform apodization, nonlinear self-defocusing.

## Shock saturation: a source-power-independent ceiling (`telek.nonlinear`)

Classification: **model ceiling under the stated weak-shock/ray assumptions**.
This result is important because it is source-power independent inside that
model, but it is not a universal theorem for every nonlinear acoustic field.

Air is a nonlinear acoustic medium (`beta = 1 + B/2A = 1.2`). A finite-amplitude
plane wave steepens into a shock after `x_bar = rho c^3 / (beta omega p0)`, after
which energy is dissipated at the shock. In lossless weak-shock theory, an
initially sinusoidal wave at normalized distance `sigma = x/x_bar > 1` has

`<p^2>/p0^2 = [pi - phi_s + sin(2 phi_s)/2 + (2/3) sigma sin^3(phi_s)] / (2 pi)`,  `phi_s = sigma sin(phi_s)`

(derived by integrating `p0^2 sin^2(phi) d(theta)` over the shock-trimmed
Earnshaw/Fubini waveform `theta = phi - sigma sin phi`; it reduces to `1/2` at
`sigma = 1` and to the sawtooth value `(pi/(1+sigma))^2/3` as `sigma -> inf`).
Raising the source amplitude at fixed `x` raises `sigma`; the resulting
intensity increases monotonically to (and never reaches) the supremum

`I_sup(x) = pi^2 rho c^5 / (3 beta^2 omega^2 x^2)`

which is **independent of source power within the weak-shock model**. At 20 C: 207 W/m^2 at 1 m and 40 kHz
(`2 I/c` = 1.2 Pa radiation pressure on a perfect reflector); it scales as
`1/(f^2 x^2)`.

Extension to beams. For a spherical ray tube converging from aperture radius
of curvature `R0` toward a focus, the waveform evolves as a plane wave over
`x_eff = R0 ln(R0/r) >= L` (path length), while the tube area shrinks as the
amplitude grows; tube power is therefore `<= I_sup(L) * A_ap`. For a diverging
tube, the target intercepts at most `I_sup(L) * A_t` because
`u <= (1+u) ln(1+u)`. Collimated beams are the limiting case. Hence

`P_delivered <= I_sup(L) * max(A_aperture, A_target)`.

Assumptions/loopholes, stated so they can be attacked:

1. Weak-shock theory without diffraction-nonlinearity coupling (no KZK). Real
   focused beams can differ quantitatively; general non-spherical beams are not
   rigorously covered.
2. Absorption is ignored, which only lowers delivered power.
3. Momentum lost at shocks is not destroyed: it drives **acoustic streaming**
   (wind). That is real momentum transfer but it is airflow, not radiation
   pressure; it is bounded by total radiated `P_ac/c` and has airflow's poor
   selectivity. It must be evaluated under the airflow mechanism.
4. Lower frequency raises the ceiling as `1/f^2` but approaches audibility
   (discreet-intent conflict, hearing safety) and worsens diffraction
   (aperture `D ~ lambda L / d`).

### Consequence for the milestones (`telek gap`)

With a 0.30 m diameter wearable aperture (0.071 m^2) and 0.10 m target,
`telek gap` gives (margin = force supremum / required force):

| milestone | case | 20 kHz | 25 kHz | 40 kHz | area needed at 40 kHz |
|---|---|---|---|---|---|
| M2 (10 g, 0.25 m) | lift | 56x | 36x | 14x | 0.005 m^2 |
| M3 (100 g, 1 m) | slide, mu = 0.3 | 1.16x | 0.74x | 0.29x | 0.24 m^2 |
| M3 (100 g, 1 m) | lift | 0.35x | 0.22x | 0.087x | 0.81 m^2 |
| M4 (500 g, 3 m) | lift | 0.0078x | 0.0050x | 0.0019x | 36.5 m^2 |

Interpretation:

- **The current weak-shock model puts M4 2-3 orders of magnitude short** for a
  wearable aperture, independent of transducer power or efficiency inside the
  model. Treat this as strong negative evidence, not a universal impossibility
  proof, until the diffraction/nonlinearity loopholes are tested quantitatively.
- **M3** is marginal: only sliding (not lifting), only near the audible limit
  or with a larger-than-wearable aperture.
- **M2** is not limited by saturation; it is limited by source power,
  efficiency, and diffraction, so engineering and measurement decide it.

These numbers are model ceilings, not device predictions. Ordinary engineering
losses push downward, while a failure of the model assumptions could move the
ceiling. That distinction is why KZK/full-field and experimental validation are
explicit next steps.

## Why phased arrays remain interesting

A phased aperture can alter wavefront geometry without mechanically steering the source. In principle this enables electronic movement of focal regions, vortices, and other pressure structures. That maps naturally to Telek's need for a spatially programmable force field.

The open question is **force density at useful standoff from a portable aperture**, not whether small-object acoustic manipulation exists.

## Cross-mechanism comparison

The first quantitative screen of airflow, photon pressure, electrostatics and
magnetics is now in `docs/MECHANISMS.md` and `telek.mechanisms`. Its main result
is that directed airflow is by far the strongest known portable interaction in
raw force at meter scale, but it is push-only and conspicuous; the field-based
alternatives collapse with range or target material. None currently supplies
the bidirectional, selective M4 behavior.

The notes below remain as qualitative context.

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
