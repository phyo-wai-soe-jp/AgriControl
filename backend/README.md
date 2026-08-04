# FastAPI bridge (Stage 6 - Browser and FastAPI; Stage 7 - Irrigation slice)

Blueprint Branch 3 ("Browser-to-ESP communication, sessions, logs, replay,
tests"). Sits between the website simulator (`simulator/index.html`) and the
ESP32. Coordinates sessions, sequencing, and logging -- it never decides
actuator behavior itself; that stays on the ESP, per the blueprint's core
rule that no interface may bypass the central control loop.

Unlike `firmware/`, **this code has actually been run and tested** in this
environment -- there's no hardware dependency for the bridge itself, only
for the real ESP it eventually talks to.

## Setup

```bash
cd /path/to/ArgriControl
pip install -r backend/requirements.txt
```

## Run

```bash
# Point at wherever the real ESP ends up (see docs/PROJECT_STATE.md --
# the ESP's IP address is an open owner question, not something to guess).
AGRICONTROL_ESP_BASE_URL="http://<esp-ip>" uvicorn backend.app:app --reload
```

Then open `simulator/index.html` in a browser (as a local file, or serve it
with any static file server) and point its "FastAPI bridge base URL" field
at `http://127.0.0.1:8000`.

## Test

```bash
python3 -m pytest backend/tests/ -v
```

17 tests, all passing as of this writing, covering: health check, forwarding
temperature to the ESP with the correct protocol shape, sequence
incrementing, relaying the ESP's response unchanged, ESP-unreachable and
ESP-rejects-message error handling (both return HTTP 502 with the failure
logged), the event log's bounded ring-buffer behavior, session reset, a
200-sequential-update endurance run (roadmap task 48's bridge-side half --
see "What's not tested" below), and the Stage 7 irrigation fields
(soil_moisture/water_level_percent/rain: all optional, only forwarded when
provided, rain restricted to 0/1, type validation).

Also live-smoke-tested end-to-end over real sockets: `uvicorn` serving the
bridge, a throwaway `http.server`-based fake ESP, and `curl` driving the
whole path -- confirmed correct sequence numbers and correct
temperature-to-command mapping (20C -> fan off/window 10, 30C -> fan
on/window 90, 40C -> fan on/window 170), matching
`firmware/include/decision.h` exactly.

## What's not tested

- Against the **real** ESP. Every test here uses a fake ESP (either
  monkeypatched `httpx.post`, or a throwaway local `http.server`). Roadmap
  task 48 ("run hundreds of updates") is only half-covered: the bridge's own
  correctness under load is verified, but not the physical ESP's endurance.
- `simulator/index.html` was functionally tested with a jsdom harness
  (temperature slider, send, response rendering, window-angle-to-rotation
  scaling, error handling, event log rendering, connection check) -- but
  never opened in an actual browser. Do that before relying on it.

## Files

- `app.py` - the FastAPI app: `POST /api/temperature` (roadmap task 42),
  `GET /api/events` (task 47), `GET /api/health`, `POST /api/session/reset`.
- `tests/test_app.py` - pytest suite (see above).
- `requirements.txt` - `fastapi`, `httpx`, `uvicorn`, `pytest`.

## Scope

Temperature is required; soil moisture, tank level, and rain are optional,
matching `firmware/src/irrigation_slice.cpp`'s validation. Pump commands
are relayed in the ESP's response but not physically actuated anywhere in
this system yet -- no pump GPIO/relay pin has been assigned on the
firmware side.

## Open owner questions

- The real ESP's IP address / hostname (`AGRICONTROL_ESP_BASE_URL`) once the
  board is on a network reachable from wherever this bridge runs.
- Whether `allow_origins=["*"]` in the CORS middleware is acceptable for
  local development, or should be tightened once this isn't purely local.
