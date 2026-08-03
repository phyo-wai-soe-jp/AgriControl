"""System state machine (blueprint Stage 2, roadmap task 10, Branch 7).

Modeled as one explicit mode transition graph instead of independent boolean
flags, per the blueprint rule: "State changes must follow defined
transitions. Avoid disconnected Boolean flags that can create impossible
combinations."
"""
from dataclasses import dataclass, replace
from enum import Enum


class Mode(str, Enum):
    BOOT = "boot"
    CONNECTING = "connecting"
    READY = "ready"
    AUTOMATIC = "automatic"
    WARNING = "warning"
    SAFE = "safe"
    FAULT = "fault"
    RECOVERY = "recovery"


class CommunicationState(str, Enum):
    OFFLINE = "offline"
    CONNECTING = "connecting"
    ONLINE = "online"
    DATA_ACTIVE = "data_active"
    DATA_STALE = "data_stale"
    RECONNECTING = "reconnecting"


# Exactly the chain documented in the blueprint:
# BOOT -> CONNECTING -> READY -> AUTOMATIC -> WARNING/SAFE/FAULT -> RECOVERY -> AUTOMATIC
ALLOWED_MODE_TRANSITIONS = {
    Mode.BOOT: {Mode.CONNECTING},
    Mode.CONNECTING: {Mode.READY},
    Mode.READY: {Mode.AUTOMATIC},
    Mode.AUTOMATIC: {Mode.WARNING, Mode.SAFE, Mode.FAULT},
    Mode.WARNING: {Mode.RECOVERY},
    Mode.SAFE: {Mode.RECOVERY},
    Mode.FAULT: {Mode.RECOVERY},
    Mode.RECOVERY: {Mode.AUTOMATIC},
}


class InvalidModeTransition(ValueError):
    """Raised when a requested mode change is not part of the defined transition graph."""


@dataclass(frozen=True)
class SystemState:
    mode: Mode
    communication_state: CommunicationState
    alarm_level: str
    boot_id: str
    recovery_status: str = "idle"

    def transition_to(self, next_mode: Mode) -> "SystemState":
        if next_mode != self.mode and next_mode not in ALLOWED_MODE_TRANSITIONS.get(self.mode, set()):
            raise InvalidModeTransition(f"{self.mode.value} -> {next_mode.value} is not a defined transition")
        return replace(self, mode=next_mode)
