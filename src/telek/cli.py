from __future__ import annotations

import argparse

from .acoustics import (
    DEFAULT_SOUND_SPEED_M_S,
    ideal_force_from_incident_power,
    ideal_incident_power_to_hold_mass,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="telek",
        description="Telek feasibility calculator (ideal acoustic bounds only)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    force = sub.add_parser("force", help="ideal force from incident acoustic power")
    force.add_argument("--power", type=float, required=True, help="incident acoustic power in W")
    force.add_argument("--c", type=float, default=DEFAULT_SOUND_SPEED_M_S, help="sound speed in m/s")
    force.add_argument(
        "--multiplier",
        type=float,
        default=2.0,
        help="momentum multiplier: 1 absorption, 2 ideal reflection",
    )

    hold = sub.add_parser("hold", help="ideal incident power floor to support a mass")
    hold.add_argument("--mass", type=float, required=True, help="target mass in kg")
    hold.add_argument("--accel", type=float, default=0.0, help="additional upward acceleration in m/s^2")
    hold.add_argument("--c", type=float, default=DEFAULT_SOUND_SPEED_M_S, help="sound speed in m/s")
    hold.add_argument("--multiplier", type=float, default=2.0)
    return parser


def main() -> None:
    args = _parser().parse_args()
    if args.command == "force":
        value = ideal_force_from_incident_power(
            args.power,
            sound_speed_m_s=args.c,
            momentum_multiplier=args.multiplier,
        )
        print(f"ideal axial force: {value:.6g} N")
        print("WARNING: ideal momentum-flux bound; not a realizable-device prediction")
        return

    value = ideal_incident_power_to_hold_mass(
        args.mass,
        upward_accel_m_s2=args.accel,
        sound_speed_m_s=args.c,
        momentum_multiplier=args.multiplier,
    )
    print(f"ideal incident acoustic power floor: {value:.6g} W")
    print("WARNING: excludes conversion, propagation, focusing, coupling, thermal and safety losses")


if __name__ == "__main__":
    main()
