from math import log, pi

import pytest

from telek.atmosphere import Air, absorption_power_transmission, iso9613_absorption_db_per_m
from telek.cli import main
from telek.gap import milestone_gap
from telek.linkbudget import (
    LinkScenario,
    airy_encircled_energy,
    bessel_j,
    diffraction_capture_fraction,
    evaluate_link,
    momentum_multiplier_for_target,
    required_force_to_slide,
)
from telek.nonlinear import (
    converging_wave_effective_distance,
    normalized_mean_square,
    plane_wave_intensity_at_distance,
    radiation_force_supremum,
    required_area_for_force,
    saturated_intensity_supremum,
    shock_formation_distance_m,
)

AIR = Air()


# --- atmosphere -----------------------------------------------------------

def test_iso9613_matches_standard_table_at_1khz() -> None:
    # ISO 9613-1 Table 1: 20 C, 70 % RH, 1 kHz -> 4.98 dB/km.
    assert iso9613_absorption_db_per_m(1000, Air(relative_humidity_pct=70)) == pytest.approx(4.98e-3, rel=0.01)


def test_40khz_absorption_is_about_1_3_db_per_m() -> None:
    assert iso9613_absorption_db_per_m(40e3, AIR) == pytest.approx(1.32, rel=0.05)


def test_absorption_increases_with_frequency_in_ultrasound() -> None:
    values = [iso9613_absorption_db_per_m(f, AIR) for f in (20e3, 40e3, 80e3)]
    assert values == sorted(values)


def test_transmission_is_unity_at_zero_range() -> None:
    assert absorption_power_transmission(40e3, 0.0) == 1.0


def test_air_properties_near_standard_values() -> None:
    assert AIR.density_kg_m3 == pytest.approx(1.204, rel=0.002)
    assert AIR.sound_speed_m_s == pytest.approx(343.2, rel=0.002)
    assert AIR.nonlinearity_coefficient == pytest.approx(1.2)


# --- nonlinear saturation ---------------------------------------------------

def test_preshock_wave_keeps_linear_mean_square() -> None:
    assert normalized_mean_square(0.0) == 0.5
    assert normalized_mean_square(1.0) == 0.5


def test_mean_square_is_continuous_at_shock_formation() -> None:
    assert normalized_mean_square(1.0 + 1e-6) == pytest.approx(0.5, abs=1e-4)


def test_mean_square_approaches_sawtooth_far_field() -> None:
    for sigma in (50.0, 500.0):
        sawtooth = (pi / (1.0 + sigma)) ** 2 / 3.0
        assert normalized_mean_square(sigma) == pytest.approx(sawtooth, rel=1e-4)


def test_intensity_rises_monotonically_toward_but_never_exceeds_supremum() -> None:
    # sigma^2 <p^2>/p0^2 is the intensity at fixed distance as source amplitude grows.
    previous = 0.0
    for i in range(1, 4001):
        sigma = i * 0.05
        value = sigma * sigma * normalized_mean_square(sigma)
        assert value >= previous - 1e-12
        assert value < pi**2 / 3.0
        previous = value


def test_plane_wave_intensity_respects_supremum_for_any_source() -> None:
    sup = saturated_intensity_supremum(40e3, 1.0)
    for p0 in (10.0, 1e3, 1e4, 1e5):
        assert plane_wave_intensity_at_distance(p0, 40e3, 1.0) < sup


def test_saturation_scaling_with_frequency_and_range() -> None:
    base = saturated_intensity_supremum(40e3, 1.0)
    assert saturated_intensity_supremum(20e3, 1.0) == pytest.approx(4 * base)
    assert saturated_intensity_supremum(40e3, 2.0) == pytest.approx(base / 4)


def test_40khz_one_metre_supremum_value() -> None:
    # pi^2 rho c^5 / (3 beta^2 omega^2 x^2) with rho=1.204, c=343.2, beta=1.2.
    assert saturated_intensity_supremum(40e3, 1.0) == pytest.approx(207.5, rel=0.01)


def test_shock_distance_inverse_in_amplitude() -> None:
    assert shock_formation_distance_m(200.0, 40e3) == pytest.approx(shock_formation_distance_m(100.0, 40e3) / 2)


def test_converging_effective_distance_exceeds_geometric_path() -> None:
    r0 = 1.0
    for r in (0.9, 0.5, 0.1, 0.01):
        assert converging_wave_effective_distance(r0, r) >= r0 - r
    assert converging_wave_effective_distance(r0, r0 / 10) == pytest.approx(log(10))


def test_diverging_tube_bound_inequality() -> None:
    # Basis for using max(A_ap, A_t): u <= (1+u) ln(1+u) for u >= 0.
    for u in (1e-3, 0.1, 1.0, 10.0, 1e3):
        assert u <= (1 + u) * log(1 + u)


def test_required_area_inverts_force_bound() -> None:
    area = required_area_for_force(1.0, 40e3, 1.0)
    assert radiation_force_supremum(40e3, 1.0, area, area / 10) == pytest.approx(1.0)


# --- link budget ------------------------------------------------------------

def test_bessel_values() -> None:
    assert bessel_j(0, 0.0) == pytest.approx(1.0)
    assert bessel_j(1, 0.0) == pytest.approx(0.0, abs=1e-15)
    assert bessel_j(0, 2.404825557695773) == pytest.approx(0.0, abs=1e-12)
    assert bessel_j(1, 3.831705970207512) == pytest.approx(0.0, abs=1e-12)


def test_airy_first_dark_ring_contains_83_8_percent() -> None:
    assert airy_encircled_energy(3.831705970207512) == pytest.approx(0.8378, abs=1e-4)


def test_capture_fraction_shrinks_with_range() -> None:
    near = diffraction_capture_fraction(0.3, 0.05, 0.5, 40e3)
    far = diffraction_capture_fraction(0.3, 0.05, 5.0, 40e3)
    assert 0.0 < far < near <= 1.0


def test_hard_solid_target_momentum_multiplier_near_two() -> None:
    assert momentum_multiplier_for_target(1.5e6) == pytest.approx(2.0, abs=2e-3)
    assert momentum_multiplier_for_target(AIR.impedance_rayl) == pytest.approx(1.0)


def test_slide_force() -> None:
    assert required_force_to_slide(0.1, 0.3) == pytest.approx(0.1 * 0.3 * 9.80665)


def _scenario(**overrides: float) -> LinkScenario:
    base = dict(
        frequency_hz=40e3,
        range_m=1.0,
        aperture_diameter_m=0.3,
        target_diameter_m=0.1,
        electrical_power_w=100.0,
        electroacoustic_efficiency=0.1,
        max_acoustic_power_w=1000.0,
    )
    base.update(overrides)
    return LinkScenario(**base)


def test_link_force_never_exceeds_ideal_momentum_bound() -> None:
    b = evaluate_link(_scenario())
    assert b.force_n <= 2.0 * b.acoustic_power_w / AIR.sound_speed_m_s


def test_huge_source_power_hits_shock_saturation() -> None:
    b = evaluate_link(_scenario(electrical_power_w=1e6, electroacoustic_efficiency=1.0, max_acoustic_power_w=1e6))
    assert b.limiting_factor == "shock saturation"
    assert b.delivered_power_w == pytest.approx(b.nonlinear_power_cap_w)


def test_transducer_cap_is_reported() -> None:
    b = evaluate_link(_scenario(range_m=0.25, max_acoustic_power_w=1.0))
    assert b.acoustic_power_w == 1.0
    assert b.limiting_factor == "transducer acoustic-power limit"


def test_invalid_scenario_rejected() -> None:
    with pytest.raises(ValueError):
        _scenario(electroacoustic_efficiency=0.0)
    with pytest.raises(ValueError):
        _scenario(misalignment_deg=90.0)


# --- milestone gap ----------------------------------------------------------

def test_m4_is_far_below_weak_shock_model_ceiling() -> None:
    rows = milestone_gap(aperture_area_m2=pi * 0.15**2, target_area_m2=pi * 0.05**2)
    m4 = [r for r in rows if r.milestone == "M4"]
    assert m4 and all(r.margin < 0.01 for r in m4)


def test_m2_is_not_ruled_out_by_saturation() -> None:
    rows = milestone_gap(aperture_area_m2=pi * 0.15**2, target_area_m2=pi * 0.05**2)
    assert all(r.margin > 1 for r in rows if r.milestone == "M2")


def test_cli_gap_runs(capsys: pytest.CaptureFixture[str]) -> None:
    main(["gap"])
    out = capsys.readouterr().out
    assert "M4" in out and "model ceiling" in out
