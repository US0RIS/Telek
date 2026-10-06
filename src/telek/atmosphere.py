"""Air properties and atmospheric sound absorption.

Classification: **engineering estimate** (standardized empirical model).

``iso9613_absorption_db_per_m`` implements the pure-tone atmospheric absorption
equations of ISO 9613-1:1993. The standard states its equations are intended for
roughly 50 Hz to 10 MHz, but its quoted accuracy (about +/-10 %) applies to the
audio band; treat ultrasonic values as estimates. No fitted constants are added
beyond those published in the standard.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, log10, sqrt

REFERENCE_PRESSURE_PA = 101_325.0
REFERENCE_TEMPERATURE_K = 293.15
TRIPLE_POINT_WATER_K = 273.16
DRY_AIR_GAS_CONSTANT_J_KG_K = 287.05
DRY_AIR_GAMMA = 1.4


@dataclass(frozen=True, slots=True)
class Air:
    """Ambient air state. Defaults: 20 C, 50 % RH, 1 standard atmosphere."""

    temperature_k: float = REFERENCE_TEMPERATURE_K
    relative_humidity_pct: float = 50.0
    pressure_pa: float = REFERENCE_PRESSURE_PA

    def __post_init__(self) -> None:
        if self.temperature_k <= 0:
            raise ValueError("temperature_k must be > 0")
        if not 0.0 <= self.relative_humidity_pct <= 100.0:
            raise ValueError("relative_humidity_pct must be in [0, 100]")
        if self.pressure_pa <= 0:
            raise ValueError("pressure_pa must be > 0")

    @property
    def density_kg_m3(self) -> float:
        """Dry-air ideal-gas density (humidity changes this by < 1 % near 20 C)."""

        return self.pressure_pa / (DRY_AIR_GAS_CONSTANT_J_KG_K * self.temperature_k)

    @property
    def sound_speed_m_s(self) -> float:
        """Dry-air ideal-gas sound speed."""

        return sqrt(DRY_AIR_GAMMA * DRY_AIR_GAS_CONSTANT_J_KG_K * self.temperature_k)

    @property
    def impedance_rayl(self) -> float:
        return self.density_kg_m3 * self.sound_speed_m_s

    @property
    def nonlinearity_coefficient(self) -> float:
        """beta = 1 + B/(2A); for an ideal diatomic gas B/A = gamma - 1."""

        return 1.0 + (DRY_AIR_GAMMA - 1.0) / 2.0


def iso9613_absorption_db_per_m(frequency_hz: float, air: Air = Air()) -> float:
    """Pure-tone atmospheric absorption coefficient in dB/m (ISO 9613-1)."""

    if frequency_hz <= 0:
        raise ValueError("frequency_hz must be > 0")
    f = float(frequency_hz)
    t = air.temperature_k
    pa_rel = air.pressure_pa / REFERENCE_PRESSURE_PA
    t_rel = t / REFERENCE_TEMPERATURE_K

    c_sat = -6.8346 * (TRIPLE_POINT_WATER_K / t) ** 1.261 + 4.6151
    psat_rel = 10.0**c_sat
    h = air.relative_humidity_pct * psat_rel / pa_rel  # molar water-vapour %

    fr_o = pa_rel * (24.0 + 4.04e4 * h * (0.02 + h) / (0.391 + h))
    fr_n = pa_rel * t_rel**-0.5 * (9.0 + 280.0 * h * exp(-4.170 * (t_rel ** (-1.0 / 3.0) - 1.0)))

    classical = 1.84e-11 / pa_rel * t_rel**0.5
    relax_o = 0.01275 * exp(-2239.1 / t) / (fr_o + f * f / fr_o)
    relax_n = 0.1068 * exp(-3352.0 / t) / (fr_n + f * f / fr_n)
    return 8.686 * f * f * (classical + t_rel**-2.5 * (relax_o + relax_n))


def absorption_power_transmission(frequency_hz: float, distance_m: float, air: Air = Air()) -> float:
    """Fraction of acoustic power surviving absorption over ``distance_m``."""

    if distance_m < 0:
        raise ValueError("distance_m must be >= 0")
    return 10.0 ** (-iso9613_absorption_db_per_m(frequency_hz, air) * distance_m / 10.0)


def spl_db_from_rms_pressure(p_rms_pa: float) -> float:
    """Sound pressure level re 20 uPa."""

    if p_rms_pa <= 0:
        raise ValueError("p_rms_pa must be > 0")
    return 20.0 * log10(p_rms_pa / 20e-6)
