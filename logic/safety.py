"""Safety supervisor (blueprint Stage 2, roadmap task 12, Branch 9).

Has final authority over every actuator command. Applies the blueprint's
documented safe-state matrix in the documented priority order (Emergency >
Safety > Equipment protection > Automatic operation). Only narrows or
overrides decision engine output -- it never recomputes requested actions.

Two "safe angle" / "configured safe state" values are left as caller-supplied
defaults because the blueprint names them without giving numbers:
- SAFE_WINDOW_DEG defaults to the documented closed angle (10 deg), which
  matches the blueprint's own startup default.
- configured_safe_fan_state defaults to off, the conservative choice when a
  concrete equipment-safe fan behavior has not been specified by the owner.
Both are explicit parameters, not hidden guesses, so a future agent or the
owner can override them once real requirements are confirmed.
"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from .decision import Decision, WINDOW_CLOSED_DEG

SAFE_WINDOW_DEG = WINDOW_CLOSED_DEG
LOW_TANK_THRESHOLD_PERCENT = 15.0


class SafetyPriority(str, Enum):
    EMERGENCY = "emergency"
    SAFETY = "safety"
    EQUIPMENT_PROTECTION = "equipment_protection"
    AUTOMATIC_OPERATION = "automatic_operation"


@dataclass(frozen=True)
class SafetyResult:
    commanded_pump: bool
    commanded_fan: bool
    commanded_window_deg: int
    alarm_level: str
    applied_priority: SafetyPriority
    overrides: List[str]


def evaluate_safety(
    decision: Decision,
    tank_level_percent: Optional[float],
    emergency_stop: bool = False,
    controller_fault: bool = False,
    data_stale: bool = False,
    is_startup: bool = False,
    configured_safe_fan_state: bool = False,
) -> SafetyResult:
    if emergency_stop:
        return SafetyResult(
            commanded_pump=False,
            commanded_fan=False,
            commanded_window_deg=SAFE_WINDOW_DEG,
            alarm_level="critical",
            applied_priority=SafetyPriority.EMERGENCY,
            overrides=["EMERGENCY-STOP"],
        )

    if controller_fault:
        return SafetyResult(
            commanded_pump=False,
            commanded_fan=configured_safe_fan_state,
            commanded_window_deg=SAFE_WINDOW_DEG,
            alarm_level="critical",
            applied_priority=SafetyPriority.SAFETY,
            overrides=["CONTROLLER-FAULT"],
        )

    if data_stale:
        return SafetyResult(
            commanded_pump=False,
            commanded_fan=configured_safe_fan_state,
            commanded_window_deg=SAFE_WINDOW_DEG,
            alarm_level="warning",
            applied_priority=SafetyPriority.SAFETY,
            overrides=["DATA-STALE"],
        )

    if is_startup:
        return SafetyResult(
            commanded_pump=False,
            commanded_fan=False,
            commanded_window_deg=WINDOW_CLOSED_DEG,
            alarm_level="startup_indication",
            applied_priority=SafetyPriority.SAFETY,
            overrides=["STARTUP"],
        )

    if tank_level_percent is not None and tank_level_percent < LOW_TANK_THRESHOLD_PERCENT:
        return SafetyResult(
            commanded_pump=False,
            commanded_fan=decision.requested_fan,
            commanded_window_deg=decision.requested_window_deg,
            alarm_level="warning",
            applied_priority=SafetyPriority.EQUIPMENT_PROTECTION,
            overrides=["LOW-TANK"] if decision.requested_pump else [],
        )

    return SafetyResult(
        commanded_pump=decision.requested_pump,
        commanded_fan=decision.requested_fan,
        commanded_window_deg=decision.requested_window_deg,
        alarm_level="normal",
        applied_priority=SafetyPriority.AUTOMATIC_OPERATION,
        overrides=[],
    )
