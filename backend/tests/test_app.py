"""Tests for the FastAPI bridge (roadmap tasks 41, 42, 47, 48).

Runs entirely on the host -- no physical ESP needed. httpx.post is
monkeypatched to a fake ESP so these tests are fast, deterministic, and
don't depend on network or hardware availability. This is the one part of
AgriControl's Stage 4-6 work that can be genuinely executed and verified
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
