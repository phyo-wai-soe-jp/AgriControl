# AgriControl

AgriControl is the project workspace for an ESP32 Virtual Control Lab: a
digital-twin and hardware-in-the-loop control platform for a greenhouse-style
controller.

## Live Links

- Control site (simulator, drives the real ESP32 board):
  https://agricontrol.phyowaisoe.com/
- Progress dashboard: https://agricontrol.phyowaisoe.com/taskmanagement/

(Both are also reachable under `https://phyowaisoe.com/agricontrol/...`.)

## Source Of Truth

The project is guided by `ESP32_Virtual_Control_Lab_Blueprint.pdf`. The core
design rule is that no interface, sensor, actuator, or communication method may
bypass the central control loop.

The physical board is confirmed by `ESP32-C3M-TRY-R1-20230701.pdf`, the
owner's manual for the ESP32-C3M-TRY (MicroFan) eval board used to build the
control lab.

## Architecture

The control site talks to a FastAPI bridge, which talks to the real
ESP32-C3M-TRY over MQTT (via a self-hosted Mosquitto broker) -- not direct
HTTP. This lets the board sit behind a home NAT with no port-forwarding or
tunnel: both the ESP and the bridge make outbound connections to the broker.
The ESP remains the sole decision-making authority; the bridge only relays,
correlates requests/responses, and logs.

```
Browser (simulator) --HTTP--> FastAPI bridge --MQTT--> Mosquitto --MQTT--> ESP32-C3M-TRY
```

## Repository Map

- `ESP32_Virtual_Control_Lab_Blueprint.pdf` - complete system blueprint.
- `ESP32-C3M-TRY-R1-20230701.pdf` - owner's manual for the confirmed physical
  board (board identity, pin map, peripheral wiring).
- `web-build/` - static website deployed to the public dashboard URL.
- `docs/AI_CONTINUITY_SYSTEM.md` - operating system for future AI agents.
- `docs/PROJECT_STATE.md` - current project status, evidence, and next work.
- `docs/USER_GUIDE.md` - owner guide for dashboard, communication reports, and
  agent board.
- `docs/AI_AGENT_GUIDE.md` - model guide for multi-agent coordination and
  handoff.
- `docs/PROMPT_TEST_LIBRARY.md` - structured implementation and verification
  prompts for the whole roadmap.
- `data/progress-baseline.json` - machine-readable blueprint progress model.
- `data/agent-coordination.json` - machine-readable agent roles and current
  assignments.
- `data/prompt-test-library.json` - machine-readable prompt and test catalog.
- `tools/generate-prompt-test-library.mjs` - rebuilds the Markdown and JSON
  prompt library from the baseline model.
- `tools/mqtt_hardware_verify.py` - standalone MQTT client for verifying the
  real board against `firmware/src/mqtt_test_harness.cpp` directly, without
  going through the bridge.
- `logic/` - host-runnable pure logic: canonical sensor state, system and
  actuator state, the stateful decision engine, the safety supervisor, and
  actuator-feedback fault simulation (`actuator_feedback.py`).
- `tests/` - unit, boundary, conflict, and sequence tests for `logic/`
  (`python3 -m unittest discover -s tests`).
- `firmware/` - PlatformIO / Arduino C++ project for the ESP32-C3M-TRY board.
  `env:mqtt_test_harness` is what's actually flashed and running on the real
  board in production (MQTT transport, no port-forwarding needed);
  `env:irrigation_slice` is the equivalent direct-HTTP version for
  local-network-only use. Both share the same decision engine, safety
  supervisor, and actuator-feedback handling. All 10 environments build
  clean; the MQTT and HTTP slices have each been flashed and verified
  against the real board (Gates A-C).
- `backend/` - FastAPI bridge (Stage 6/7/9, Branch 3) between the website
  simulator and the ESP, talking MQTT via `paho-mqtt`. Actually run and
  tested (`python3 -m pytest backend/tests/` -- 35 passing).
- `simulator/` - the live control site: temperature/soil-moisture/tank-level
  sliders, a live actuator view (animated window, spinning fan, and a
  water-flowing pump/valve visual), and a Japanese/English toggle. Verified
  end-to-end against the real ESP32 board over the public internet, not just
  host-level tests -- deployed at https://agricontrol.phyowaisoe.com/.
- `AGENTS.md` - instructions for coding agents working in this repo.

## Current Progress Model

The dashboard tracks:

- 12 blueprint development stages.
- 82 roadmap tasks.
- 16 architecture branches.
- 12 central control-loop steps.
- Gate A-E completion criteria.
- Communication reports for open work, owner help, unknowns, and blockers in
  multiple-choice, long-text, and structured handoff formats.
- AI agent coordination showing which model is doing what, what it has done,
  and where owner help is needed.

Progress edits in the browser are saved locally unless exported. Durable status
updates should be written back to `data/progress-baseline.json` and
`docs/PROJECT_STATE.md`.

## Continue The Project

Start with `AGENTS.md`, then read `docs/PROJECT_STATE.md` and
`docs/AI_CONTINUITY_SYSTEM.md`, then use `docs/AI_AGENT_GUIDE.md` and
`docs/PROMPT_TEST_LIBRARY.md` to claim one agent role and pick the exact
implementation and test prompts for the next open task. Work through the
blueprint roadmap in order, starting with the first open task that unlocks the
next vertical slice.
