import pytest

from telek.control import IntentPolicy
from telek.model import GestureEvent, Vec3


def test_low_confidence_event_is_ignored() -> None:
    policy = IntentPolicy(min_confidence=0.9)
    event = GestureEvent("push", confidence=0.89)
    assert policy.command_for(event, target_id="cup", aim_unit=Vec3(1, 0, 0)) is None


def test_push_and_pull_have_opposite_sign() -> None:
    policy = IntentPolicy(max_command_force_n=2.0)
    push = policy.command_for(
        GestureEvent("push", confidence=0.99, strength=0.5),
        target_id="cup",
        aim_unit=Vec3(1, 0, 0),
    )
    pull = policy.command_for(
        GestureEvent("pull", confidence=0.99, strength=0.5),
        target_id="cup",
        aim_unit=Vec3(1, 0, 0),
    )
    assert push is not None and pull is not None
    assert push.force_n.x == pytest.approx(1.0)
    assert pull.force_n.x == pytest.approx(-1.0)


def test_non_unit_aim_is_rejected() -> None:
    policy = IntentPolicy()
    with pytest.raises(ValueError):
        policy.command_for(
            GestureEvent("push", confidence=1.0),
            target_id="cup",
            aim_unit=Vec3(2, 0, 0),
        )
