# Telek project criteria

This file is authoritative. A feature, experiment, or proposed technology is relevant only to the extent that it advances these criteria.

## 1. End state

A person wearing a portable system can use deliberate, discreet hand gestures to cause a selected ordinary physical object to translate, lift, hold, pull, push, or rotate at a distance in a previously unprepared environment.

The experience should converge on the useful physical semantics of fictional telekinesis rather than on generic gesture-controlled automation.

## 2. What counts

A candidate approach is **considerable** only if its useful effect travels with the wearer. It must not depend on prior installation at the location.

A strong solution should satisfy all of the following:

1. **Portable:** the enabling equipment is carried or worn by the user (or is a generally available commodity carried with the user), not installed around the room.
2. **Unprepared environment:** it works in a place the system has not previously instrumented.
3. **Unmodified target:** the object does not need a tag, magnet, reflector, tether, embedded motor, special coating, or paired electronics.
4. **Real mechanical effect:** the target actually moves because force/torque is applied to it. AR-only effects and UI control do not satisfy the core goal.
5. **Remote:** useful operation occurs without touching the target.
6. **Directional:** the system can intentionally choose the direction of force, rather than merely disturbing the object.
7. **Target-selective:** the chosen object can be acted on without indiscriminately affecting the surrounding scene.
8. **Discreet intent:** commands can originate from low-motion hand/finger intent, ideally wrist EMG or an equivalent wearable neural/muscular interface.
9. **Closed-loop:** object motion is sensed and corrected rather than fired open-loop.
10. **Safe enough to test:** experimental work must use bounded energy/force and explicit interlocks. Safety limits are part of the architecture, not an afterthought.

## 3. What does not count as the core result

These can be useful supporting technologies but do not themselves satisfy Telek:

- smart-home control;
- pre-motorized doors, blinds, drawers, or furniture;
- hidden cables, rails, ceiling robots, or room-mounted emitters;
- drones visibly carrying the target;
- magnets or markers attached to the target;
- a special test chamber that supplies the actuation infrastructure;
- AR/VR objects that only appear to move;
- calling an unspecified future invention a "tractor beam" without identifying a physical coupling mechanism.

A benchtop setup may still be used to validate a portable mechanism. The distinction is that the *mechanism being validated* must have a credible path to traveling with the wearer rather than requiring the bench/environment to become the final product.

## 4. Force vocabulary

The interface should ultimately expose physical verbs rather than per-device commands:

- **select** — designate the target;
- **push / pull** — accelerate target along a chosen vector;
- **lift / lower** — control vertical force;
- **hold** — maintain target pose against gravity/disturbance;
- **translate** — move through a commanded 3-D trajectory;
- **rotate** — apply torque about a commanded axis;
- **release** — remove commanded force safely.

The actuator may change over time. These semantics should not.

## 5. Quantitative milestones

These are research milestones, not claims about current capability.

### M0 — model integrity
- Unit-tested physics utilities.
- Every result labels ideal bounds vs. empirical/engineering assumptions.
- No hidden fudge factors.

### M1 — measurable contactless influence
- Unmodified target.
- Portable-side actuator concept.
- Repeatable displacement distinguishable from airflow/vibration/artifact.
- Closed-loop measurement.

### M2 — deliberate 1-D control
- At least 10 g target.
- At least 0.25 m standoff.
- Bidirectional commanded motion along one axis.
- <= 250 ms command-to-controller latency (excluding slow object dynamics).

### M3 — useful tabletop telekinesis
- At least 100 g target.
- At least 1 m standoff.
- 2-D controlled translation on/near a surface or suspension condition.
- Reliable target selection among multiple objects.

### M4 — Force-like free-space manipulation
- At least 500 g target.
- At least 3 m standoff.
- Counter gravity plus commanded acceleration.
- 3-D translation and meaningful rotation.
- No target or environment preparation.

M4 is intentionally far beyond demonstrated portable airborne-ultrasound capability as of project inception. The repository must quantify the gap rather than quietly relaxing the goal.

## 6. Current technology thesis

The first mechanism to investigate is **airborne phased ultrasound** because acoustic radiation pressure provides genuine remote momentum transfer to a broad class of ordinary materials, and phased arrays provide electronic steering and field shaping.

This is a hypothesis, not a commitment. Telek should replace ultrasound if another physical mechanism scores better against the criteria.

The key question is not "can ultrasound levitate something?" It is:

> Can a portable emitter create enough controllable force density at useful range, with acceptable efficiency and safety, to manipulate macroscopic unmodified objects?

## 7. Evidence standard

Keep three categories separate in code and documentation:

- **Physical bound:** follows from equations and stated assumptions.
- **Published result:** measured by an external source; include provenance.
- **Telek result:** measured in our own experiment; include raw data and procedure.

Never present an ideal upper bound as an achievable device specification.

## 8. Contributor rule

Before doing substantial work, read this file and `HANDOFF.md`. If an attractive idea violates section 2, either reject it or label it explicitly as a supporting/non-core capability.
