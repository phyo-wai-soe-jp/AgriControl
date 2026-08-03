"""Actuator state (blueprint Stage 2, roadmap task 10, Branch 10: Actuator abstraction).

Keeps requested, commanded, simulated, measured, and fault evidence separate
so a command is never reported as the actual physical state without
feedback confirming it.
"""
from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class ActuatorState:
    name: str
    requested_state: Any
    commanded_state: Any
    simulated_state: Any = None
    measured_state: Any = None
    fault_state: Optional[str] = None
