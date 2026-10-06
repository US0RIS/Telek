"""Cross-mechanism screening models for portable remote-force concepts.

This module compares actual physical coupling mechanisms before Telek commits
to hardware. The functions are intentionally simple and auditable. They are
not device designs, and most are optimistic screening estimates.

Evidence classes used here:
- photon momentum: physical momentum-flux bound;
- round free jet: engineering estimate using turbulent-jet correlations;
- electrostatics: idealized induced-dipole estimate for a spherical target;
- magnetics: idealized linear-susceptibility/dipole-source estimate.

A mechanism can produce a large number here and still fail CRITERIA.md because
of directionality, target-material dependence, noise, collateral disturbance,
portability, or safety.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, log, pi, sqrt

SPEED_OF_LIGHT_M_S = 299_792_458.0
VACUUM_PERMITTIVITY_F_M = 8.854_187_8128e-12
VACUUM_PERMEABILITY_H_M = 1.256_637_062_12e-6
DEFAULT_AIR_DENSITY_KG_M3 = 1.204


def _nonnegative(name: str, value: float) -> float:
    if value < 0:
        raise ValueError(f"{name} must be >= 0")
    return float(value)


def _positive(name: str, value: float) -> float:
    if value <= 0:
        raise ValueError(f"{name} must be > 0")
    return float(value)


def _fraction(name: str, value: float) -> float:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be in [0, 1]")
    return float(value)


@dataclass(frozen=True, slots=True)
class MechanismEstimate:
    """One comparable force estimate with the caveats needed to interpret it."""

    mechanism: str
    force_n: float
    directionality: str
    target_scope: str
    evidence_class: str
    source_power_w: float | None = None
    note: str = ""

    def margin(self, required_force_n: float) -> float:
        required = _positive("required_force_n", required_force_n)
        return self.force_n / required


def optical_radiation_force(
    optical_power_w: float,
    *,
    momentum_multiplier: float = 2.0,
) -> float:
    """Ideal axial photon-radiation force.

    momentum_multiplier=1 is perfect absorption and 2 is perfect normal
    reflection. This is a physical momentum-flux bound for a passive target.
    """

    power = _nonnegative("optical_power_w", optical_power_w)
    if not 0.0 <= momentum_multiplier <= 2.0:
        raise ValueError("momentum_multiplier must be in [0, 2]")
    return momentum_multiplier * power / SPEED_OF_LIGHT_M_S


def optical_power_for_force(
    force_n: float,
    *,
    momentum_multiplier: float = 2.0,
) -> float:
    """Ideal optical power required for an axial radiation force."""

    force = _nonnegative("force_n", force_n)
    if not 0.0 < momentum_multiplier <= 2.0:
        raise ValueError("momentum_multiplier must be in (0, 2]")
    return force * SPEED_OF_LIGHT_M_S / momentum_multiplier


def round_jet_nozzle_area(nozzle_diameter_m: float) -> float:
    d = _positive("nozzle_diameter_m", nozzle_diameter_m)
    return pi * d * d / 4.0


def round_jet_thrust(
    nozzle_diameter_m: float,
    exit_velocity_m_s: float,
    *,
    air_density_kg_m3: float = DEFAULT_AIR_DENSITY_KG_M3,
) -> float:
    """Exit momentum flux rho A v^2 of an ambient-pressure round air jet."""

    area = round_jet_nozzle_area(nozzle_diameter_m)
    velocity = _nonnegative("exit_velocity_m_s", exit_velocity_m_s)
    rho = _positive("air_density_kg_m3", air_density_kg_m3)
    return rho * area * velocity * velocity


def round_jet_kinetic_power(
    nozzle_diameter_m: float,
    exit_velocity_m_s: float,
    *,
    air_density_kg_m3: float = DEFAULT_AIR_DENSITY_KG_M3,
) -> float:
    """Kinetic power 0.5 rho A v^3 in an ambient-pressure round air jet."""

    area = round_jet_nozzle_area(nozzle_diameter_m)
    velocity = _nonnegative("exit_velocity_m_s", exit_velocity_m_s)
    rho = _positive("air_density_kg_m3", air_density_kg_m3)
    return 0.5 * rho * area * velocity**3


def round_jet_capture_fraction(
    nozzle_diameter_m: float,
    target_diameter_m: float,
    range_m: float,
) -> float:
    """Centered-disk fraction of round-jet axial momentum.

    For x/D <= 6.2, the approximate potential-core length for a turbulent
    round jet, this uses the optimistic geometric fraction of nozzle area
    intercepted by the target, capped at one.

    Beyond the potential core it integrates the common self-similar profile
    log10(Uc/U(r)) = 40 (r/x)^2. Since momentum density scales as U^2, the
    centered momentum fraction inside target radius a becomes
    1 - exp[-80 ln(10) (a/x)^2].

    This assumes perfect centering and ignores crosswind, body blockage,
    source inefficiency, and unsteady impingement.
    """

    d = _positive("nozzle_diameter_m", nozzle_diameter_m)
    target_d = _positive("target_diameter_m", target_diameter_m)
    x = _positive("range_m", range_m)
    if x / d <= 6.2:
        return min(1.0, (target_d / d) ** 2)
    radius = target_d / 2.0
    exponent = -80.0 * log(10.0) * (radius / x) ** 2
    return 1.0 - exp(exponent)


def round_jet_force_on_centered_disk(
    nozzle_diameter_m: float,
    exit_velocity_m_s: float,
    target_diameter_m: float,
    range_m: float,
    *,
    momentum_coupling: float = 1.0,
    air_density_kg_m3: float = DEFAULT_AIR_DENSITY_KG_M3,
) -> float:
    """Estimated push force on a centered disk intercepting a turbulent air jet."""

    coupling = _fraction("momentum_coupling", momentum_coupling)
    thrust = round_jet_thrust(
        nozzle_diameter_m,
        exit_velocity_m_s,
        air_density_kg_m3=air_density_kg_m3,
    )
    capture = round_jet_capture_fraction(nozzle_diameter_m, target_diameter_m, range_m)
    return thrust * capture * coupling


def round_jet_exit_velocity_for_force(
    required_force_n: float,
    nozzle_diameter_m: float,
    target_diameter_m: float,
    range_m: float,
    *,
    momentum_coupling: float = 1.0,
    air_density_kg_m3: float = DEFAULT_AIR_DENSITY_KG_M3,
) -> float:
    """Exit velocity required by the round-jet estimate for a target force."""

    force = _nonnegative("required_force_n", required_force_n)
    coupling = _fraction("momentum_coupling", momentum_coupling)
    if coupling == 0.0:
        if force == 0.0:
            return 0.0
        raise ValueError("momentum_coupling must be > 0 when required_force_n > 0")
    rho = _positive("air_density_kg_m3", air_density_kg_m3)
    area = round_jet_nozzle_area(nozzle_diameter_m)
    capture = round_jet_capture_fraction(nozzle_diameter_m, target_diameter_m, range_m)
    if force == 0.0:
        return 0.0
    return sqrt(force / (rho * area * capture * coupling))


def round_jet_kinetic_power_for_force(
    required_force_n: float,
    nozzle_diameter_m: float,
    target_diameter_m: float,
    range_m: float,
    *,
    momentum_coupling: float = 1.0,
    air_density_kg_m3: float = DEFAULT_AIR_DENSITY_KG_M3,
) -> float:
    """Ideal jet kinetic power corresponding to the required exit velocity."""

    velocity = round_jet_exit_velocity_for_force(
        required_force_n,
        nozzle_diameter_m,
        target_diameter_m,
        range_m,
        momentum_coupling=momentum_coupling,
        air_density_kg_m3=air_density_kg_m3,
    )
    return round_jet_kinetic_power(
        nozzle_diameter_m,
        velocity,
        air_density_kg_m3=air_density_kg_m3,
    )


def electrostatic_induced_force_sphere(
    emitter_radius_m: float,
    target_radius_m: float,
    center_distance_m: float,
    emitter_surface_field_v_m: float,
    *,
    polarizability_factor: float = 1.0,
) -> float:
    """Optimistic pull force on a neutral polarizable sphere in air.

    Model:
    - emitter is an isolated charged conducting sphere of radius R;
    - its surface field is E0 and therefore E(r)=E0(R/r)^2;
    - target is small relative to range and has polarizability factor K in
      [0, 1], with K=1 the conducting-sphere limit;
    - dielectrophoretic force is F = 2 pi eps0 a^3 K grad(E^2).

    For the spherical emitter, |grad(E^2)| = 4 E^2/r, so force decays as r^-5.
    This is a screening estimate, not a breakdown/corona or exposure model.
    """

    source_r = _positive("emitter_radius_m", emitter_radius_m)
    target_r = _positive("target_radius_m", target_radius_m)
    distance = _positive("center_distance_m", center_distance_m)
    field0 = _nonnegative("emitter_surface_field_v_m", emitter_surface_field_v_m)
    k = _fraction("polarizability_factor", polarizability_factor)
    if distance <= source_r + target_r:
        raise ValueError("center_distance_m must exceed emitter_radius_m + target_radius_m")
    field = field0 * (source_r / distance) ** 2
    grad_e2 = 4.0 * field * field / distance
    return 2.0 * pi * VACUUM_PERMITTIVITY_F_M * target_r**3 * k * grad_e2


def magnetic_susceptibility_force_sphere(
    emitter_radius_m: float,
    target_radius_m: float,
    center_distance_m: float,
    emitter_surface_field_t: float,
    volume_susceptibility: float,
) -> float:
    """Magnitude of an idealized force on a weakly magnetic spherical target.

    The source is represented by a dipole-like axial field
    B(r)=B_surface(R/r)^3. For a linear material,
    F = chi V grad(B^2)/(2 mu0), and |grad(B^2)| = 6 B^2/r.

    The returned magnitude therefore scales as |chi| r^-7. The sign of
    susceptibility determines attraction versus repulsion. This model is only
    for weak linear dia/paramagnetic materials; it does not generalize a
    ferromagnetic-target result to arbitrary objects.
    """

    source_r = _positive("emitter_radius_m", emitter_radius_m)
    target_r = _positive("target_radius_m", target_radius_m)
    distance = _positive("center_distance_m", center_distance_m)
    surface_b = _nonnegative("emitter_surface_field_t", emitter_surface_field_t)
    if distance <= source_r + target_r:
        raise ValueError("center_distance_m must exceed emitter_radius_m + target_radius_m")
    b = surface_b * (source_r / distance) ** 3
    grad_b2 = 6.0 * b * b / distance
    volume = 4.0 * pi * target_r**3 / 3.0
    return abs(volume_susceptibility) * volume * grad_b2 / (2.0 * VACUUM_PERMEABILITY_H_M)


__all__ = [
    "DEFAULT_AIR_DENSITY_KG_M3",
    "MechanismEstimate",
    "SPEED_OF_LIGHT_M_S",
    "VACUUM_PERMEABILITY_H_M",
    "VACUUM_PERMITTIVITY_F_M",
    "electrostatic_induced_force_sphere",
    "magnetic_susceptibility_force_sphere",
    "optical_power_for_force",
    "optical_radiation_force",
    "round_jet_capture_fraction",
    "round_jet_exit_velocity_for_force",
    "round_jet_force_on_centered_disk",
    "round_jet_kinetic_power_for_force",
    "round_jet_kinetic_power",
    "round_jet_nozzle_area",
    "round_jet_thrust",
]
