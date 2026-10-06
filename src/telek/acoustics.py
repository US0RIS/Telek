"""Ideal acoustic momentum-transfer bounds.

These functions intentionally model only the most favorable momentum-flux limit.
They do NOT include transducer efficiency, diffraction, focusing loss, absorption,
target coupling, thermal limits, or safety limits. Treat returned powers as hard
physics floors, not practical device specifications.
"""

from __future__ import annotations

DEFAULT_SOUND_SPEED_M_S = 343.0
STANDARD_GRAVITY_M_S2 = 9.80665


def _positive(name: str, value: float, *, allow_zero: bool = False) -> float:
    if allow_zero:
        if value < 0:
            raise ValueError(f"{name} must be >= 0")
    elif value <= 0:
        raise ValueError(f"{name} must be > 0")
    return float(value)


def ideal_force_from_incident_power(
    incident_power_w: float,
    *,
    sound_speed_m_s: float = DEFAULT_SOUND_SPEED_M_S,
    momentum_multiplier: float = 2.0,
) -> float:
    """Return the ideal axial force from acoustic power incident on a target.

    ``momentum_multiplier=1`` approximates perfect absorption; ``2`` approximates
    perfect normal reflection. Values outside [0, 2] are rejected because this
    helper is intended as a simple passive-target momentum-flux bound.
    """

    power = _positive("incident_power_w", incident_power_w, allow_zero=True)
    c = _positive("sound_speed_m_s", sound_speed_m_s)
    if not 0.0 <= momentum_multiplier <= 2.0:
        raise ValueError("momentum_multiplier must be in [0, 2]")
    return momentum_multiplier * power / c


def ideal_incident_power_for_force(
    force_n: float,
    *,
    sound_speed_m_s: float = DEFAULT_SOUND_SPEED_M_S,
    momentum_multiplier: float = 2.0,
) -> float:
    """Return the minimum ideal incident acoustic power for axial force ``force_n``."""

    force = _positive("force_n", force_n, allow_zero=True)
    c = _positive("sound_speed_m_s", sound_speed_m_s)
    if not 0.0 < momentum_multiplier <= 2.0:
        raise ValueError("momentum_multiplier must be in (0, 2]")
    return force * c / momentum_multiplier


def required_vertical_force(mass_kg: float, upward_accel_m_s2: float = 0.0) -> float:
    """Force required to support mass and add the requested upward acceleration."""

    mass = _positive("mass_kg", mass_kg, allow_zero=True)
    return max(0.0, mass * (STANDARD_GRAVITY_M_S2 + upward_accel_m_s2))


def ideal_incident_power_to_hold_mass(
    mass_kg: float,
    *,
    upward_accel_m_s2: float = 0.0,
    sound_speed_m_s: float = DEFAULT_SOUND_SPEED_M_S,
    momentum_multiplier: float = 2.0,
) -> float:
    """Ideal incident acoustic-power floor to support/accelerate a mass upward."""

    force = required_vertical_force(mass_kg, upward_accel_m_s2)
    return ideal_incident_power_for_force(
        force,
        sound_speed_m_s=sound_speed_m_s,
        momentum_multiplier=momentum_multiplier,
    )
