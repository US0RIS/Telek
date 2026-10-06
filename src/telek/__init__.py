"""Telek physics and control primitives."""

from .acoustics import (
    DEFAULT_SOUND_SPEED_M_S,
    ideal_force_from_incident_power,
    ideal_incident_power_for_force,
    ideal_incident_power_to_hold_mass,
)
from .atmosphere import Air, iso9613_absorption_db_per_m
from .linkbudget import LinkBudget, LinkScenario, evaluate_link
from .nonlinear import radiation_force_supremum, saturated_intensity_supremum
from .model import ForceCommand, GestureEvent, Vec3

__all__ = [
    "Air",
    "LinkBudget",
    "LinkScenario",
    "evaluate_link",
    "iso9613_absorption_db_per_m",
    "radiation_force_supremum",
    "saturated_intensity_supremum",
    "DEFAULT_SOUND_SPEED_M_S",
    "ForceCommand",
    "GestureEvent",
    "Vec3",
    "ideal_force_from_incident_power",
    "ideal_incident_power_for_force",
    "ideal_incident_power_to_hold_mass",
]
