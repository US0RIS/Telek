"""Nonlinear (shock) saturation limits on acoustic power delivered at range.

Classification: **physical bound (approximate)** under these stated assumptions:

- lossless weak-shock theory (Burgers/Earnshaw characteristics + equal-area
  shock fitting) for an initially sinusoidal wave;
- locally plane wavefronts propagating in spherical/collimated ray tubes
  (collimated, converging-to-focus, or diverging beams);
- acoustic Mach number << 1 (true here: saturated pressures are ~kPa vs
  rho c^2 ~ 140 kPa);
- thermoviscous and molecular-relaxation absorption are ignored, which can only
  *lower* delivered power, so ignoring them keeps the bound favorable.

Key result (see ``docs/PHYSICS.md``): however strong the source, the
mean-square pressure of a plane wave after propagating a distance ``x`` cannot
exceed the sawtooth saturation value, giving the intensity supremum

    I_sup(x) = pi^2 rho c^5 / (3 beta^2 omega^2 x^2).

For converging, collimated or diverging ray tubes from an aperture of area
``A_ap`` to a target of area ``A_t`` at path length ``L``, the acoustic power
reaching the target obeys ``P <= I_sup(L) * max(A_ap, A_t)``.

What this does NOT bound: wave momentum dissipated at shocks is transferred to
the air and drives acoustic streaming. That momentum can still reach a target
as wind. It is limited by the total radiated momentum flux ``P_ac / c`` and
behaves like a directed airflow jet (spreading, entrainment, poor selectivity),
so it belongs to the airflow mechanism model, not to radiation pressure.
General beam shapes (strongly non-spherical wavefronts, Bessel beams, full
diffraction-nonlinearity coupling as in KZK models) are not covered rigorously.
"""

from __future__ import annotations

from math import log, pi, sin

from .atmosphere import Air


def _check_positive(name: str, value: float) -> float:
    if value <= 0:
        raise ValueError(f"{name} must be > 0")
    return float(value)


def shock_formation_distance_m(source_amplitude_pa: float, frequency_hz: float, air: Air = Air()) -> float:
    """Plane-wave shock formation distance ``x_bar = rho c^3 / (beta omega p0)``."""

    p0 = _check_positive("source_amplitude_pa", source_amplitude_pa)
    omega = 2.0 * pi * _check_positive("frequency_hz", frequency_hz)
    rho, c, beta = air.density_kg_m3, air.sound_speed_m_s, air.nonlinearity_coefficient
    return rho * c**3 / (beta * omega * p0)


def _shock_phase(sigma: float) -> float:
    """Solve ``phi = sigma sin(phi)`` for phi in (0, pi), sigma > 1, by bisection."""

    lo, hi = 0.0, pi
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if mid - sigma * sin(mid) < 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def normalized_mean_square(sigma: float) -> float:
    """<p^2>/p0^2 for an initially sinusoidal plane wave at normalized distance sigma.

    ``sigma = x / x_bar``. For sigma <= 1 no shock has formed and the lossless
    value is 1/2. For sigma > 1 the shock-fitted waveform gives

        <p^2>/p0^2 = [pi - phi_s + sin(2 phi_s)/2 + (2/3) sigma sin^3 phi_s] / (2 pi)

    with ``phi_s = sigma sin(phi_s)``. As sigma -> inf this tends to the
    sawtooth result (pi/(1+sigma))^2 / 3.
    """

    if sigma < 0:
        raise ValueError("sigma must be >= 0")
    if sigma <= 1.0:
        return 0.5
    phi = _shock_phase(sigma)
    s = sin(phi)
    bracket = pi - phi + 0.5 * sin(2.0 * phi) + (2.0 / 3.0) * sigma * s**3
    return bracket / (2.0 * pi)


def plane_wave_intensity_at_distance(
    source_amplitude_pa: float,
    frequency_hz: float,
    distance_m: float,
    air: Air = Air(),
) -> float:
    """Lossless weak-shock intensity (W/m^2) of a plane wave after ``distance_m``."""

    if distance_m < 0:
        raise ValueError("distance_m must be >= 0")
    p0 = _check_positive("source_amplitude_pa", source_amplitude_pa)
    sigma = distance_m / shock_formation_distance_m(p0, frequency_hz, air)
    return p0 * p0 * normalized_mean_square(sigma) / air.impedance_rayl


def saturated_intensity_supremum(frequency_hz: float, distance_m: float, air: Air = Air()) -> float:
    """Supremum over source amplitude of plane-wave intensity at ``distance_m``.

    ``I_sup = pi^2 rho c^5 / (3 beta^2 omega^2 x^2)``. Independent of source power.
    """

    x = _check_positive("distance_m", distance_m)
    omega = 2.0 * pi * _check_positive("frequency_hz", frequency_hz)
    rho, c, beta = air.density_kg_m3, air.sound_speed_m_s, air.nonlinearity_coefficient
    return pi**2 * rho * c**5 / (3.0 * beta**2 * omega**2 * x**2)


def delivered_power_supremum(
    frequency_hz: float,
    path_length_m: float,
    aperture_area_m2: float,
    target_area_m2: float,
    air: Air = Air(),
) -> float:
    """Upper bound on acoustic power reaching a target through spherical/collimated ray tubes."""

    a_ap = _check_positive("aperture_area_m2", aperture_area_m2)
    a_t = _check_positive("target_area_m2", target_area_m2)
    return saturated_intensity_supremum(frequency_hz, path_length_m, air) * max(a_ap, a_t)


def radiation_force_supremum(
    frequency_hz: float,
    path_length_m: float,
    aperture_area_m2: float,
    target_area_m2: float,
    *,
    momentum_multiplier: float = 2.0,
    air: Air = Air(),
) -> float:
    """Upper bound on acoustic radiation force (N) at range from shock saturation."""

    if not 0.0 < momentum_multiplier <= 2.0:
        raise ValueError("momentum_multiplier must be in (0, 2]")
    power = delivered_power_supremum(frequency_hz, path_length_m, aperture_area_m2, target_area_m2, air)
    return momentum_multiplier * power / air.sound_speed_m_s


def required_area_for_force(
    force_n: float,
    frequency_hz: float,
    path_length_m: float,
    *,
    momentum_multiplier: float = 2.0,
    air: Air = Air(),
) -> float:
    """Minimum ``max(A_aperture, A_target)`` (m^2) for which the saturation bound allows ``force_n``."""

    force = _check_positive("force_n", force_n)
    if not 0.0 < momentum_multiplier <= 2.0:
        raise ValueError("momentum_multiplier must be in (0, 2]")
    intensity = saturated_intensity_supremum(frequency_hz, path_length_m, air)
    return force * air.sound_speed_m_s / (momentum_multiplier * intensity)


def converging_wave_effective_distance(start_radius_m: float, end_radius_m: float) -> float:
    """Equivalent plane-wave nonlinear distance for a converging spherical wave.

    ``x_eff = R0 ln(R0 / r)``; always >= the geometric path ``R0 - r``.
    """

    r0 = _check_positive("start_radius_m", start_radius_m)
    r = _check_positive("end_radius_m", end_radius_m)
    if r > r0:
        raise ValueError("converging wave requires end_radius_m <= start_radius_m")
    return r0 * log(r0 / r)


__all__ = [
    "converging_wave_effective_distance",
    "delivered_power_supremum",
    "normalized_mean_square",
    "plane_wave_intensity_at_distance",
    "radiation_force_supremum",
    "required_area_for_force",
    "saturated_intensity_supremum",
    "shock_formation_distance_m",
]
