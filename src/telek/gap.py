"""Quantify the gap between CRITERIA.md milestones and airborne radiation-pressure bounds.

Only the shock-saturation supremum is used here, so the results do not depend on
transducer efficiency, electrical power, or array engineering. A milestone that
fails this test cannot be met by acoustic radiation pressure from a wearable
aperture at that frequency, under the assumptions listed in ``nonlinear.py``.
"""

from __future__ import annotations

from dataclasses import dataclass

from .atmosphere import Air
from .linkbudget import required_force_to_lift, required_force_to_slide
from .nonlinear import radiation_force_supremum, required_area_for_force


@dataclass(frozen=True, slots=True)
class Milestone:
    name: str
    mass_kg: float
    range_m: float
    must_lift: bool


# Mass/range values from CRITERIA.md section 5. ``must_lift`` is True only where
# the criteria demand countering gravity; otherwise a sliding case is evaluated.
MILESTONES: tuple[Milestone, ...] = (
    Milestone("M2", 0.010, 0.25, must_lift=False),
    Milestone("M3", 0.100, 1.0, must_lift=False),
    Milestone("M4", 0.500, 3.0, must_lift=True),
)


@dataclass(frozen=True, slots=True)
class GapRow:
    milestone: str
    mode: str
    frequency_hz: float
    required_force_n: float
    force_supremum_n: float
    required_area_m2: float

    @property
    def margin(self) -> float:
        return self.force_supremum_n / self.required_force_n


def milestone_gap(
    *,
    aperture_area_m2: float,
    target_area_m2: float,
    frequencies_hz: tuple[float, ...] = (20e3, 25e3, 40e3),
    friction_coefficient: float = 0.3,
    momentum_multiplier: float = 2.0,
    air: Air = Air(),
) -> list[GapRow]:
    """Evaluate each milestone in lift and (where allowed) slide modes."""

    rows: list[GapRow] = []
    for m in MILESTONES:
        modes = [("lift", required_force_to_lift(m.mass_kg))]
        if not m.must_lift:
            modes.append((f"slide mu={friction_coefficient:g}", required_force_to_slide(m.mass_kg, friction_coefficient)))
        for mode, force in modes:
            for f in frequencies_hz:
                rows.append(
                    GapRow(
                        milestone=m.name,
                        mode=mode,
                        frequency_hz=f,
                        required_force_n=force,
                        force_supremum_n=radiation_force_supremum(
                            f,
                            m.range_m,
                            aperture_area_m2,
                            target_area_m2,
                            momentum_multiplier=momentum_multiplier,
                            air=air,
                        ),
                        required_area_m2=required_area_for_force(
                            force, f, m.range_m, momentum_multiplier=momentum_multiplier, air=air
                        ),
                    )
                )
    return rows
