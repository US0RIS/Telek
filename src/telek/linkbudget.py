"""Engineering acoustic link budget: electrical power -> force on an unmodified target.

Every factor is an explicit input or an explicitly labeled model:

=========================  ==================================  =====================
factor                     model                               classification
=========================  ==================================  =====================
electro-acoustic eff.      user input                          engineering assumption
max acoustic power         user input (transducer/thermal)     engineering assumption
atmospheric absorption     ISO 9613-1                          engineering estimate
diffraction capture        paraxial Airy encircled energy      physical model
target momentum coupling   1 + |R|^2, normal incidence         physical bound
alignment                  cos(angle)                          geometry input
shock saturation           weak-shock supremum (nonlinear.py)  physical bound (approx)
=========================  ==================================  =====================

The resulting force is an *optimistic engineering estimate*: it assumes a
perfectly phased, uniformly weighted circular aperture focused on the target,
ignores grating lobes, phase quantization, element directivity, near-field
standing waves between wearer and target, and trap stability.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, pi, radians, sin, sqrt

from .acoustics import STANDARD_GRAVITY_M_S2
from .atmosphere import Air, absorption_power_transmission
from .nonlinear import delivered_power_supremum


def bessel_j(n: int, x: float) -> float:
    """Integer-order Bessel function via the periodic trapezoid rule (spectrally accurate)."""

    if n < 0:
        raise ValueError("n must be >= 0")
    steps = max(64, int(2 * abs(x)) + 2 * n + 64)
    h = 2.0 * pi / steps
    total = sum(cos(n * k * h - x * sin(k * h)) for k in range(steps))
    return total / steps


def airy_encircled_energy(x: float) -> float:
    """Fraction of an Airy pattern's power within normalized radius ``x = k a rho / L``."""

    if x < 0:
        raise ValueError("x must be >= 0")
    return 1.0 - bessel_j(0, x) ** 2 - bessel_j(1, x) ** 2


def diffraction_capture_fraction(
    aperture_diameter_m: float,
    target_diameter_m: float,
    range_m: float,
    frequency_hz: float,
    air: Air = Air(),
) -> float:
    """Fraction of power from a focused uniform circular aperture landing on a coaxial disk target.

    Paraxial (Fresnel) focal-plane Airy pattern. Inaccurate for numerical
    apertures approaching 1 (aperture diameter comparable to range); the result
    is still a fraction in [0, 1].
    """

    for name, value in (
        ("aperture_diameter_m", aperture_diameter_m),
        ("target_diameter_m", target_diameter_m),
        ("range_m", range_m),
        ("frequency_hz", frequency_hz),
    ):
        if value <= 0:
            raise ValueError(f"{name} must be > 0")
    wavelength = air.sound_speed_m_s / frequency_hz
    x = pi * aperture_diameter_m * target_diameter_m / (2.0 * wavelength * range_m)
    return min(1.0, max(0.0, airy_encircled_energy(x)))


def pressure_reflection_coefficient(target_impedance_rayl: float, medium_impedance_rayl: float) -> float:
    """Normal-incidence plane-wave pressure reflection coefficient."""

    if target_impedance_rayl <= 0 or medium_impedance_rayl <= 0:
        raise ValueError("impedances must be > 0")
    return (target_impedance_rayl - medium_impedance_rayl) / (target_impedance_rayl + medium_impedance_rayl)


def momentum_multiplier_for_target(target_impedance_rayl: float, air: Air = Air()) -> float:
    """``1 + R^2``: upper bound for a passive target that lets nothing exit its far side."""

    r = pressure_reflection_coefficient(target_impedance_rayl, air.impedance_rayl)
    return 1.0 + r * r


def required_force_to_lift(mass_kg: float, upward_accel_m_s2: float = 0.0) -> float:
    if mass_kg < 0:
        raise ValueError("mass_kg must be >= 0")
    return max(0.0, mass_kg * (STANDARD_GRAVITY_M_S2 + upward_accel_m_s2))


def required_force_to_slide(mass_kg: float, friction_coefficient: float, accel_m_s2: float = 0.0) -> float:
    """Horizontal force to break static friction (``mu m g``) plus ``m a``."""

    if mass_kg < 0:
        raise ValueError("mass_kg must be >= 0")
    if friction_coefficient < 0:
        raise ValueError("friction_coefficient must be >= 0")
    if accel_m_s2 < 0:
        raise ValueError("accel_m_s2 must be >= 0")
    return mass_kg * (friction_coefficient * STANDARD_GRAVITY_M_S2 + accel_m_s2)


@dataclass(frozen=True, slots=True)
class LinkScenario:
    """All assumptions for one acoustic link. No hidden defaults except ambient air."""

    frequency_hz: float
    range_m: float
    aperture_diameter_m: float
    target_diameter_m: float
    electrical_power_w: float
    electroacoustic_efficiency: float
    max_acoustic_power_w: float
    momentum_multiplier: float = 2.0
    misalignment_deg: float = 0.0
    air: Air = Air()

    def __post_init__(self) -> None:
        for name in (
            "frequency_hz",
            "range_m",
            "aperture_diameter_m",
            "target_diameter_m",
            "max_acoustic_power_w",
        ):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be > 0")
        if self.electrical_power_w < 0:
            raise ValueError("electrical_power_w must be >= 0")
        if not 0.0 < self.electroacoustic_efficiency <= 1.0:
            raise ValueError("electroacoustic_efficiency must be in (0, 1]")
        if not 0.0 < self.momentum_multiplier <= 2.0:
            raise ValueError("momentum_multiplier must be in (0, 2]")
        if not 0.0 <= self.misalignment_deg < 90.0:
            raise ValueError("misalignment_deg must be in [0, 90)")

    @property
    def aperture_area_m2(self) -> float:
        return pi * self.aperture_diameter_m**2 / 4.0

    @property
    def target_area_m2(self) -> float:
        return pi * self.target_diameter_m**2 / 4.0


@dataclass(frozen=True, slots=True)
class LinkBudget:
    scenario: LinkScenario
    acoustic_power_w: float
    absorption_transmission: float
    capture_fraction: float
    linear_delivered_power_w: float
    nonlinear_power_cap_w: float
    delivered_power_w: float
    force_n: float
    limiting_factor: str

    def margin(self, required_force_n: float) -> float:
        """Achievable / required force. Values < 1 mean the scenario fails."""

        if required_force_n <= 0:
            raise ValueError("required_force_n must be > 0")
        return self.force_n / required_force_n


def evaluate_link(s: LinkScenario) -> LinkBudget:
    electrical_acoustic = s.electrical_power_w * s.electroacoustic_efficiency
    acoustic = min(electrical_acoustic, s.max_acoustic_power_w)
    transmission = absorption_power_transmission(s.frequency_hz, s.range_m, s.air)
    capture = diffraction_capture_fraction(
        s.aperture_diameter_m, s.target_diameter_m, s.range_m, s.frequency_hz, s.air
    )
    linear = acoustic * transmission * capture
    cap = delivered_power_supremum(s.frequency_hz, s.range_m, s.aperture_area_m2, s.target_area_m2, s.air)
    delivered = min(linear, cap)

    # Name the dominant loss; if propagation keeps more than half the power,
    # the source itself is the bottleneck.
    if cap < linear:
        limiting = "shock saturation"
    elif min(transmission, capture) < 0.5:
        limiting = "atmospheric absorption" if transmission < capture else "diffraction capture"
    elif electrical_acoustic > s.max_acoustic_power_w:
        limiting = "transducer acoustic-power limit"
    else:
        limiting = "electrical power x efficiency"

    force = s.momentum_multiplier * cos(radians(s.misalignment_deg)) * delivered / s.air.sound_speed_m_s
    return LinkBudget(
        scenario=s,
        acoustic_power_w=acoustic,
        absorption_transmission=transmission,
        capture_fraction=capture,
        linear_delivered_power_w=linear,
        nonlinear_power_cap_w=cap,
        delivered_power_w=delivered,
        force_n=force,
        limiting_factor=limiting,
    )


def equivalent_disk_diameter(area_m2: float) -> float:
    if area_m2 <= 0:
        raise ValueError("area_m2 must be > 0")
    return sqrt(4.0 * area_m2 / pi)
