"""Stage 8 scenario testing (roadmap tasks 58-60, Branch 13: Testing).

Exercises the FastAPI bridge end-to-end against a fake ESP that computes its
response with the *real*, host-tested decision engine and safety supervisor
(logic/decision.py, logic/safety.py) -- the same algorithm
firmware/include/decision.h, safety.h, and irrigation.h are a verified,
line-by-line port of -- rather than a hand-duplicated stand-in. Each
scenario's expected commands/mode/alarm therefore comes from proven logic,
not from guessing what the ESP "should" do.

This is bridge-side evidence only. response_time_budget_s is this suite's
own generous ceiling on the in-process bridge call, not a measurement of the
physical ESP's real round-trip time -- there is no board or network here.
Communication-loss and invalid-data handling are exercised at the bridge
protocol layer (502 + event log), matching what backend/app.py actually does
when the real ESP is unreachable or rejects a message.

The parametrized SCENARIOS below are single, independent readings and use
real_esp_responder() (is_startup/data_stale both fixed False -- already
"recovered"). test_recovery_requires_stable_valid_messages_through_the_bridge
is different: it uses real_esp_responder_with_recovery(), which tracks
SystemState/RecoveryTracker across a *sequence* of requests the way the
real ESP's SharedState does, to prove Gate A's "recovery requires stable
valid messages" through the actual bridge protocol path -- added
2026-08-05 after a real bug was found where the firmware's dataStale
input wasn't actually wired to this state at all.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple

import pytest
from fastapi.testclient import TestClient

from backend import app as app_module
from backend.app import BridgeSession, EventLog
from logic.protocol import (
    RECOVERY_CONSECUTIVE_VALID_REQUIRED,
    RecoveryTracker,
    evaluate_tick,
    is_data_stale_for_safety,
    is_valid_temperature_c,
)
from logic.safety import SafetyPriority, evaluate_safety
from logic.decision import evaluate_decision
from logic.system_state import CommunicationState, Mode, SystemState
from tests.helpers import make_sensors


@pytest.fixture(autouse=True)
def reset_bridge_state():
    app_module.session = BridgeSession()
    app_module.events = EventLog()
    yield


@pytest.fixture
def client():
    return TestClient(app_module.app)


def real_esp_responder(previous_pump_requested: bool = False) -> Callable[[str, dict], Tuple[int, dict]]:
    """A fake-ESP httpx.post responder built on the real decision engine and
    safety supervisor, not a re-implementation of their rules. Each scenario
    below is a single, independent reading (not the device's very first
    reading after boot), so is_startup is fixed False here rather than
    tracked -- that path is already covered by vertical_slice/irrigation_slice
    review and doesn't need re-proving per scenario.
    """
    state = {"previous_pump_requested": previous_pump_requested}

    def responder(url: str, payload: dict) -> Tuple[int, dict]:
        values = payload["values"]
        temperature = values["temperature"]
        if not is_valid_temperature_c(temperature):
            return 400, {"accepted": False, "error": "temperature out of range"}

        sensors = make_sensors(
            temperature=temperature,
            soil_moisture=values.get("soil_moisture"),
            rain=values.get("rain"),
            water_level_percent=values.get("water_level_percent"),
        )
        decision = evaluate_decision(sensors, state["previous_pump_requested"], decision_id=f"D{payload['sequence']}")
        safety = evaluate_safety(
            decision,
            tank_level_percent=values.get("water_level_percent"),
            is_startup=False,
        )
        state["previous_pump_requested"] = decision.requested_pump

        body = {
            "accepted": True,
            "sequence": payload["sequence"],
            "mode": "automatic" if safety.applied_priority == SafetyPriority.AUTOMATIC_OPERATION else "safety_override",
            "alarm_level": safety.alarm_level,
            "commands": {
                "fan": safety.commanded_fan,
                "window_angle": safety.commanded_window_deg,
                "pump": safety.commanded_pump,
            },
            "triggered_rules": decision.triggered_rules + safety.overrides,
            "reasons": decision.reasons,
        }
        return 200, body

    return responder


def real_esp_responder_with_recovery(initial_mode: Mode = Mode.AUTOMATIC) -> Callable[[str, dict], Tuple[int, dict]]:
    """Like real_esp_responder(), but also tracks SystemState/
    RecoveryTracker across calls the way the real ESP's SharedState does,
    using is_data_stale_for_safety() -- so a scenario can prove the bridge
    relays the ESP's real Gate-A "recovery requires stable valid
    messages" behavior across a *sequence* of requests, not just a single
    isolated reading like the other scenarios in this file.

    Starting in Mode.WARNING (with communication_state set to match, as
    the real SharedState always keeps them in sync) lets a test begin
    mid-recovery without needing to simulate real wall-clock staleness
    detection first -- staleness detection itself is already covered by
    tests/test_protocol.py's TestStaleness.
    """
    communication_state = (
        CommunicationState.DATA_STALE if initial_mode == Mode.WARNING else CommunicationState.DATA_ACTIVE
    )
    system_state = {
        "value": SystemState(
            mode=initial_mode, communication_state=communication_state, alarm_level="normal",
            boot_id="recovery-scenario",
        )
    }
    recovery = RecoveryTracker()
    previous_pump_requested = {"value": False}

    def responder(url: str, payload: dict) -> Tuple[int, dict]:
        values = payload["values"]
        temperature = values["temperature"]
        if not is_valid_temperature_c(temperature):
            return 400, {"accepted": False, "error": "temperature out of range"}

        # Mirrors SharedState::tick() running just before this message is
        # processed (any_stale=False: this scenario is about the recovery
        # streak, not about re-triggering staleness mid-test).
        tick_result = evaluate_tick(system_state["value"], recovery, any_stale=False)
        system_state["value"] = tick_result.system_state

        sensors = make_sensors(
            temperature=temperature, soil_moisture=values.get("soil_moisture"), rain=values.get("rain"),
            water_level_percent=values.get("water_level_percent"),
        )
        decision = evaluate_decision(
            sensors, previous_pump_requested["value"], decision_id=f"D{payload['sequence']}"
        )
        data_stale = is_data_stale_for_safety(system_state["value"].mode)
        safety = evaluate_safety(decision, tank_level_percent=values.get("water_level_percent"), data_stale=data_stale)
        previous_pump_requested["value"] = decision.requested_pump
        recovery.record_valid()

        body = {
            "accepted": True,
            "sequence": payload["sequence"],
            "mode": "automatic" if safety.applied_priority == SafetyPriority.AUTOMATIC_OPERATION else "safety_override",
            "alarm_level": safety.alarm_level,
            "commands": {
                "fan": safety.commanded_fan,
                "window_angle": safety.commanded_window_deg,
                "pump": safety.commanded_pump,
            },
            "triggered_rules": decision.triggered_rules + safety.overrides,
            "reasons": decision.reasons,
        }
        return 200, body

    return responder


def install_responder(monkeypatch, responder: Callable[[str, dict], Tuple[int, dict]]) -> None:
    """Installs `responder` as a fake ESP by monkeypatching mqtt_client.publish
    so a publish to SENSOR_TOPIC/FEEDBACK_TOPIC synchronously resolves the
    matching PendingResponses entry, standing in for the real MQTT round
    trip. Correlates on the *request's own* sequence/request_id (which the
    bridge already knows, having just sent it) rather than trusting the
    responder's reply to echo it back correctly -- the same thing the real
    ESP does, but not something a test fake should have to get right too.
    """

    def fake_publish(topic, payload_str, qos=1):
        payload = json.loads(payload_str)
        _, body = responder(topic, payload)
        if topic == app_module.SENSOR_TOPIC:
            app_module.sensor_responses.resolve(payload["sequence"], body)
        elif topic == app_module.FEEDBACK_TOPIC:
            app_module.feedback_responses.resolve(payload["request_id"], body)

    monkeypatch.setattr(app_module.mqtt_client, "publish", fake_publish)


@dataclass
class Scenario:
    """One roadmap-task-58 preset scenario plus roadmap-task-59's expected
    commands/mode/alarm/response-time budget. A field left as None is not
    checked -- e.g. invalid_data only checks the HTTP status, since the ESP
    never got far enough to compute commands."""

    name: str
    values: Dict[str, float]
    expect_status: int = 200
    expect_fan: Optional[bool] = None
    expect_window_angle: Optional[int] = None
    expect_pump: Optional[bool] = None
    expect_mode: Optional[str] = None
    expect_alarm_level: Optional[str] = None
    previous_pump_requested: bool = False
    response_time_budget_s: float = 1.0


SCENARIOS = [
    Scenario(
        name="normal",
        values={"temperature": 25.0, "soil_moisture": 50.0, "water_level_percent": 80.0, "rain": 0.0},
        expect_fan=False,
        expect_window_angle=10,
        expect_pump=False,
        expect_mode="automatic",
        expect_alarm_level="normal",
    ),
    Scenario(
        name="hot",
        values={"temperature": 40.0, "soil_moisture": 50.0, "water_level_percent": 80.0, "rain": 0.0},
        expect_fan=True,
        expect_window_angle=170,
        expect_pump=False,
        expect_mode="automatic",
        expect_alarm_level="normal",
    ),
    Scenario(
        name="dry_soil",
        values={"temperature": 25.0, "soil_moisture": 20.0, "water_level_percent": 80.0, "rain": 0.0},
        expect_fan=False,
        expect_window_angle=10,
        expect_pump=True,
        expect_mode="automatic",
        expect_alarm_level="normal",
    ),
    Scenario(
        name="low_tank",
        # Same dry soil as above (decision engine still requests the pump
        # on), but the tank is below the 15% equipment-protection threshold
        # -- the safety supervisor must force the pump off despite the
        # request, per logic/safety.py's EQUIPMENT_PROTECTION tier.
        values={"temperature": 25.0, "soil_moisture": 20.0, "water_level_percent": 10.0, "rain": 0.0},
        expect_fan=False,
        expect_window_angle=10,
        expect_pump=False,
        expect_mode="safety_override",
        expect_alarm_level="warning",
    ),
    Scenario(
        name="rain",
        # Dry soil that would otherwise trigger the pump, but rain=1 blocks
        # the pump-on rule (logic/decision.py's IRRIGATION-001 requires
        # rain_value == 0); pump holds its previous (False) state instead.
        values={"temperature": 25.0, "soil_moisture": 20.0, "water_level_percent": 80.0, "rain": 1.0},
        expect_fan=False,
        expect_window_angle=10,
        expect_pump=False,
        expect_mode="automatic",
        expect_alarm_level="normal",
    ),
    Scenario(
        name="invalid_data",
        # Physically implausible temperature -- the ESP itself rejects it
        # (matching irrigation_slice.cpp's range check), so the bridge
        # relays that as a 502 (backend/app.py's ESP_REJECTED path).
        values={"temperature": 999.0},
        expect_status=502,
    ),
]


@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s.name for s in SCENARIOS])
def test_scenario(client, monkeypatch, scenario: Scenario):
    """Roadmap tasks 58-60: run a preset scenario end-to-end through the
    bridge and automatically compare the outcome to its expected commands/
    mode/alarm/status/response-time. The assert calls below *are* the
    automatic PASS/FAIL comparison -- pytest reports each scenario id as
    passed or failed on its own."""
    install_responder(monkeypatch, real_esp_responder(previous_pump_requested=scenario.previous_pump_requested))

    started = time.monotonic()
    response = client.post("/api/temperature", json=scenario.values)
    elapsed_s = time.monotonic() - started

    assert response.status_code == scenario.expect_status, scenario.name
    assert elapsed_s < scenario.response_time_budget_s, (
        f"{scenario.name} exceeded its response-time budget: {elapsed_s:.3f}s"
    )

    if scenario.expect_status != 200:
        return

    body = response.json()
    if scenario.expect_fan is not None:
        assert body["commands"]["fan"] == scenario.expect_fan, scenario.name
    if scenario.expect_window_angle is not None:
        assert body["commands"]["window_angle"] == scenario.expect_window_angle, scenario.name
    if scenario.expect_pump is not None:
        assert body["commands"]["pump"] == scenario.expect_pump, scenario.name
    if scenario.expect_mode is not None:
        assert body["mode"] == scenario.expect_mode, scenario.name
    if scenario.expect_alarm_level is not None:
        assert body["alarm_level"] == scenario.expect_alarm_level, scenario.name


def test_recovery_requires_stable_valid_messages_through_the_bridge(client, monkeypatch):
    """Gate A ("Recovery requires stable valid messages"), proven through
    the real bridge protocol path -- not just logic/ in isolation like
    tests/test_protocol.py's TestFullRecoveryGatingIntegration, and not
    just live hardware like the 2026-08-05 session that found this bug.
    Starts mid-recovery (Mode.WARNING) and sends a sequence of otherwise
    identical readings through /api/temperature, confirming the bridge
    relays safety_override for exactly RECOVERY_CONSECUTIVE_VALID_REQUIRED
    messages before automatic resumes on the next one -- this is the
    scenario Stage 8's original suite never modeled, since its fake ESP
    never tracked staleness/recovery at all.
    """
    install_responder(monkeypatch, real_esp_responder_with_recovery(initial_mode=Mode.WARNING))
    payload = {"temperature": 25.0, "soil_moisture": 50.0, "water_level_percent": 80.0, "rain": 0.0}

    for i in range(RECOVERY_CONSECUTIVE_VALID_REQUIRED):
        response = client.post("/api/temperature", json=payload)
        assert response.status_code == 200
        assert response.json()["mode"] == "safety_override", (
            f"message {i + 1}: resumed automatic too early"
        )

    response = client.post("/api/temperature", json=payload)
    assert response.status_code == 200
    assert response.json()["mode"] == "automatic"


def test_communication_loss_returns_502_and_logs_event(client, monkeypatch):
    """Roadmap task 58's communication-loss scenario: the ESP is entirely
    unreachable. Over MQTT this isn't a connection exception at publish
    time (a publish to a connected broker essentially always succeeds) --
    the real failure mode is silence: nothing ever arrives on
    STATE_TOPIC, and the bridge's own wait_for() timeout is what surfaces
    it as 502/ESP_UNREACHABLE. Simulated here by a fake publish() that
    does nothing, with the timeout shortened so the test doesn't have to
    actually wait out the real multi-second default."""
    monkeypatch.setattr(app_module, "MQTT_RESPONSE_TIMEOUT_SECONDS", 0.05)
    monkeypatch.setattr(app_module.mqtt_client, "publish", lambda topic, payload_str, qos=1: None)

    started = time.monotonic()
    response = client.post("/api/temperature", json={"temperature": 25.0})
    elapsed_s = time.monotonic() - started

    assert response.status_code == 502
    assert elapsed_s < 1.0, f"communication_loss exceeded its response-time budget: {elapsed_s:.3f}s"

    events = client.get("/api/events").json()
    codes = [e["code"] for e in events]
    assert "ESP_UNREACHABLE" in codes
