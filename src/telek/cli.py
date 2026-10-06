from __future__ import annotations

import argparse
from math import pi

from .acoustics import (
    DEFAULT_SOUND_SPEED_M_S,
    ideal_force_from_incident_power,
    ideal_incident_power_to_hold_mass,
)
from .atmosphere import Air
from .gap import milestone_gap
from .linkbudget import LinkScenario, evaluate_link, required_force_to_lift
from .mechanisms import (
    electrostatic_induced_force_sphere,
    magnetic_susceptibility_force_sphere,
    optical_power_for_force,
    optical_radiation_force,
    round_jet_exit_velocity_for_force,
    round_jet_force_on_centered_disk,
    round_jet_kinetic_power,
    round_jet_kinetic_power_for_force,
)
from .nonlinear import radiation_force_supremum, saturated_intensity_supremum


def _air_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--temp-c", type=float, default=20.0, help="air temperature in C")
    p.add_argument("--rh", type=float, default=50.0, help="relative humidity in %%")


def _air(args: argparse.Namespace) -> Air:
    return Air(temperature_k=args.temp_c + 273.15, relative_humidity_pct=args.rh)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="telek",
        description="Telek feasibility calculator. Every output states its evidence class.",
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

    sat = sub.add_parser("saturation", help="shock-saturation bound on radiation force at range")
    sat.add_argument("--freq", type=float, required=True, help="frequency in Hz")
    sat.add_argument("--range", type=float, required=True, help="path length in m")
    sat.add_argument("--aperture-area", type=float, required=True, help="emitting aperture area in m^2")
    sat.add_argument("--target-area", type=float, required=True, help="target projected area in m^2")
    _air_args(sat)

    link = sub.add_parser("link", help="engineering link budget (all assumptions explicit)")
    link.add_argument("--freq", type=float, required=True, help="frequency in Hz")
    link.add_argument("--range", type=float, required=True, help="range in m")
    link.add_argument("--aperture-diameter", type=float, required=True, help="m")
    link.add_argument("--target-diameter", type=float, required=True, help="m")
    link.add_argument("--electrical-power", type=float, required=True, help="W")
    link.add_argument("--efficiency", type=float, required=True, help="electro-acoustic efficiency (0,1]")
    link.add_argument("--max-acoustic-power", type=float, required=True, help="transducer/thermal cap in W")
    link.add_argument("--multiplier", type=float, default=2.0, help="target momentum multiplier 1+R^2")
    link.add_argument("--mass", type=float, default=None, help="optional target mass for lift margin, kg")
    _air_args(link)

    screen = sub.add_parser("screen", help="compare reference remote-force mechanisms")
    screen.add_argument("--mass", type=float, default=0.5, help="benchmark target mass in kg")
    screen.add_argument("--range", type=float, default=3.0, help="target range / center distance in m")
    screen.add_argument("--target-diameter", type=float, default=0.1, help="target diameter in m")
    screen.add_argument("--emitter-diameter", type=float, default=0.3, help="wearable field/acoustic aperture diameter in m")
    screen.add_argument("--acoustic-freq", type=float, default=40e3, help="acoustic comparison frequency in Hz")
    screen.add_argument("--jet-nozzle-diameter", type=float, default=0.05, help="round-air-jet nozzle diameter in m")
    screen.add_argument("--jet-velocity", type=float, default=100.0, help="reference jet exit velocity in m/s")
    screen.add_argument("--optical-power", type=float, default=1000.0, help="reference optical beam power in W")
    screen.add_argument("--electrostatic-surface-field", type=float, default=3e6, help="idealized emitter surface E field in V/m")
    screen.add_argument("--magnetic-surface-field", type=float, default=2.0, help="idealized emitter surface B field in T")
    screen.add_argument("--susceptibility", type=float, default=1e-5, help="target volume magnetic susceptibility magnitude")
    _air_args(screen)

    gap = sub.add_parser("gap", help="CRITERIA.md milestones vs shock-saturation model ceiling")
    gap.add_argument("--aperture-diameter", type=float, default=0.3, help="wearable aperture diameter, m")
    gap.add_argument("--target-diameter", type=float, default=0.1, help="target diameter, m")
    gap.add_argument("--mu", type=float, default=0.3, help="static friction coefficient for slide cases")
    _air_args(gap)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = _parser().parse_args(argv)
    if args.command == "force":
        value = ideal_force_from_incident_power(
            args.power,
            sound_speed_m_s=args.c,
            momentum_multiplier=args.multiplier,
        )
        print(f"ideal axial force: {value:.6g} N")
        print("WARNING: ideal momentum-flux bound; not a realizable-device prediction")
        return

    if args.command == "hold":
        value = ideal_incident_power_to_hold_mass(
            args.mass,
            upward_accel_m_s2=args.accel,
            sound_speed_m_s=args.c,
            momentum_multiplier=args.multiplier,
        )
        print(f"ideal incident acoustic power floor: {value:.6g} W")
        print("WARNING: excludes conversion, propagation, focusing, coupling, thermal and safety losses")
        return

    air = _air(args)
    if args.command == "screen":
        required = required_force_to_lift(args.mass)
        aperture_area = pi * args.emitter_diameter**2 / 4.0
        target_area = pi * args.target_diameter**2 / 4.0
        acoustic = radiation_force_supremum(
            args.acoustic_freq,
            args.range,
            aperture_area,
            target_area,
            air=air,
        )
        jet = round_jet_force_on_centered_disk(
            args.jet_nozzle_diameter,
            args.jet_velocity,
            args.target_diameter,
            args.range,
            air_density_kg_m3=air.density_kg_m3,
        )
        jet_power = round_jet_kinetic_power(
            args.jet_nozzle_diameter,
            args.jet_velocity,
            air_density_kg_m3=air.density_kg_m3,
        )
        jet_need_v = round_jet_exit_velocity_for_force(
            required,
            args.jet_nozzle_diameter,
            args.target_diameter,
            args.range,
            air_density_kg_m3=air.density_kg_m3,
        )
        jet_need_p = round_jet_kinetic_power_for_force(
            required,
            args.jet_nozzle_diameter,
            args.target_diameter,
            args.range,
            air_density_kg_m3=air.density_kg_m3,
        )
        optical = optical_radiation_force(args.optical_power)
        optical_need = optical_power_for_force(required)
        electrostatic = electrostatic_induced_force_sphere(
            args.emitter_diameter / 2.0,
            args.target_diameter / 2.0,
            args.range,
            args.electrostatic_surface_field,
        )
        magnetic = magnetic_susceptibility_force_sphere(
            args.emitter_diameter / 2.0,
            args.target_diameter / 2.0,
            args.range,
            args.magnetic_surface_field,
            args.susceptibility,
        )
        rows = (
            ("acoustic weak-shock", acoustic, "structured*", "broad"),
            ("round air jet", jet, "push", "broad"),
            ("optical radiation", optical, "push", "broad surface"),
            ("electrostatic DEP", electrostatic, "pull", "polarizable"),
            ("magnetic susceptibility", magnetic, "material-dependent", "weak dia/paramagnetic"),
        )
        print(
            f"benchmark: {args.mass:g} kg target, {args.range:g} m range, "
            f"{args.target_diameter:g} m target diameter; weight = {required:.6g} N"
        )
        print(f"{'mechanism':<25}{'force N':>12}{'margin':>12}  {'direction':<18}{'target scope'}")
        for name, force_n, direction, scope in rows:
            print(f"{name:<25}{force_n:>12.5g}{force_n / required:>12.3g}  {direction:<18}{scope}")
        print(
            f"air jet reference: {args.jet_nozzle_diameter:g} m nozzle @ {args.jet_velocity:g} m/s "
            f"contains {jet_power / 1000:.3g} kW ideal kinetic power"
        )
        print(
            f"air jet to equal benchmark force in this centered-target model: "
            f"{jet_need_v:.1f} m/s, {jet_need_p / 1000:.3g} kW ideal kinetic power"
        )
        print(f"optical power to equal benchmark force at perfect reflection: {optical_need / 1e6:.3g} MW")
        print("CLASS: screening comparison. Models are not equally rigorous or equally realizable.")
        print("NOTE: airflow is push-only and conspicuous; field estimates use optimistic idealized target/source geometry.")
        print("NOTE: acoustic value is a weak-shock model ceiling, not a universal theorem for every nonlinear beam geometry.")
        return

    if args.command == "saturation":
        intensity = saturated_intensity_supremum(args.freq, args.range, air)
        force = radiation_force_supremum(args.freq, args.range, args.aperture_area, args.target_area, air=air)
        print(f"saturated intensity supremum at {args.range:g} m: {intensity:.6g} W/m^2")
        print(f"radiation force supremum: {force:.6g} N")
        print("CLASS: weak-shock model ceiling under stated spherical/collimated-ray assumptions")
        print("NOTE: excludes streaming/wind momentum, which belongs to the airflow mechanism model")
        return

    if args.command == "link":
        s = LinkScenario(
            frequency_hz=args.freq,
            range_m=args.range,
            aperture_diameter_m=args.aperture_diameter,
            target_diameter_m=args.target_diameter,
            electrical_power_w=args.electrical_power,
            electroacoustic_efficiency=args.efficiency,
            max_acoustic_power_w=args.max_acoustic_power,
            momentum_multiplier=args.multiplier,
            air=air,
        )
        b = evaluate_link(s)
        print(f"acoustic power radiated:     {b.acoustic_power_w:.4g} W   (assumption-driven)")
        print(f"absorption transmission:     {b.absorption_transmission:.4g}     (ISO 9613-1 estimate)")
        print(f"diffraction capture:         {b.capture_fraction:.4g}     (paraxial Airy model)")
        print(f"linear delivered power:      {b.linear_delivered_power_w:.4g} W")
        print(f"shock-saturation power cap:  {b.nonlinear_power_cap_w:.4g} W   (weak-shock model ceiling)")
        print(f"force on target:             {b.force_n:.4g} N")
        print(f"limiting factor:             {b.limiting_factor}")
        if args.mass is not None:
            need = required_force_to_lift(args.mass)
            print(f"lift margin for {args.mass:g} kg:     {b.margin(need):.3g}x")
        print("CLASS: optimistic engineering estimate; not a device specification")
        return

    a_ap = pi * args.aperture_diameter**2 / 4.0
    a_t = pi * args.target_diameter**2 / 4.0
    print(
        f"aperture {args.aperture_diameter:g} m dia ({a_ap:.4g} m^2), target {args.target_diameter:g} m dia, "
        f"{args.temp_c:g} C, {args.rh:g}% RH"
    )
    print(f"{'ms':<4}{'mode':<14}{'f kHz':>7}{'need N':>10}{'sup N':>11}{'margin':>10}{'area needed m^2':>17}")
    for r in milestone_gap(aperture_area_m2=a_ap, target_area_m2=a_t, friction_coefficient=args.mu, air=air):
        print(
            f"{r.milestone:<4}{r.mode:<14}{r.frequency_hz / 1e3:>7.0f}{r.required_force_n:>10.4g}"
            f"{r.force_supremum_n:>11.4g}{r.margin:>10.3g}{r.required_area_m2:>17.4g}"
        )
    print("CLASS: weak-shock model ceiling. margin < 1 => this model does not permit the milestone.")
    print("NOTE: 20 kHz is at the edge of human hearing; it conflicts with discreet operation.")


if __name__ == "__main__":
    main()
