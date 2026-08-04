"""Protocol validation, staleness detection, and recovery tracking
(blueprint Stage 4/5, roadmap tasks 25/27/28/38/39/40, Branches 4:
Protocol, 7: State management).

Mirrors firmware/include/canonical.h's isStale, firmware/include/
system_state.h's RecoveryTracker, and firmware/include/shared_state.h's
SharedState::tick() (plus the sequence/temperature validation duplicated
inline across firmware/src/runtime.cpp, vertical_slice.cpp, and
irrigation_slice.cpp) in pure Python -- so the underlying algorithm can be
proven correct on the host, the same way logic/decision.py and
logic/safety.py are proven before their C++ ports.
"""
from dataclasses import dataclass, replace
from typing import List

from .system_state import CommunicationState, Mode, SystemState

# Roadmap task 28: consecutive valid messages required before recovery
# completes and the system returns to AUTOMATIC. Tunable runtime parameter,
# not a hardware fact -- mirrors kRecoveryConsecutiveValidRequired in
# firmware/include/system_state.h.
RECOVERY_CONSECUTIVE_VALID_REQUIRED = 5

# Roadmap task 27: data-staleness timeout. Mirrors kDataStaleTimeoutMs.
DATA_STALE_TIMEOUT_MS = 10000

# Roadmap task 39: physically plausible temperature range. Mirrors
# kTemperatureMinC/kTemperatureMaxC, currently duplicated per-file across
# firmware/src/vertical_slice.cpp and irrigation_slice.cpp rather than
# centralized in a shared header. Not a hardware fact -- a placeholder
# pending owner confirmation, like the other tuning constants in this
# codebase.
TEMPERATURE_MIN_C = -40.0
TEMPERATURE_MAX_C = 85.0


class RecoveryTracker:
    """Roadmap task 28: recovery logic. Call record_valid()/record_failure()
    as messages are validated; stable_communication_confirmed() reports
    whether enough consecutive valid messages have arrived to leave
    RECOVERY. Mutable by design, matching the C++ original -- this is a
    running counter, not a value type like the other logic/ structures.
    """

    def __init__(self) -> None:
        self._consecutive_valid = 0

    def record_failure(self) -> None:
        self._consecutive_valid = 0

    def record_valid(self) -> None:
        if self._consecutive_valid < RECOVERY_CONSECUTIVE_VALID_REQUIRED:
            self._consecutive_valid += 1

    def stable_communication_confirmed(self) -> bool:
        return self._consecutive_valid >= RECOVERY_CONSECUTIVE_VALID_REQUIRED

    @property
    def consecutive_valid(self) -> int:
        return self._consecutive_valid


def is_stale(reading_age_ms: int, timeout_ms: int = DATA_STALE_TIMEOUT_MS) -> bool:
    """Roadmap task 27: a reading is stale once its age exceeds timeout_ms.
    Mirrors SensorState::isStale in firmware/include/canonical.h. Takes an
    already-computed age (see SensorReading.age_ms in logic/canonical.py)
    rather than a reading plus now_ms, so it composes with any reading
    source, not just logic.canonical.SensorState.
    """
    return reading_age_ms > timeout_ms


def is_valid_sequence(sequence: int, last_sequence: int, have_sequence: bool) -> bool:
    """Roadmap task 38: rejects duplicate or out-of-order sequence numbers.
    Mirrors the check duplicated across firmware/src/runtime.cpp,
    vertical_slice.cpp, and irrigation_slice.cpp's handleSensorPost():
    `shared.haveSequence && sequence <= shared.lastSequence -> reject`.
    A gap (sequence jumping ahead by more than 1) is still valid -- only
    non-increasing sequence numbers are rejected.
    """
    if have_sequence and sequence <= last_sequence:
        return False
    return True


def is_valid_temperature_c(value: float) -> bool:
    """Roadmap task 39: physically plausible temperature range check,
    mirroring the ESP's own validation (irrigation_slice.cpp's inRange()
    call) -- values outside this range never reach the decision engine.
    """
    return TEMPERATURE_MIN_C <= value <= TEMPERATURE_MAX_C


@dataclass(frozen=True)
class TickResult:
    """The outcome of one evaluate_tick() call: the (possibly updated)
    system state plus any event codes that would be logged this tick."""

    system_state: SystemState
    events: List[str]


def evaluate_tick(system_state: SystemState, recovery: RecoveryTracker, any_stale: bool) -> TickResult:
    """Roadmap tasks 27/28/40: one call mirrors
    firmware/include/shared_state.h's SharedState::tick() -- detects
    staleness and advances recovery/mode transitions. `recovery` is
    mutated in place (record_failure()), matching the C++ original's
    side-effecting tracker; record_valid() is *not* called here, the same
    as the C++ original -- that happens separately, once per successfully
    validated message, not once per tick.
    """
    events: List[str] = []
    state = system_state

    if any_stale:
        if state.communication_state != CommunicationState.DATA_STALE:
            state = replace(state, communication_state=CommunicationState.DATA_STALE)
            events.append("DATA_STALE")
            recovery.record_failure()
            if state.mode == Mode.AUTOMATIC:
                state = state.transition_to(Mode.WARNING)
    elif state.communication_state == CommunicationState.DATA_STALE:
        state = replace(state, communication_state=CommunicationState.DATA_ACTIVE)
        if state.mode == Mode.WARNING:
            state = state.transition_to(Mode.RECOVERY)
            events.append("RECOVERY_START")

    if state.mode == Mode.RECOVERY and recovery.stable_communication_confirmed():
        events.append("RECOVERED")
        state = state.transition_to(Mode.AUTOMATIC)

    return TickResult(system_state=state, events=events)
