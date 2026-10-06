"""Hardware-neutral mapping from deliberate gesture events to force semantics."""

from __future__ import annotations

from dataclasses import dataclass

from .model import ForceCommand, GestureEvent, Vec3


@dataclass(frozen=True, slots=True)
class IntentPolicy:
    """Conservative gate for future EMG classifiers.

    This is intentionally simple. A real system should add temporal confirmation,
    out-of-distribution detection, and an independent physical safety interlock.
    """

    min_confidence: float = 0.90
    max_command_force_n: float = 1.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.min_confidence <= 1.0:
            raise ValueError("min_confidence must be in [0, 1]")
        if self.max_command_force_n <= 0:
            raise ValueError("max_command_force_n must be > 0")

    def command_for(
        self,
        event: GestureEvent,
        *,
        target_id: str,
        aim_unit: Vec3,
    ) -> ForceCommand | None:
        """Translate a small semantic gesture vocabulary into a force command.

        ``aim_unit`` is supplied by a separate targeting/tracking layer. The
        caller is responsible for providing a normalized direction.
        """

        if event.confidence < self.min_confidence:
            return None
        mag = aim_unit.magnitude
        if abs(mag - 1.0) > 1e-6:
            raise ValueError("aim_unit must have magnitude 1")

        force = self.max_command_force_n * event.strength
        gesture = event.gesture.lower().strip()
        if gesture == "push":
            vector = aim_unit.scaled(force)
            return ForceCommand(target_id=target_id, force_n=vector)
        if gesture == "pull":
            vector = aim_unit.scaled(-force)
            return ForceCommand(target_id=target_id, force_n=vector)
        if gesture == "hold":
            return ForceCommand(target_id=target_id, force_n=Vec3(), hold=True)
        if gesture == "release":
            return ForceCommand(target_id=target_id, force_n=Vec3(), hold=False)
        return None
