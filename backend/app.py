"""FastAPI bridge (blueprint Branch 3, Stage 6 roadmap tasks 41/42/47).

Sits between the website simulator and the ESP32 control authority.
Forwards the website's virtual temperature to the ESP's /sensor endpoint,
relays the ESP's decision back to the website, and keeps a bridge-side
event log. Coordinates sessions/sequencing/logging only -- it never
decides actuator behavior itself; that stays on the ESP, per the
blueprint's core rule that no interface may bypass the central control
loop.

First vertical slice scope: temperature only, matching
firmware/src/vertical_slice.cpp. Soil moisture, tank level, and rain
arrive in Stage 7.

Run locally with: uvicorn backend.app:app --reload
"""
from __future__ import annotations

import itertools
import os
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Iterator, List

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

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


class TemperatureRequest(BaseModel):
    temperature: float = Field(..., description="Virtual temperature in Celsius from the website simulator.")


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
def forward_temperature(request: TemperatureRequest) -> dict:
    """Roadmap task 42: forward temperature to the ESP."""
    sequence = session.next_sequence()
    payload = {
        "session_id": session.session_id,
        "sequence": sequence,
        "values": {"temperature": request.temperature},
    }
    events.push("SENT", f"sequence={sequence} temperature={request.temperature}")

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
