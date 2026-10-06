from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True, slots=True)
class Vec3:
    """Small immutable 3-D vector used by hardware-neutral command types."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    @property
    def magnitude(self) -> float:
        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def scaled(self, factor: float) -> "Vec3":
        return Vec3(self.x * factor, self.y * factor, self.z * factor)


@dataclass(frozen=True, slots=True)
class ForceCommand:
    """Desired physical effect, deliberately decoupled from actuator hardware."""

    target_id: str
    force_n: Vec3
    torque_nm: Vec3 = Vec3()
    hold: bool = False

    def __post_init__(self) -> None:
        if not self.target_id.strip():
            raise ValueError("target_id must not be empty")


@dataclass(frozen=True, slots=True)
class GestureEvent:
    """Semantic output of a future EMG/gesture recognizer."""

    gesture: str
    confidence: float
    strength: float = 1.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in [0, 1]")
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError("strength must be in [0, 1]")
        if not self.gesture.strip():
            raise ValueError("gesture must not be empty")
