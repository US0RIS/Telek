import math

import pytest

from telek.acoustics import (
    DEFAULT_SOUND_SPEED_M_S,
    STANDARD_GRAVITY_M_S2,
    ideal_force_from_incident_power,
    ideal_incident_power_for_force,
    ideal_incident_power_to_hold_mass,
    required_vertical_force,
)


def test_force_power_are_inverse_at_ideal_reflection() -> None:
    for power in (0.0, 1.0, 100.0, 1000.0):
        force = ideal_force_from_incident_power(power)
        recovered = ideal_incident_power_for_force(force)
        assert math.isclose(recovered, power, rel_tol=1e-12, abs_tol=1e-12)


def test_one_newton_requires_171_5_w_at_343_m_s() -> None:
    assert ideal_incident_power_for_force(1.0) == pytest.approx(171.5)


def test_half_kg_hold_floor_is_about_840_w() -> None:
    expected = 0.5 * STANDARD_GRAVITY_M_S2 * DEFAULT_SOUND_SPEED_M_S / 2.0
    assert ideal_incident_power_to_hold_mass(0.5) == pytest.approx(expected)
    assert expected == pytest.approx(840.92, abs=0.1)


def test_added_upward_acceleration_increases_force() -> None:
    assert required_vertical_force(1.0, 2.0) == pytest.approx(STANDARD_GRAVITY_M_S2 + 2.0)


def test_large_downward_acceleration_clamps_support_force_at_zero() -> None:
    assert required_vertical_force(1.0, -20.0) == 0.0


def test_invalid_inputs_fail_loudly() -> None:
    with pytest.raises(ValueError):
        ideal_force_from_incident_power(-1)
    with pytest.raises(ValueError):
        ideal_incident_power_for_force(1, momentum_multiplier=0)
    with pytest.raises(ValueError):
        ideal_force_from_incident_power(1, momentum_multiplier=2.1)
