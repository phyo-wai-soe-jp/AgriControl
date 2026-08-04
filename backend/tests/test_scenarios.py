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
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple

import httpx
import pytest
from fastapi.testclient import TestClient

from backend import app as app_module
from backend.app import BridgeSession, EventLog
from logic.safety import SafetyPriority, evaluate_safety
from logic.decision import evaluate_decision
from tests.helpers import make_sensors

# Mirrors firmware/src/irrigation_slice.cpp's kTemperatureMinC/kTemperatureMaxC.
TEMPERATURE_MIN_C = -40.0
TEMPERATURE_MAX_C = 85.0


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
        if not (TEMPERATURE_MIN_C <= temperature <= TEMPERATURE_MAX_C):
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


def install_responder(monkeypatch, responder: Callable[[str, dict], Tuple[int, dict]]) -> None:
    def fake_post(url, json=None, timeout=None):
        request = httpx.Request("POST", url)
        status_code, payload = responder(url, json)
        return httpx.Response(status_code, json=payload, request=request)

    monkeypatch.setattr(app_module.httpx, "post", fake_post)


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


def test_communication_loss_returns_502_and_logs_event(client, monkeypatch):
    """Roadmap task 58's communication-loss scenario: the ESP is entirely
    unreachable (not just rejecting the message), matching
    backend/app.py's httpx.RequestError handling."""

    def fake_post(url, json=None, timeout=None):
        raise httpx.ConnectError("connection refused", request=httpx.Request("POST", url))

    monkeypatch.setattr(app_module.httpx, "post", fake_post)

    started = time.monotonic()
    response = client.post("/api/temperature", json={"temperature": 25.0})
    elapsed_s = time.monotonic() - started

    assert response.status_code == 502
    assert elapsed_s < 1.0, f"communication_loss exceeded its response-time budget: {elapsed_s:.3f}s"

    events = client.get("/api/events").json()
    codes = [e["code"] for e in events]
    assert "ESP_UNREACHABLE" in codes
