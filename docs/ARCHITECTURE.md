# Architecture

Telek separates **intent**, **targeting**, **force semantics**, **actuation**, and **measurement** so that progress in one layer does not bake in assumptions about another.

```text
EMG / gesture sensor
        |
        v
Intent decoder  --->  arm/deadman policy
        |
        v
Target selector <--- vision / ranging / tracking
        |
        v
Force command (target, F, torque, duration/hold)
        |
        v
Safety envelope / saturator
        |
        +------> simulator (default)
        |
        `------> actuator backend (future, explicitly armed)
                        |
                        v
                    physical target
                        |
                        v
                pose/velocity feedback
                        `-----------> controller
```

## Core types

`ForceCommand`
: Hardware-neutral command describing desired force and torque on a selected target. It is intentionally not a raw transducer command.

`GestureEvent`
: Output of an EMG/gesture recognizer. It carries semantic intent and confidence, not electrode samples.

`ActuatorCapability`
: Declares force/power/range limits so controllers can reject impossible commands rather than silently clipping them.

## Design rules

1. Simulation is the default backend.
2. The physics layer exposes assumptions explicitly.
3. High-level intent never directly specifies transducer voltages/phases.
4. Any future hardware adapter must sit behind a safety/saturation boundary.
5. Target tracking and actuation remain separate; a better camera must not change force semantics.
6. The same `ForceCommand` vocabulary should work with any future coupling mechanism.

## Near-term software roadmap

### Phase A — physical feasibility
- Ideal momentum-transfer bounds. (`telek.acoustics`, done)
- Engineering loss model. (`telek.linkbudget`, `telek.atmosphere`, first version done)
- Range/aperture model. (paraxial diffraction capture + shock-saturation bound in `telek.nonlinear`, done)
- Milestone gap report. (`telek.gap`, `telek gap`, done)
- Competing-mechanism comparison. (next)

### Phase B — closed-loop digital twin
- Rigid target state.
- Gravity, drag, surface contact.
- Actuator saturation.
- Pose-sensor latency/noise.
- Controller stability and trajectory tracking.

### Phase C — intent
- Synthetic gesture source first.
- Recorded EMG dataset adapter.
- Real-time recognizer adapter.
- Intent confirmation/deadman behavior.

### Phase D — hardware research adapters
Only after the model identifies a credible bounded experiment. Hardware interfaces should implement a narrow capability contract and independent interlocks.
