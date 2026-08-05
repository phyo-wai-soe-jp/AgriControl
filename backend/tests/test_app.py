"""Tests for the FastAPI bridge (roadmap tasks 41, 42, 47, 48, and the
Stage 7 irrigation fields added to /api/temperature: 49-51).

Runs entirely on the host -- no physical ESP needed. httpx.post is
monkeypatched to a fake ESP so these tests are fast, deterministic, and
don't depend on network or hardware availability. This is the one part of
AgriControl's Stage 4-7 work that can be genuinely executed and verified
from this environment, unlike the firmware (no PlatformIO toolchain here).
"""
from __future__ import annotations

import httpx
import pytest
from fastapi.testclient import TestClient

from backend import app as app_module
from backend.app import BridgeSession, EventLog


@pytest.fixture(autouse=True)
def reset_bridge_state():
    """Each test gets a fresh session and event log, matching what a real
    process restart would give (see BridgeSession's docstring)."""
    app_module.session = BridgeSession()
    app_module.events = EventLog()
    yield


@pytest.fixture
def client():
    return TestClient(app_module.app)


def fake_esp_decision(temperature: float) -> dict:
    """Mirrors firmware/include/decision.h's thresholds, standing in for a
    real ESP response."""
    if temperature <= 28:
        fan, window = False, 10
    elif temperature <= 35:
        fan, window = True, 90
    else:
        fan, window = True, 170
    return {"fan": fan, "window_angle": window}


def install_fake_esp(monkeypatch, responder):
    """Replaces httpx.post (as used inside backend/app.py) with a fake
    that never touches the network."""

    def fake_post(url, json=None, timeout=None):
        request = httpx.Request("POST", url)
        status_code, payload = responder(url, json)
        return httpx.Response(status_code, json=payload, request=request)

    monkeypatch.setattr(app_module.httpx, "post", fake_post)


class TestHealth:
    def test_health_reports_ok_and_session_id(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["session_id"] == app_module.session.session_id


class TestForwardTemperature:
    def test_forwards_correct_protocol_shape_to_esp(self, client, monkeypatch):
        captured = {}

        def responder(url, payload):
            captured["url"] = url
            captured["payload"] = payload
            return 200, {"accepted": True, "sequence": payload["sequence"], "commands": fake_esp_decision(payload["values"]["temperature"])}

        install_fake_esp(monkeypatch, responder)

        response = client.post("/api/temperature", json={"temperature": 40.0})
        assert response.status_code == 200
        assert captured["url"] == f"{app_module.ESP_BASE_URL}/sensor"
        assert captured["payload"]["values"] == {"temperature": 40.0}
        assert captured["payload"]["session_id"] == app_module.session.session_id
        assert captured["payload"]["sequence"] == 1

    def test_sequence_increments_across_calls(self, client, monkeypatch):
        def responder(url, payload):
            return 200, {"accepted": True, "sequence": payload["sequence"], "commands": fake_esp_decision(payload["values"]["temperature"])}

        install_fake_esp(monkeypatch, responder)

        first = client.post("/api/temperature", json={"temperature": 20.0})
        second = client.post("/api/temperature", json={"temperature": 30.0})
        third = client.post("/api/temperature", json={"temperature": 40.0})

        assert first.json()["sequence"] == 1
        assert second.json()["sequence"] == 2
        assert third.json()["sequence"] == 3

    def test_relays_esp_response_body_unchanged(self, client, monkeypatch):
        esp_body = {
            "accepted": True,
            "sequence": 1,
            "mode": "automatic",
            "alarm_level": "normal",
            "commands": {"fan": True, "window_angle": 170},
            "triggered_rules": ["TEMPERATURE-003"],
            "reasons": ["Temperature 40.0 C is above 35.0 C"],
        }

        install_fake_esp(monkeypatch, lambda url, payload: (200, esp_body))

        response = client.post("/api/temperature", json={"temperature": 40.0})
        assert response.status_code == 200
        assert response.json() == esp_body

    def test_esp_unreachable_returns_502_and_logs_event(self, client, monkeypatch):
        def fake_post(url, json=None, timeout=None):
            raise httpx.ConnectError("connection refused", request=httpx.Request("POST", url))

        monkeypatch.setattr(app_module.httpx, "post", fake_post)

        response = client.post("/api/temperature", json={"temperature": 25.0})
        assert response.status_code == 502
        assert "Could not reach ESP" in response.json()["detail"]

        events = client.get("/api/events").json()
        codes = [e["code"] for e in events]
        assert "ESP_UNREACHABLE" in codes
        assert "SENT" in codes

    def test_esp_rejection_returns_502_and_logs_event(self, client, monkeypatch):
        install_fake_esp(monkeypatch, lambda url, payload: (400, {"accepted": False, "error": "temperature out of range"}))

        response = client.post("/api/temperature", json={"temperature": 999.0})
        assert response.status_code == 502
        assert "ESP rejected the message" in response.json()["detail"]

        events = client.get("/api/events").json()
        codes = [e["code"] for e in events]
        assert "ESP_REJECTED" in codes

    def test_missing_temperature_field_is_rejected_before_forwarding(self, client, monkeypatch):
        calls = []
        install_fake_esp(monkeypatch, lambda url, payload: calls.append(payload) or (200, {}))

        response = client.post("/api/temperature", json={})
        assert response.status_code == 422  # FastAPI/pydantic validation error
        assert calls == []  # never reached the (fake) ESP


class TestIrrigationFields:
    """Roadmap tasks 49-51: soil moisture, tank level, and rain forwarded
    alongside temperature, matching firmware/include/irrigation.h /
    firmware/src/irrigation_slice.cpp's optional-field handling."""

    def test_temperature_only_omits_irrigation_keys(self, client, monkeypatch):
        captured = {}
        install_fake_esp(
            monkeypatch,
            lambda url, payload: captured.update(payload)
            or (200, {"accepted": True, "sequence": payload["sequence"], "commands": {}}),
        )

        client.post("/api/temperature", json={"temperature": 25.0})
        assert captured["values"] == {"temperature": 25.0}
        assert "soil_moisture" not in captured["values"]
        assert "water_level_percent" not in captured["values"]
        assert "rain" not in captured["values"]

    def test_all_four_fields_forwarded_together(self, client, monkeypatch):
        captured = {}
        install_fake_esp(
            monkeypatch,
            lambda url, payload: captured.update(payload)
            or (200, {"accepted": True, "sequence": payload["sequence"], "commands": {}}),
        )

        client.post(
            "/api/temperature",
            json={"temperature": 20.0, "soil_moisture": 22.5, "water_level_percent": 60.0, "rain": 0},
        )
        assert captured["values"] == {
            "temperature": 20.0,
            "soil_moisture": 22.5,
            "water_level_percent": 60.0,
            "rain": 0.0,
        }

    def test_partial_irrigation_fields_only_forwards_what_was_sent(self, client, monkeypatch):
        captured = {}
        install_fake_esp(
            monkeypatch,
            lambda url, payload: captured.update(payload)
            or (200, {"accepted": True, "sequence": payload["sequence"], "commands": {}}),
        )

        client.post("/api/temperature", json={"temperature": 20.0, "soil_moisture": 15.0})
        assert captured["values"] == {"temperature": 20.0, "soil_moisture": 15.0}
        assert "water_level_percent" not in captured["values"]
        assert "rain" not in captured["values"]

    def test_rain_accepts_zero_and_one(self, client, monkeypatch):
        captured_payloads = []
        install_fake_esp(
            monkeypatch,
            lambda url, payload: captured_payloads.append(payload)
            or (200, {"accepted": True, "sequence": payload["sequence"], "commands": {}}),
        )

        client.post("/api/temperature", json={"temperature": 20.0, "rain": 0})
        client.post("/api/temperature", json={"temperature": 20.0, "rain": 1})
        assert captured_payloads[0]["values"]["rain"] == 0.0
        assert captured_payloads[1]["values"]["rain"] == 1.0

    def test_non_numeric_irrigation_field_is_rejected_before_forwarding(self, client, monkeypatch):
        calls = []
        install_fake_esp(monkeypatch, lambda url, payload: calls.append(payload) or (200, {}))

        response = client.post("/api/temperature", json={"temperature": 20.0, "soil_moisture": "wet"})
        assert response.status_code == 422
        assert calls == []


class TestEvents:
    def test_events_endpoint_returns_most_recent_first(self, client, monkeypatch):
        install_fake_esp(monkeypatch, lambda url, payload: (200, {"accepted": True, "sequence": payload["sequence"], "commands": {}}))

        client.post("/api/temperature", json={"temperature": 20.0})
        client.post("/api/temperature", json={"temperature": 30.0})

        events = client.get("/api/events").json()
        # Most recent event (ACCEPTED for sequence 2) should be first.
        assert events[0]["code"] == "ACCEPTED"
        assert "sequence=2" in events[0]["detail"]

    def test_events_respects_limit_query_param(self, client, monkeypatch):
        install_fake_esp(monkeypatch, lambda url, payload: (200, {"accepted": True, "sequence": payload["sequence"], "commands": {}}))

        for temperature in range(5):
            client.post("/api/temperature", json={"temperature": float(temperature)})

        events = client.get("/api/events?limit=3").json()
        assert len(events) == 3


class TestSessionReset:
    def test_reset_issues_new_session_id_and_resets_sequence(self, client, monkeypatch):
        install_fake_esp(monkeypatch, lambda url, payload: (200, {"accepted": True, "sequence": payload["sequence"], "commands": {}}))

        old_session_id = app_module.session.session_id
        client.post("/api/temperature", json={"temperature": 20.0})

        reset_response = client.post("/api/session/reset")
        assert reset_response.status_code == 200
        new_session_id = reset_response.json()["session_id"]
        assert new_session_id != old_session_id

        captured = {}
        install_fake_esp(monkeypatch, lambda url, payload: captured.update(payload) or (200, {"accepted": True, "sequence": payload["sequence"], "commands": {}}))
        client.post("/api/temperature", json={"temperature": 25.0})
        assert captured["session_id"] == new_session_id
        assert captured["sequence"] == 1  # sequence restarted


class TestActuatorFeedback:
    """Roadmap task 66 / blueprint page-1 diagram's "F. Actuator Simulator":
    the website picks an actuator + fault, this bridge computes the
    simulated feedback via logic/actuator_feedback.py and forwards it to
    the ESP's POST /feedback. These tests exercise the real simulation
    functions (not mocked) and only fake the ESP's HTTP response."""

    def test_fan_no_fault_matches_commanded_state(self, client, monkeypatch):
        install_fake_esp(monkeypatch, lambda url, payload: (200, {"accepted": True, "controller_fault_active": False}))

        response = client.post(
            "/api/actuator/feedback",
            json={"actuator": "fan", "fault_mode": "none", "commanded_state": True},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["measured_state"] is True
        assert body["fault_code"] is None

    def test_pump_stuck_off_produces_fault_when_commanded_on(self, client, monkeypatch):
        install_fake_esp(monkeypatch, lambda url, payload: (200, {"accepted": True, "controller_fault_active": True}))

        response = client.post(
            "/api/actuator/feedback",
            json={"actuator": "pump", "fault_mode": "stuck_off", "commanded_state": True},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["measured_state"] is False
        assert body["fault_code"] == "ACTUATOR-STUCK-OFF"

    def test_window_wrong_position_produces_fault_and_offset_angle(self, client, monkeypatch):
        install_fake_esp(monkeypatch, lambda url, payload: (200, {"accepted": True, "controller_fault_active": True}))

        response = client.post(
            "/api/actuator/feedback",
            json={"actuator": "window", "fault_mode": "wrong_position", "commanded_window_deg": 90},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["measured_state"] == 105
        assert body["fault_code"] == "ACTUATOR-WRONG-POSITION"

    def test_forwards_actuator_and_fault_code_to_esp_feedback_endpoint(self, client, monkeypatch):
        captured = {}

        def responder(url, payload):
            captured["url"] = url
            captured["payload"] = payload
            return 200, {"accepted": True, "controller_fault_active": True}

        install_fake_esp(monkeypatch, responder)

        client.post(
            "/api/actuator/feedback",
            json={"actuator": "fan", "fault_mode": "failed_startup", "commanded_state": True},
        )
        assert captured["url"] == f"{app_module.ESP_BASE_URL}/feedback"
        assert captured["payload"] == {"actuator": "fan", "fault_code": "ACTUATOR-FAILED-STARTUP"}

    def test_unknown_fault_mode_is_rejected_before_forwarding(self, client, monkeypatch):
        calls = []
        install_fake_esp(monkeypatch, lambda url, payload: calls.append(payload) or (200, {}))

        response = client.post(
            "/api/actuator/feedback",
            json={"actuator": "fan", "fault_mode": "not_a_real_fault", "commanded_state": True},
        )
        assert response.status_code == 400
        assert calls == []

    def test_unknown_actuator_is_rejected_before_forwarding(self, client, monkeypatch):
        calls = []
        install_fake_esp(monkeypatch, lambda url, payload: calls.append(payload) or (200, {}))

        response = client.post(
            "/api/actuator/feedback",
            json={"actuator": "heater", "fault_mode": "none", "commanded_state": True},
        )
        assert response.status_code == 400
        assert calls == []

    def test_missing_commanded_state_for_fan_is_rejected_before_forwarding(self, client, monkeypatch):
        calls = []
        install_fake_esp(monkeypatch, lambda url, payload: calls.append(payload) or (200, {}))

        response = client.post("/api/actuator/feedback", json={"actuator": "fan", "fault_mode": "none"})
        assert response.status_code == 400
        assert calls == []

    def test_missing_commanded_window_deg_is_rejected_before_forwarding(self, client, monkeypatch):
        calls = []
        install_fake_esp(monkeypatch, lambda url, payload: calls.append(payload) or (200, {}))

        response = client.post("/api/actuator/feedback", json={"actuator": "window", "fault_mode": "none"})
        assert response.status_code == 400
        assert calls == []

    def test_esp_unreachable_returns_502_and_logs_event(self, client, monkeypatch):
        def fake_post(url, json=None, timeout=None):
            raise httpx.ConnectError("connection refused", request=httpx.Request("POST", url))

        monkeypatch.setattr(app_module.httpx, "post", fake_post)

        response = client.post(
            "/api/actuator/feedback",
            json={"actuator": "fan", "fault_mode": "none", "commanded_state": True},
        )
        assert response.status_code == 502
        assert "Could not reach ESP" in response.json()["detail"]

        events = client.get("/api/events").json()
        codes = [e["code"] for e in events]
        assert "ESP_UNREACHABLE" in codes
        assert "ACTUATOR_FEEDBACK_SIMULATED" in codes

    def test_esp_rejection_returns_502_and_logs_event(self, client, monkeypatch):
        install_fake_esp(monkeypatch, lambda url, payload: (400, {"accepted": False, "error": "unknown actuator"}))

        response = client.post(
            "/api/actuator/feedback",
            json={"actuator": "fan", "fault_mode": "none", "commanded_state": True},
        )
        assert response.status_code == 502
        assert "ESP rejected the feedback" in response.json()["detail"]

        events = client.get("/api/events").json()
        codes = [e["code"] for e in events]
        assert "ESP_REJECTED" in codes


class TestEventLogUnit:
    """Direct unit tests of EventLog's ring-buffer behavior (roadmap task
    47), independent of the HTTP layer."""

    def test_bounded_capacity_evicts_oldest(self):
        log = EventLog(capacity=5)
        for i in range(8):
            log.push("CODE", f"detail-{i}")
        assert len(log) == 5
        recent = log.recent(limit=5)
        # Most recent first; oldest 3 (0,1,2) evicted.
        assert [e.detail for e in recent] == ["detail-7", "detail-6", "detail-5", "detail-4", "detail-3"]


class TestEndurance:
    """Roadmap task 48: run hundreds of updates.

    This exercises the bridge (sequencing, event log, request/response
    handling) under sustained load against a fake ESP -- real evidence for
    the bridge's own correctness. It is not evidence of the physical ESP
    surviving hundreds of real HTTP requests; that half of task 48 needs
    the real board and is tracked separately in docs/PROJECT_STATE.md.
    """

    def test_two_hundred_sequential_updates(self, client, monkeypatch):
        install_fake_esp(
            monkeypatch,
            lambda url, payload: (
                200,
                {
                    "accepted": True,
                    "sequence": payload["sequence"],
                    "commands": fake_esp_decision(payload["values"]["temperature"]),
                },
            ),
        )

        total_updates = 200
        for i in range(total_updates):
            temperature = 10.0 + (i % 50)
            response = client.post("/api/temperature", json={"temperature": temperature})
            assert response.status_code == 200
            assert response.json()["sequence"] == i + 1

        events = client.get(f"/api/events?limit={total_updates * 2}").json()
        accepted_events = [e for e in events if e["code"] == "ACCEPTED"]
        assert len(accepted_events) == total_updates
