"""Recording and replay (blueprint Stage 10, roadmap tasks 67-68, Branch 14).

Records a decision cycle's inputs, the rule versions active when it ran,
and the outputs actually produced, then replays a recorded cycle's inputs
through the *current* decision engine and safety supervisor to check
whether the outcome still matches what was recorded. A mismatch means
either the rules changed on purpose (compare rule_version) or a
regression was introduced -- this is what makes that distinction
reviewable instead of just trusted (Stage 10's core hazard: "Record
protocol and rule versions.").

Deliberately does not import from tests/ -- production code should not
depend on test helpers, even though the sensor-state reconstruction here
resembles tests/helpers.py's make_sensors().
"""
import json
from dataclasses import asdict, dataclass
from typing import List, Optional

from .canonical import SensorReading, SensorState, SourceMode
from .decision import DECISION_RULES_VERSION, evaluate_decision
from .safety import SAFETY_RULES_VERSION, evaluate_safety


@dataclass(frozen=True)
class RecordedCycle:
    """One recorded decision cycle: every input the decision engine and
    safety supervisor saw, tagged with the rule versions active at
    recording time (task 68), plus the outputs actually produced."""

    sequence: int
    decision_rules_version: str
    safety_rules_version: str

    temperature: Optional[float]
    soil_moisture: Optional[float]
    rain: Optional[float]
    water_level_percent: Optional[float]
    previous_pump_requested: bool
    tank_level_percent: Optional[float]
    emergency_stop: bool
    controller_fault: bool
    data_stale: bool
    is_startup: bool

    recorded_requested_fan: bool
    recorded_requested_window_deg: int
    recorded_requested_pump: bool
    recorded_commanded_fan: bool
    recorded_commanded_window_deg: int
    recorded_commanded_pump: bool
    recorded_alarm_level: str


@dataclass(frozen=True)
class ReplayMismatch:
    """One field where a replayed cycle's outcome disagrees with what was
    recorded."""

    sequence: int
    field: str
    recorded_value: object
    replayed_value: object


def _sensors_from_recorded(cycle: RecordedCycle, now_ms: int = 0) -> SensorState:
    state = SensorState()
    values = {
        "temperature": cycle.temperature,
        "soil_moisture": cycle.soil_moisture,
        "rain": cycle.rain,
        "water_level_percent": cycle.water_level_percent,
    }
    for name, value in values.items():
        if value is None:
            continue
        state.update(
            SensorReading(
                name=name, value=float(value), unit="", source=SourceMode.VIRTUAL, quality="good",
                received_at_ms=now_ms, valid=True,
            )
        )
    return state


def record_cycle(
    sequence: int,
    sensors: SensorState,
    previous_pump_requested: bool,
    tank_level_percent: Optional[float] = None,
    emergency_stop: bool = False,
    controller_fault: bool = False,
    data_stale: bool = False,
    is_startup: bool = False,
) -> RecordedCycle:
    """Roadmap task 67: runs one real decision cycle and records everything
    needed to replay it later."""
    decision = evaluate_decision(sensors, previous_pump_requested, decision_id=f"record-{sequence}")
    safety = evaluate_safety(
        decision, tank_level_percent, emergency_stop, controller_fault, data_stale, is_startup
    )
    return RecordedCycle(
        sequence=sequence,
        decision_rules_version=DECISION_RULES_VERSION,
        safety_rules_version=SAFETY_RULES_VERSION,
        temperature=sensors.value_of("temperature"),
        soil_moisture=sensors.value_of("soil_moisture"),
        rain=sensors.value_of("rain"),
        water_level_percent=sensors.value_of("water_level_percent"),
        previous_pump_requested=previous_pump_requested,
        tank_level_percent=tank_level_percent,
        emergency_stop=emergency_stop,
        controller_fault=controller_fault,
        data_stale=data_stale,
        is_startup=is_startup,
        recorded_requested_fan=decision.requested_fan,
        recorded_requested_window_deg=decision.requested_window_deg,
        recorded_requested_pump=decision.requested_pump,
        recorded_commanded_fan=safety.commanded_fan,
        recorded_commanded_window_deg=safety.commanded_window_deg,
        recorded_commanded_pump=safety.commanded_pump,
        recorded_alarm_level=safety.alarm_level,
    )


def replay_cycle(cycle: RecordedCycle) -> List[ReplayMismatch]:
    """Re-runs one recorded cycle's inputs through the *current* decision
    engine and safety supervisor and reports every field where the
    outcome now differs from what was recorded. An empty list means the
    rules produced byte-for-byte the same decision this time."""
    sensors = _sensors_from_recorded(cycle)
    decision = evaluate_decision(sensors, cycle.previous_pump_requested, decision_id=f"replay-{cycle.sequence}")
    safety = evaluate_safety(
        decision, cycle.tank_level_percent, cycle.emergency_stop, cycle.controller_fault, cycle.data_stale,
        cycle.is_startup,
    )

    checks = [
        ("requested_fan", cycle.recorded_requested_fan, decision.requested_fan),
        ("requested_window_deg", cycle.recorded_requested_window_deg, decision.requested_window_deg),
        ("requested_pump", cycle.recorded_requested_pump, decision.requested_pump),
        ("commanded_fan", cycle.recorded_commanded_fan, safety.commanded_fan),
        ("commanded_window_deg", cycle.recorded_commanded_window_deg, safety.commanded_window_deg),
        ("commanded_pump", cycle.recorded_commanded_pump, safety.commanded_pump),
        ("alarm_level", cycle.recorded_alarm_level, safety.alarm_level),
    ]
    return [
        ReplayMismatch(cycle.sequence, field, recorded_value, replayed_value)
        for field, recorded_value, replayed_value in checks
        if recorded_value != replayed_value
    ]


def replay_sequence(cycles: List[RecordedCycle]) -> List[ReplayMismatch]:
    """Replays a whole recorded sequence in order, returning every
    mismatch found across every cycle (not just the first)."""
    mismatches: List[ReplayMismatch] = []
    for cycle in cycles:
        mismatches.extend(replay_cycle(cycle))
    return mismatches


def save_recording(cycles: List[RecordedCycle], path: str) -> None:
    """Roadmap task 67: durable recording, one JSON object per line so a
    recording can be appended to incrementally and inspected with
    ordinary line-oriented tools."""
    with open(path, "w", encoding="utf-8") as handle:
        for cycle in cycles:
            handle.write(json.dumps(asdict(cycle)))
            handle.write("\n")


def load_recording(path: str) -> List[RecordedCycle]:
    cycles = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            cycles.append(RecordedCycle(**json.loads(line)))
    return cycles
