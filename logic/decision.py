"""Stateful decision engine (blueprint Stage 2, roadmap task 11, Branch 8).

Calculates requested actuator actions under normal, valid conditions from
canonical sensor state. Never touches GPIO, PWM, OLED, Wi-Fi, HTTP, or
browser APIs, and never applies safety overrides -- that is the safety
supervisor's job (logic/safety.py), kept in a separate module on purpose.

Tank-level gating for the pump is intentionally NOT part of this module. The
blueprint's own worked conflict example ("Decision engine: dry soil -> pump
ON. Safety supervisor: tank below 15% -> pump OFF.") shows the decision
engine requesting the pump on from soil/rain conditions alone, with the tank
threshold enforced downstream by the safety supervisor. Implementing it here
too would duplicate a safety-supervisor responsibility inside the decision
engine.
"""
from dataclasses import dataclass
from typing import List

from .canonical import SensorState

FAN_OFF = False
FAN_ON = True

WINDOW_CLOSED_DEG = 10
WINDOW_HALF_DEG = 90
WINDOW_OPEN_DEG = 170

MOISTURE_PUMP_ON_BELOW = 30.0
MOISTURE_PUMP_OFF_ABOVE = 40.0

TEMP_FAN_ON_ABOVE = 28.0
TEMP_WINDOW_FULL_ABOVE = 35.0


@dataclass(frozen=True)
class Decision:
    decision_id: str
    requested_fan: bool
    requested_window_deg: int
    requested_pump: bool
    triggered_rules: List[str]
    reasons: List[str]


def evaluate_decision(sensors: SensorState, previous_pump_requested: bool, decision_id: str) -> Decision:
    triggered_rules: List[str] = []
    reasons: List[str] = []

    temperature = sensors.value_of("temperature")
    moisture = sensors.value_of("soil_moisture")
    rain_value = sensors.value_of("rain")

    if temperature is None:
        fan = FAN_OFF
        window_deg = WINDOW_CLOSED_DEG
        reasons.append("Temperature reading unavailable; holding closed/off state")
    elif temperature <= TEMP_FAN_ON_ABOVE:
        fan = FAN_OFF
        window_deg = WINDOW_CLOSED_DEG
        triggered_rules.append("TEMPERATURE-001")
        reasons.append(f"Temperature {temperature} C is at or below {TEMP_FAN_ON_ABOVE} C")
    elif temperature <= TEMP_WINDOW_FULL_ABOVE:
        fan = FAN_ON
        window_deg = WINDOW_HALF_DEG
        triggered_rules.append("TEMPERATURE-002")
        reasons.append(f"Temperature {temperature} C is above {TEMP_FAN_ON_ABOVE} C")
    else:
        fan = FAN_ON
        window_deg = WINDOW_OPEN_DEG
        triggered_rules.append("TEMPERATURE-003")
        reasons.append(f"Temperature {temperature} C is above {TEMP_WINDOW_FULL_ABOVE} C")

    if moisture is None or rain_value is None:
        pump = previous_pump_requested
        reasons.append("Soil moisture or rain reading unavailable; holding previous pump state")
    elif moisture < MOISTURE_PUMP_ON_BELOW and rain_value == 0:
        pump = True
        triggered_rules.append("IRRIGATION-001")
        reasons.append(f"Soil moisture {moisture}% is below {MOISTURE_PUMP_ON_BELOW}% and no rain is detected")
    elif moisture > MOISTURE_PUMP_OFF_ABOVE:
        pump = False
        triggered_rules.append("IRRIGATION-002")
        reasons.append(f"Soil moisture {moisture}% is above {MOISTURE_PUMP_OFF_ABOVE}%")
    else:
        pump = previous_pump_requested
        triggered_rules.append("IRRIGATION-003")
        reasons.append(
            f"Soil moisture {moisture}% is between {MOISTURE_PUMP_ON_BELOW}% and "
            f"{MOISTURE_PUMP_OFF_ABOVE}%; holding previous pump state"
        )

    return Decision(
        decision_id=decision_id,
        requested_fan=fan,
        requested_window_deg=window_deg,
        requested_pump=pump,
        triggered_rules=triggered_rules,
        reasons=reasons,
    )
