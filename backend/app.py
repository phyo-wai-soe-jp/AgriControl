"""FastAPI bridge (blueprint Branch 3, Stage 6 roadmap tasks 41/42/47).

Sits between the website simulator and the ESP32 control authority.
Forwards the website's virtual temperature to the ESP's /sensor endpoint,
relays the ESP's decision back to the website, and keeps a bridge-side
event log. Coordinates sessions/sequencing/logging only -- it never
decides actuator behavior itself; that stays on the ESP, per the
blueprint's core rule that no interface may bypass the central control
loop.

Stage 7 (roadmap tasks 49-57) extended this to soil moisture, tank level,
and rain, matching firmware/src/irrigation_slice.cpp -- all three are
optional per request, same as the ESP firmware's validation (a request
with temperature alone still works exactly as it did in Stage 6).

Run locally with: uvicorn backend.app:app --reload
"""
from __future__ import annotations

import itertools
import os
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Iterator, List, Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from logic.actuator_feedback import (
    FaultMode,
    detect_mismatch,
    simulate_binary_actuator,
    simulate_servo_actuator,
)

# Roadmap task 42: forward temperature to the ESP. Configurable, not
# hardcoded -- the real ESP's IP address is an open owner question (see
# docs/PROJECT_STATE.md), not something to guess.
ESP_BASE_URL = os.environ.get("AGRICONTROL_ESP_BASE_URL", "http://192.168.4.1")
ESP_REQUEST_TIMEOUT_SECONDS = float(os.environ.get("AGRICONTROL_ESP_TIMEOUT_SECONDS", "5"))

# Roadmap task 47: event log. Fixed-capacity, matching the firmware's
# ring-buffer approach (firmware/include/events.h), for the same reason:
# bounded memory on a long-running bridge process.
EVENT_LOG_CAPACITY = 500


@dataclass
class Event:
    timestamp_ms: int
    code: str
    detail: str


class EventLog:
    def __init__(self, capacity: int = EVENT_LOG_CAPACITY) -> None:
        self._events: Deque[Event] = deque(maxlen=capacity)

    def push(self, code: str, detail: str) -> None:
        self._events.append(Event(timestamp_ms=int(time.time() * 1000), code=code, detail=detail))

    def recent(self, limit: int = 50) -> List[Event]:
        return list(self._events)[-limit:][::-1]

    def __len__(self) -> int:
        return len(self._events)


@dataclass
class BridgeSession:
    """Session and sequence state for one bridge run.

    Blueprint protocol rule: "New browser start creates a new session_id."
    This bridge owns one session per process start -- it is the thing
    actually talking to the ESP, so it is the thing that owns session_id
    and the per-session sequence counter, not the website.
    """

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    _sequence: Iterator[int] = field(default_factory=lambda: itertools.count(1))

    def next_sequence(self) -> int:
        return next(self._sequence)


class SensorRequest(BaseModel):
    """Roadmap tasks 42/49-51: the values the website simulator can send.

    Only `temperature` is required, matching the ESP firmware's
    validation (firmware/src/irrigation_slice.cpp): a request with just
    temperature is still a fully valid message, just like Stage 5/6.
    """

    temperature: float = Field(..., description="Virtual temperature in Celsius from the website simulator.")
    soil_moisture: Optional[float] = Field(None, description="Virtual soil moisture percent (0-100).")
    water_level_percent: Optional[float] = Field(None, description="Virtual tank level percent (0-100).")
    rain: Optional[float] = Field(None, description="Virtual rain flag: 0 (no rain) or 1 (raining).")


class ActuatorFeedbackRequest(BaseModel):
    """Roadmap task 66 / blueprint page-1 diagram's "F. Actuator Simulator".

    The website picks an actuator and an injectable fault; this bridge
    computes the simulated feedback (via logic/actuator_feedback.py, not
    reimplemented here) and forwards it to the ESP's POST /feedback so its
    safety supervisor can react through controller_fault -- closing the
    loop, not just proving the fault math on the host.
    """

    actuator: str = Field(..., description="'fan', 'pump', or 'window'.")
    fault_mode: str = Field("none", description="none, failed_startup, stuck_on, stuck_off, or wrong_position.")
    commanded_state: Optional[bool] = Field(None, description="Commanded on/off, required for fan/pump.")
    commanded_window_deg: Optional[int] = Field(None, description="Commanded angle in degrees, required for window.")


app = FastAPI(title="AgriControl FastAPI Bridge", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Local bridge for a local simulator; tighten before any non-local deployment.
    allow_methods=["*"],
    allow_headers=["*"],
)

session = BridgeSession()
events = EventLog()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "session_id": session.session_id}


@app.post("/api/temperature")
def forward_temperature(request: SensorRequest) -> dict:
    """Roadmap tasks 42/49-51: forward sensor values to the ESP.

    Only includes keys the caller actually provided -- an omitted
    soil_moisture/water_level_percent/rain is genuinely "no reading available"
    to the ESP's decision engine (holds previous pump state), not "assume 0",
    matching logic/decision.py's / firmware/include/irrigation.h's handling
    of missing values.
    """
    sequence = session.next_sequence()
    values: dict = {"temperature": request.temperature}
    if request.soil_moisture is not None:
        values["soil_moisture"] = request.soil_moisture
    if request.water_level_percent is not None:
        values["water_level_percent"] = request.water_level_percent
    if request.rain is not None:
        values["rain"] = request.rain

    payload = {
        "session_id": session.session_id,
        "sequence": sequence,
        "values": values,
    }
    events.push("SENT", f"sequence={sequence} values={values}")

    try:
        response = httpx.post(f"{ESP_BASE_URL}/sensor", json=payload, timeout=ESP_REQUEST_TIMEOUT_SECONDS)
    except httpx.RequestError as exc:
        events.push("ESP_UNREACHABLE", f"sequence={sequence} error={exc}")
        raise HTTPException(status_code=502, detail=f"Could not reach ESP at {ESP_BASE_URL}: {exc}") from exc

    if response.status_code >= 400:
        events.push(
            "ESP_REJECTED", f"sequence={sequence} status={response.status_code} body={response.text}"
        )
        raise HTTPException(
            status_code=502, detail=f"ESP rejected the message: {response.status_code} {response.text}"
        )

    body = response.json()
    events.push("ACCEPTED", f"sequence={sequence} response={body}")
    return body


@app.post("/api/actuator/feedback")
def simulate_actuator_feedback(request: ActuatorFeedbackRequest) -> dict:
    """Roadmap task 66: simulate an actuator fault and forward it to the ESP.

    Computes the simulated feedback host-side using logic/actuator_feedback.py
    (already covered by tests/test_actuator_feedback.py), then POSTs the
    resulting fault_code to the ESP's /feedback endpoint, mirroring
    forward_temperature's ESP-error handling (RequestError -> 502,
    status>=400 -> 502).
    """
    try:
        fault_mode = FaultMode(request.fault_mode)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Unknown fault_mode: {request.fault_mode}") from exc

    if request.actuator == "window":
        if request.commanded_window_deg is None:
            raise HTTPException(status_code=400, detail="commanded_window_deg is required for actuator=window")
        servo_feedback = simulate_servo_actuator(request.commanded_window_deg, fault_mode=fault_mode)
        measured_state = servo_feedback.measured_deg
        fault_code = detect_mismatch(request.commanded_window_deg, measured_state, servo_feedback.fault_code)
    elif request.actuator in ("fan", "pump"):
        if request.commanded_state is None:
            raise HTTPException(status_code=400, detail=f"commanded_state is required for actuator={request.actuator}")
        # elapsed_since_command_ms is fixed well past any startup-delay window:
        # this endpoint simulates steady-state fault behavior for the website,
        # not the transient startup-delay case (see logic/actuator_feedback.py).
        binary_feedback = simulate_binary_actuator(
            request.commanded_state, elapsed_since_command_ms=99999, fault_mode=fault_mode
        )
        measured_state = binary_feedback.measured_state
        fault_code = detect_mismatch(request.commanded_state, measured_state, binary_feedback.fault_code)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown actuator: {request.actuator}")

    events.push(
        "ACTUATOR_FEEDBACK_SIMULATED",
        f"actuator={request.actuator} fault_mode={request.fault_mode} measured={measured_state} fault_code={fault_code}",
    )

    esp_payload = {"actuator": request.actuator, "fault_code": fault_code}
    try:
        response = httpx.post(f"{ESP_BASE_URL}/feedback", json=esp_payload, timeout=ESP_REQUEST_TIMEOUT_SECONDS)
    except httpx.RequestError as exc:
        events.push("ESP_UNREACHABLE", f"feedback actuator={request.actuator} error={exc}")
        raise HTTPException(status_code=502, detail=f"Could not reach ESP at {ESP_BASE_URL}: {exc}") from exc

    if response.status_code >= 400:
        events.push(
            "ESP_REJECTED", f"feedback actuator={request.actuator} status={response.status_code} body={response.text}"
        )
        raise HTTPException(
            status_code=502, detail=f"ESP rejected the feedback: {response.status_code} {response.text}"
        )

    esp_body = response.json()
    events.push("ACCEPTED", f"feedback actuator={request.actuator} esp_response={esp_body}")
    return {"measured_state": measured_state, "fault_code": fault_code, "esp_response": esp_body}


@app.get("/api/events")
def recent_events(limit: int = 50) -> List[dict]:
    """Roadmap task 47: expose the bridge-side event log."""
    return [{"timestamp_ms": e.timestamp_ms, "code": e.code, "detail": e.detail} for e in events.recent(limit)]


@app.post("/api/session/reset")
def reset_session() -> dict:
    """Start a new session_id and sequence counter, matching the
    blueprint's "New browser start creates a new session_id" rule."""
    global session
    session = BridgeSession()
    events.push("SESSION_RESET", f"session_id={session.session_id}")
    return {"session_id": session.session_id}
