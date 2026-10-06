import pytest

from telek import mechanisms as m


def test_optical_force_power_inverse() -> None:
    for force in (0.0, 1e-6, 1.0, 5.0):
        power = m.optical_power_for_force(force)
        assert m.optical_radiation_force(power) == pytest.approx(force)


def test_one_newton_optical_reflection_needs_about_150_mw() -> None:
    assert m.optical_power_for_force(1.0) / 1e6 == pytest.approx(149.896229, rel=1e-8)


def test_round_jet_power_thrust_relation() -> None:
    d, v = 0.05, 100.0
    thrust = m.round_jet_thrust(d, v)
    power = m.round_jet_kinetic_power(d, v)
    assert power == pytest.approx(0.5 * thrust * v)


def test_round_jet_far_capture_decreases_with_range_and_increases_with_target_size() -> None:
    c1 = m.round_jet_capture_fraction(0.05, 0.10, 1.0)
    c3 = m.round_jet_capture_fraction(0.05, 0.10, 3.0)
    bigger = m.round_jet_capture_fraction(0.05, 0.20, 3.0)
    assert 0 < c3 < c1 < 1
    assert bigger > c3


def test_round_jet_reference_case() -> None:
    force = m.round_jet_force_on_centered_disk(0.05, 100.0, 0.10, 3.0)
    assert force == pytest.approx(1.17922, rel=1e-4)
    assert m.round_jet_kinetic_power(0.05, 100.0) == pytest.approx(1182.02, rel=1e-4)


def test_round_jet_inverse_force_solution() -> None:
    target_force = 0.5 * 9.80665
    velocity = m.round_jet_exit_velocity_for_force(target_force, 0.05, 0.10, 3.0)
    force = m.round_jet_force_on_centered_disk(0.05, velocity, 0.10, 3.0)
    assert force == pytest.approx(target_force)
    assert velocity == pytest.approx(203.914, rel=1e-4)
    assert m.round_jet_kinetic_power_for_force(target_force, 0.05, 0.10, 3.0) == pytest.approx(
        10022.3, rel=1e-4
    )


def test_electrostatic_force_has_r_minus_five_scaling() -> None:
    f1 = m.electrostatic_induced_force_sphere(0.05, 0.005, 0.5, 1e6)
    f2 = m.electrostatic_induced_force_sphere(0.05, 0.005, 1.0, 1e6)
    assert f2 == pytest.approx(f1 / 32.0)


def test_magnetic_force_has_r_minus_seven_scaling() -> None:
    f1 = m.magnetic_susceptibility_force_sphere(0.05, 0.005, 0.5, 1.0, 1e-5)
    f2 = m.magnetic_susceptibility_force_sphere(0.05, 0.005, 1.0, 1.0, 1e-5)
    assert f2 == pytest.approx(f1 / 128.0)


def test_reference_long_range_field_forces_are_tiny() -> None:
    electro = m.electrostatic_induced_force_sphere(0.15, 0.05, 3.0, 3e6)
    magnetic = m.magnetic_susceptibility_force_sphere(0.15, 0.05, 3.0, 2.0, 1e-5)
    assert electro == pytest.approx(5.21555e-7, rel=1e-5)
    assert magnetic == pytest.approx(2.60417e-10, rel=1e-5)


def test_invalid_inputs_fail() -> None:
    with pytest.raises(ValueError):
        m.optical_radiation_force(-1)
    with pytest.raises(ValueError):
        m.round_jet_capture_fraction(0, 0.1, 1)
    with pytest.raises(ValueError):
        m.electrostatic_induced_force_sphere(0.15, 0.05, 0.19, 1e6)
    with pytest.raises(ValueError):
        m.magnetic_susceptibility_force_sphere(0.15, 0.05, 0.19, 1.0, 1e-5)
