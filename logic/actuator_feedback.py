"""Closed-loop actuator feedback simulation and mismatch detection
(blueprint Stage 9, roadmap tasks 61-66, Branch 10: Actuator abstraction).

logic/actuator_state.py already separates requested/commanded/simulated/
measured/fault state so a command is never reported as physical truth
without feedback confirming it -- this module is what actually produces
that feedback and detects when it disagrees with the command, which is
Stage 9's core hazard ("Commanded state is not measured state.").

Detected faults are returned as explicit string codes (never silently
folded into a boolean) and are meant to be passed into
logic/safety.py's evaluate_safety(controller_fault=True) by the caller
(roadmap task 66) rather than handled inside safety.py itself, so the
already-verified safety supervisor does not need to change shape for this.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .actuator_state import ActuatorState

# Roadmap task 62: default virtual actuator startup delay -- a relay/motor
# does not reach its commanded state instantly. Not a hardware
# measurement (no board here); a placeholder pending owner confirmation,
# like the other simulated timing constants in this codebase.
STARTUP_DELAY_MS = 500

# Roadmap task 65: injected servo mismatch magnitude for the WRONG_POSITION
# fault mode -- large enough to be unambiguously not the commanded angle,
# clamped to the servo's 0-180 range.
WRONG_POSITION_OFFSET_DEG = 15


class FaultMode(str, Enum):
    """Injectable simulated-actuator fault modes (roadmap tasks 63-65)."""

    NONE = "none"
    FAILED_STARTUP = "failed_startup"
    STUCK_ON = "stuck_on"
    STUCK_OFF = "stuck_off"
    WRONG_POSITION = "wrong_position"


@dataclass(frozen=True)
class BinaryFeedback:
    """Simulated feedback for an on/off actuator (fan, pump)."""

    measured_state: bool
    fault_code: Optional[str]


@dataclass(frozen=True)
class ServoFeedback:
    """Simulated feedback for the window servo's angle."""

    measured_deg: int
    fault_code: Optional[str]


def simulate_binary_actuator(
    commanded_state: bool,
    elapsed_since_command_ms: int,
    fault_mode: FaultMode = FaultMode.NONE,
    startup_delay_ms: int = STARTUP_DELAY_MS,
) -> BinaryFeedback:
    """Simulates fan/pump feedback for one commanded state.

    - NONE: reports the commanded ON state only after startup_delay_ms has
      elapsed (task 62); before that it reports OFF, which is not itself a
      fault -- the actuator just hasn't caught up yet. OFF commands are
      always reported immediately (nothing to wait for).
    - FAILED_STARTUP: an ON command never actually turns the actuator on;
      it keeps reporting OFF and faults (task 63). OFF commands still
      succeed -- there is nothing to fail about turning something off.
    - STUCK_ON / STUCK_OFF: always reports a fixed measured state
      regardless of command (task 64). This only surfaces as a fault once
      the fixed state actually disagrees with what was commanded -- a
      relay stuck on looks fine right up until you try to turn it off.
    """
    if fault_mode == FaultMode.STUCK_ON:
        fault = "ACTUATOR-STUCK-ON" if not commanded_state else None
        return BinaryFeedback(True, fault)
    if fault_mode == FaultMode.STUCK_OFF:
        fault = "ACTUATOR-STUCK-OFF" if commanded_state else None
        return BinaryFeedback(False, fault)
    if fault_mode == FaultMode.FAILED_STARTUP and commanded_state:
        return BinaryFeedback(False, "ACTUATOR-FAILED-STARTUP")

    if commanded_state and elapsed_since_command_ms < startup_delay_ms:
        return BinaryFeedback(False, None)
    return BinaryFeedback(commanded_state, None)


def simulate_servo_actuator(
    commanded_deg: int,
    fault_mode: FaultMode = FaultMode.NONE,
    wrong_position_offset_deg: int = WRONG_POSITION_OFFSET_DEG,
) -> ServoFeedback:
    """Simulates window-servo feedback for one commanded angle (task 65).

    WRONG_POSITION reports an offset angle that disagrees with the
    command -- standing in for mechanical slip or binding, not a timing
    issue, so no startup delay applies here the way it does for the
    binary actuators.
    """
    if fault_mode == FaultMode.WRONG_POSITION:
        measured = max(0, min(180, commanded_deg + wrong_position_offset_deg))
        return ServoFeedback(measured, "ACTUATOR-WRONG-POSITION")
    return ServoFeedback(commanded_deg, None)


def detect_mismatch(commanded_state, measured_state, fault_code: Optional[str] = None) -> Optional[str]:
    """Roadmap task 61's mismatch check, factored out from the simulators
    above so any feedback source (simulated now, a real sensor once the
    board exists) can reuse the same detection rule. An explicit
    fault_code from the source always wins; otherwise any disagreement
    between commanded and measured state is itself a fault -- never
    silently assumed to be equal (Stage 9's core hazard).
    """
    if fault_code is not None:
        return fault_code
    if commanded_state != measured_state:
        return "ACTUATOR-MISMATCH"
    return None


def to_actuator_state(name: str, requested_state, commanded_state, measured_state, fault_code: Optional[str]) -> ActuatorState:
    """Builds an ActuatorState record from simulated feedback (roadmap
    task 61). Only simulated_state is populated here, not measured_state
    -- this is Stage 9's closed-loop *simulation*, not a real sensor
    reading, and logic/actuator_state.py's docstring is explicit that the
    two must stay distinct until real feedback exists (Stage 11: physical
    migration).
    """
    return ActuatorState(
        name=name,
        requested_state=requested_state,
        commanded_state=commanded_state,
        simulated_state=measured_state,
        measured_state=None,
        fault_state=fault_code,
    )
