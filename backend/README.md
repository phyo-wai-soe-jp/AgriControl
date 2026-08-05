# FastAPI bridge (Stage 6 - Browser and FastAPI; Stage 7 - Irrigation slice; Stage 9 - Actuator feedback)

Blueprint Branch 3 ("Browser-to-ESP communication, sessions, logs, replay,
tests"). Sits between the website simulator (`simulator/index.html`) and the
ESP32. Coordinates sessions, sequencing, and logging -- it never decides
actuator behavior itself; that stays on the ESP, per the blueprint's core
rule that no interface may bypass the central control loop.

Unlike `firmware/`, **this code has actually been run and tested** in this
environment -- there's no hardware dependency for the bridge itself, only
for the real ESP it eventually talks to.

## Transport

As of 2026-08-06, this bridge talks to the ESP over MQTT (via the
self-hosted Mosquitto broker `firmware/src/mqtt_test_harness.cpp` connects
to), not direct HTTP. This lets the ESP sit behind a home NAT with no
port-forwarding or reverse tunnel required -- it makes an outbound
connection to the broker, same as this bridge does. Requests are
published to `agricontrol/sensor` / `agricontrol/feedback` and correlated
with the ESP's response on `agricontrol/state` / `agricontrol/feedback_state`
by echoing back `sequence` / `request_id`. The browser-facing HTTP API
below is unchanged by this; only how this process reaches the ESP changed.

## Setup

```bash
cd /path/to/ArgriControl
pip install -r backend/requirements.txt
```

## Run

```bash
AGRICONTROL_MQTT_HOST="esp32.phyowaisoe.com" \
AGRICONTROL_MQTT_USER="agricontrol-test-harness" \
AGRICONTROL_MQTT_PASSWORD="<broker password>" \
  uvicorn backend.app:app --reload
```

`AGRICONTROL_MQTT_PORT` defaults to 8883 (TLS). `AGRICONTROL_ESP_TIMEOUT_SECONDS`
(default 5) controls how long a request waits for the ESP's response before
being treated as unreachable.

Then open `simulator/index.html` in a browser (as a local file, or serve it
with any static file server) and point its "FastAPI bridge base URL" field
at wherever this bridge is running.

## Test

```bash
python3 -m pytest backend/tests/ -v
```

35 tests, all passing as of this writing, covering: health check, forwarding
temperature to the ESP with the correct protocol shape, sequence
incrementing, relaying the ESP's response unchanged, ESP-unreachable and
ESP-rejects-message error handling (both return HTTP 502 with the failure
logged), the event log's bounded ring-buffer behavior, session reset, a
200-sequential-update endurance run (roadmap task 48's bridge-side half --
see "What's not tested" below), the Stage 7 irrigation fields
(soil_moisture/water_level_percent/rain: all optional, only forwarded when
provided, rain restricted to 0/1, type validation), the Stage 8 scenario
suite (`test_scenarios.py`, run against the real decision/safety logic), and
Stage 9's actuator-fault-feedback endpoint (`TestActuatorFeedback`: all
three actuator kinds, all fault modes, validation errors, ESP-unreachable/
ESP-rejected paths).

## What's not tested

- Against the **real** ESP or a real MQTT broker. Every test here
  monkeypatches `mqtt_client.publish` with a fake responder -- correlation,
  request/response shape, and the bridge's own logic are proven, but not an
  actual round trip over the network. See `docs/PROJECT_STATE.md` for
  live-hardware verification evidence instead.
- `simulator/index.html` was functionally tested with a jsdom harness
  (temperature slider, send, response rendering, window-angle-to-rotation
  scaling, error handling, event log rendering, connection check, actuator
  fault simulator) -- but never opened in an actual browser. Do that before
  relying on it.

## Files

- `app.py` - the FastAPI app: `POST /api/temperature` (roadmap task 42),
  `POST /api/actuator/feedback` (task 66), `GET /api/events` (task 47),
  `GET /api/health`, `POST /api/session/reset`.
- `tests/test_app.py` - pytest suite for `app.py` (see above).
- `tests/test_scenarios.py` - Stage 8 scenario suite against the real
  decision/safety logic.
- `requirements.txt` - `fastapi`, `paho-mqtt`, `uvicorn`, `pytest`.

## Scope

Temperature is required; soil moisture, tank level, and rain are optional,
matching `firmware/src/mqtt_test_harness.cpp`'s validation. Pump commands
are relayed in the ESP's response but not physically actuated anywhere in
this system yet -- no pump GPIO/relay pin has been assigned on the
firmware side.

## Open owner questions

- Whether `allow_origins=["*"]` in the CORS middleware is acceptable now
  that the simulator page and bridge are both publicly reachable, or
  should be tightened.
- The MQTT broker credentials are a shared, unauthenticated-from-the-
  website secret (anyone who can reach the bridge can already send
  arbitrary commands/faults) -- revisit alongside the CORS question above.
