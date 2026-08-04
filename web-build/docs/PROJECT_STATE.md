# AgriControl Project State

Last updated: 2026-08-04 JST (Stage 4 ESP runtime drafted)

## Live Links

- Public dashboard: https://phyowaisoe.com/agricontrol/taskmanagement/
- GitHub repository: https://github.com/phyo-wai-soe-jp/AgriControl.git
- Blueprint PDF: `ESP32_Virtual_Control_Lab_Blueprint.pdf`
- Public blueprint PDF: https://phyowaisoe.com/agricontrol/taskmanagement/ESP32_Virtual_Control_Lab_Blueprint.pdf
- Board manual PDF: `ESP32-C3M-TRY-R1-20230701.pdf`
- Public board manual PDF: https://phyowaisoe.com/agricontrol/taskmanagement/ESP32-C3M-TRY-R1-20230701.pdf

## Current Source State

The repository currently contains the blueprint, a static dashboard, durable
handoff documentation, and machine-readable progress data.

Important files:

- `AGENTS.md`
- `README.md`
- `docs/AI_CONTINUITY_SYSTEM.md`
- `docs/PROJECT_STATE.md`
- `docs/USER_GUIDE.md`
- `docs/AI_AGENT_GUIDE.md`
- `docs/PROMPT_TEST_LIBRARY.md`
- `data/progress-baseline.json`
- `data/agent-coordination.json`
- `data/prompt-test-library.json`
- `web-build/index.html`
- `web-build/docs/AI_CONTINUITY_SYSTEM.md`
- `web-build/docs/PROJECT_STATE.md`
- `web-build/docs/USER_GUIDE.md`
- `web-build/docs/AI_AGENT_GUIDE.md`
- `web-build/docs/PROMPT_TEST_LIBRARY.md`
- `web-build/docs/README.md`
- `web-build/data/progress-baseline.json`
- `web-build/data/agent-coordination.json`
- `web-build/data/prompt-test-library.json`
- `tools/generate-prompt-test-library.mjs`
- `logic/` - host-runnable pure logic: canonical sensor state, system/actuator
  state, decision engine, safety supervisor.
- `tests/` - unit, boundary, conflict, and sequence tests for `logic/`.
- `firmware/` - PlatformIO / Arduino C++ project for the physical
  ESP32-C3M-TRY board: `main.cpp`, Stage 3 output test environments, and a
  drafted Stage 4 ESP runtime (`env:runtime`), unverified by a build in
  this environment.

## Current Progress Snapshot

Baseline progress is intentionally conservative:

- Overall progress: 29%
- Roadmap execution: 28%
- Branch readiness: 41%
- Completion gates: 0%
- Central control-loop coverage: 48%

These numbers come from the blueprint-derived model in
`data/progress-baseline.json`. Browser-local edits on the public dashboard do
not change durable project state until they are exported and committed.

## Completed Work

Date: 2026-08-04 JST (Stage 4 ESP runtime drafted)

Agent: agent-04-firmware-runtime (Claude Sonnet 5).

This session drafts the Stage 4 ESP runtime entirely without hardware
access -- it's infrastructure code (async loop, shared state, events,
stale-data detection, recovery, HTTP server, request-size/validation
limits), not something that requires the physical board to write. It does
require the board (and real WiFi credentials) to verify.

Changed:

- Added `firmware/include/canonical.h`: `SensorId`, `SensorReading`,
  `SensorState`, mirroring `logic/canonical.py`'s model in C++ (roadmap
  task 25, Branch 6/7).
- Added `firmware/include/system_state.h`: `Mode`/`CommunicationState`
  enums with the exact same transition graph as `logic/system_state.py`
  (roadmap task 24), plus `RecoveryTracker` implementing the blueprint's
  recovery chain -- Failure -> Safe state -> consecutive valid messages ->
  stable communication -> clear fault -> resume automatic (roadmap task 28).
  `kDataStaleTimeoutMs` (10s) and `kRecoveryConsecutiveValidRequired` (5)
  are explicit tunable constants, not guessed hardware facts -- flagged for
  owner confirmation.
- Added `firmware/include/events.h`: fixed-capacity (32-entry) ring-buffer
  event log, no dynamic growth (roadmap task 26, Branch 12).
- Added `firmware/include/shared_state.h`: bundles sensors/system/
  recovery/events into one `SharedState` with a non-blocking `tick()` that
  detects staleness and drives WARNING -> RECOVERY -> AUTOMATIC transitions
  (roadmap task 27).
- Added `firmware/src/runtime.cpp` (`env:runtime`): connects WiFi, runs a
  `WebServer` on port 80 with `POST /sensor`, enforces a request-size cap
  (`kMaxRequestBodyBytes = 2048`, roadmap task 30), rejects malformed JSON,
  rejects duplicate/out-of-order `sequence` values, and rejects messages
  naming an unrecognized sensor field. Explicitly does **not** call a
  decision engine or drive any actuator, and does not do per-sensor
  range/type validation -- both are Stage 5 (roadmap task 33), out of
  scope here.
- Added `firmware/include/secrets.h.example` (WiFi credential template) and
  gitignored `firmware/include/secrets.h` so real credentials are never
  committed.
- Added `[env:runtime]` to `firmware/platformio.ini` and declared the
  `ArduinoJson` dependency.
- Advanced branch 5 (ESP communication) `planned` -> `drafted` and branch
  12 (Observability) `drafted` -> `implemented`.

Evidence:

- `firmware/include/*.h` and `firmware/src/runtime.cpp` reviewed for
  syntax/structure and API usage against the Arduino-ESP32 core, `WebServer`,
  and ArduinoJson v7 APIs from memory. **No `pio run` build was performed**
  -- there is no PlatformIO toolchain, WiFi network, or physical board
  access in this environment. Treat this as a reviewed draft, not verified
  working code; normal to need small fixes once actually compiled.

Status updates:

- Roadmap tasks 24-30 marked `active` (drafted, unverified).
- Branch 5 -> `drafted`; branch 12 -> `implemented`.

Blockers (owner input needed, tracked in `data/agent-coordination.json`
under `agent-04-firmware-runtime`):

1. Real WiFi SSID/password for `firmware/include/secrets.h`.
2. Build/upload `env:runtime` and send a test `POST /sensor` (e.g. via
   `curl`); report the response and serial log as evidence.
3. Confirm or adjust the placeholder tuning constants: 10s stale-data
   timeout, 5-message recovery threshold, 2048-byte max request body.

Next task: get `env:runtime` actually building (fix whatever compile errors
turn up -- expected, since this was never compiled), then flash and test
against the real board and WiFi network.

Date: 2026-08-04 JST (firmware toolchain decision + servo power confirmed)

Agent: agent-02-hardware (Claude Sonnet 5).

Owner-provided evidence and decisions this session:

- The board on serial port `/dev/cu.usbmodem1101` is the same physical
  ESP32-C3M-TRY used for AgriControl, currently running an Arduino/PlatformIO
  test sketch rather than MicroPython.
- Decision: AgriControl's firmware layer (Stage 3+) is built with
  **PlatformIO, Arduino framework, C++**, not MicroPython. This supersedes
  the blueprint's roadmap task 2 wording ("Record the MicroPython version"),
  which is now interpreted as "record the firmware toolchain and version."
  `data/progress-baseline.json` task 2's title was updated to match, and
  `tools/generate-prompt-test-library.mjs` / `docs/USER_GUIDE.md` /
  `docs/AI_CONTINUITY_SYSTEM.md` were updated so no durable doc still implies
  MicroPython is the plan.
- Servo power stability (roadmap task 23): confirmed by direct observation
  on the live board while a servo was cycled repeatedly through motion (a
  sweep into a rapid back-and-forth pattern between roughly 0 deg and 58
  deg) -- the ESP did not reset. This test used the board's existing
  Arduino/PlatformIO sketch, not the newly-added `firmware/src/test_servo.cpp`
  below, which has not itself been flashed yet.

Changed:

- Deleted the prior session's MicroPython scripts (`firmware/boot.py`,
  `test_oled.py`, `test_neopixel.py`, `test_buzzer.py`, `test_servo.py`) --
  superseded by the toolchain decision above, and left in place they would
  have misled a future agent into thinking MicroPython was still the plan.
- Added a PlatformIO project in `firmware/`: `platformio.ini` (one
  environment per test file via `build_src_filter`, board
  `esp32-c3-devkitm-1` as the closest chip-accurate match for the
  ESP32-C3-MINI-1 module), `include/pins.h` (shared pin constants from the
  manual's Table 5.2), `src/main.cpp` (LED-blink bring-up placeholder), and
  `src/test_oled.cpp` / `test_neopixel.cpp` / `test_buzzer.cpp` /
  `test_servo.cpp` for roadmap tasks 17-20. None of this has been built with
  `pio run` in this environment -- there is no PlatformIO toolchain or board
  access here, so it is unverified beyond visual review.
- Updated `data/progress-baseline.json`, `data/agent-coordination.json`,
  `docs/USER_GUIDE.md`, `docs/AI_CONTINUITY_SYSTEM.md`,
  `tools/generate-prompt-test-library.mjs`, and README/AGENTS files to
  remove MicroPython-specific wording and reflect the PlatformIO decision;
  regenerated `docs/PROMPT_TEST_LIBRARY.md` and
  `data/prompt-test-library.json`.
- Added `firmware/src/test_all_outputs.cpp` (`env:test_all_outputs`) for
  roadmap task 21: combines OLED, NeoPixel, and buzzer on one build to check
  for shared-bus/power interference. Deliberately excludes the servo, since
  the hardware-verified servo power test did not include the other outputs
  running at the same time. Meant to run only after tasks 17-19 have their
  own individual hardware evidence.

Evidence (this session):

- Direct observation of the physical board while the servo cycled
  repeatedly (owner-reported, not reproducible from this environment).
- `firmware/*.cpp` and `platformio.ini` reviewed for syntax/structure only;
  no `pio run` build was performed here.

Status updates (this session):

- Roadmap task 2 marked `done` (title changed to "Record the firmware
  toolchain and version"; toolchain is confirmed as PlatformIO/Arduino C++).
- Roadmap tasks 20 and 23 marked `done` (servo motion observed; ESP did not
  reset).
- Roadmap tasks 17-19 remain `active` (still unverified on hardware).
- Roadmap task 21 marked `active`: combined-output test source drafted,
  unverified on hardware, and gated behind 17-19 individually passing first.
- `known_unknowns` updated: MicroPython version and generic servo-power
  unknowns removed; exact RC servo model, pump/fan pin assignment, and
  exact PlatformIO/Arduino-ESP32 core versions remain open.

Blockers (owner input still needed, tracked in `data/agent-coordination.json`
under `agent-02-hardware`):

1. Which RC servo model is attached to CN3? (Power stability is resolved;
   the model itself is not.)
2. Which spare GPIO/relay will drive the greenhouse pump and fan? This eval
   board has no built-in pump or fan output.
3. Exact `platform-espressif32` / Arduino-ESP32 core versions in use, to pin
   in `firmware/platformio.ini` for reproducible builds.

Next task: build/upload `firmware/` test environments
(`pio run -e test_oled|test_neopixel|test_buzzer -t upload`) on the physical
board and report the results, then `env:test_all_outputs` (task 21); answer
the three blockers above before advancing Stage 3 further (task 22).

Older changes (previous session: Stage 1 hardware facts + Stage 3 firmware
drafts, superseded above where noted -- the firmware was MicroPython at the
time and has since been rewritten in PlatformIO/Arduino C++):

- Confirmed the exact ESP32-C3 board (roadmap task 1): **ESP32-C3M-TRY** by
  MicroFan, using the **ESP32-C3-MINI-1** module (RISC-V core, 4MB flash).
- Recorded the complete pin map (roadmap task 3) in `firmware/README.md`,
  sourced from the manual's Table 5.2: LED1=D0, SW1/2/3=D2/D3/D6 (active-low),
  SW4=D9 (shared with I2C SCL, BOOT-mode select only), SW5=RST, NeoPixel
  x3=D10, I2C SCL=D9/SDA=D8 (OLED, AHT21, KXTJ3-1057), buzzer=D21 (PWM),
  light sensor=D1 (ADC), CN2 (PIR)=D20, CN3 (RC servo)=D7, CN5 (HC-SR04)
  TRIG=D4/ECHO=D5.
- Verified OLED, NeoPixel, and buzzer wiring (roadmap task 4) against the
  manual's working MicroPython code examples (I2C at scl=9/sda=8 for a
  128x64 SSD1306; NeoPixel on pin 10; buzzer via `machine.PWM` on pin 21).
- Added `firmware/boot.py` and Stage 3 test scripts
  (`test_oled.py`, `test_neopixel.py`, `test_buzzer.py`, `test_servo.py`)
  for roadmap tasks 17-20, matching the confirmed pin map. `test_servo.py`
  drives the CN3 RC servo header (pin D7) to the exact window angles used by
  `logic/decision.py` (10/90/170 degrees).
- Corrected branch 10 (Actuator abstraction) status to `implemented`: this
  was already true from the prior session's `logic/actuator_state.py` but
  had not been reflected in `data/progress-baseline.json`.
- Advanced branch 11 (Physical outputs) to `drafted`: test source exists but
  is unverified on physical hardware.

Source of hardware facts (previous session):

- `ESP32-C3M-TRY-R1-20230701.pdf` ("ESP32-C3M-TRY 取扱説明書"), MicroFan,
  2023-07-01, provided directly by the project owner.

Evidence (previous session):

- Manual sections 1.1, 2.1-2.8, and 5.1-5.3 (board overview, peripheral
  descriptions, schematic, and pin table) cited directly for the board
  identity and pin map above.
- The MicroPython scripts referenced here were syntax-checked and later
  deleted; see "Changed" above for the PlatformIO/C++ replacements.

Status updates (previous session, superseded above):

- Roadmap tasks 1, 3, 4 marked `done` (still current).
- Branch 10 corrected to `implemented`; branch 11 advanced to `drafted`
  (still current).

Date: 2026-08-04 JST (Stage 2 pure logic)

Agent: agent-03-logic (Claude Sonnet 5).

Changed:

- Added `logic/canonical.py`: `SensorReading` / `SensorState` matching the
  blueprint's canonical sensor record schema (name, value, unit, source,
  quality, received_at_ms, valid) and `SourceMode` (virtual/physical/hybrid/
  disabled).
- Added `logic/system_state.py`: `SystemState` with an explicit
  `Mode` transition graph (`BOOT -> CONNECTING -> READY -> AUTOMATIC ->
  WARNING/SAFE/FAULT -> RECOVERY -> AUTOMATIC`) that raises
  `InvalidModeTransition` on any transition outside the documented chain,
  instead of relying on independent boolean flags.
- Added `logic/actuator_state.py`: `ActuatorState` keeping requested,
  commanded, simulated, measured, and fault evidence separate.
- Added `logic/decision.py`: stateful decision engine implementing the
  blueprint's temperature rules (`<=28 C` fan off / window closed, `28-35 C`
  fan on / window half, `>35 C` fan on / window full) and irrigation
  hysteresis rules (moisture `<30%` + no rain -> pump on, `>40%` -> pump off,
  otherwise hold previous state). Returns triggered rule IDs and human
  reasons. Contains no GPIO/PWM/Wi-Fi/HTTP/browser calls.
- Added `logic/safety.py`: safety supervisor implementing the documented
  priority order (Emergency > Safety > Equipment protection > Automatic
  operation) and safe-state matrix (startup, valid operation, low tank,
  stale data, controller fault, emergency stop). Only narrows/overrides
  decision output; never recomputes requested actions.
- Added `tests/` (stdlib `unittest`, no external dependencies): 35 tests
  covering normal conditions (task 13), exact boundaries (task 14),
  conflicting rules (task 15), and stateful sequences (task 16), including
  the blueprint's own worked examples (moisture sequence `50 -> 20 -> 35 ->
  45%`; conflict example "dry soil -> pump ON, tank below 15% -> pump OFF").
- Updated `data/progress-baseline.json` and the dashboard's embedded
  baseline in `web-build/index.html`: tasks 9-16 -> `done`; branches 6
  (Sensor abstraction), 7 (State management), 8 (Decision engine), 9 (Safety
  supervisor) -> `implemented` (not yet `verified`, since firmware/hardware
  integration for these branches has not happened).

Design decisions made explicit (not hardware facts, so not blockers, but
worth a future owner review):

- Tank-level gating for the pump is implemented only in the safety
  supervisor, not duplicated in the decision engine's irrigation rule. The
  blueprint's own worked conflict example ("Decision engine: dry soil ->
  pump ON. Safety supervisor: tank below 15% -> pump OFF.") only makes sense
  if the decision engine's pump-on rule does not itself check tank level;
  this keeps decision and safety strictly separate per the blueprint's
  Stage 2 instruction.
- "Safe angle" (stale data / controller fault / emergency stop) defaults to
  the closed window angle (10 deg), matching the blueprint's own startup
  default. "Configured safe fan state" defaults to off and is an explicit
  parameter of `evaluate_safety`, not a hardcoded guess.

Blueprint area (this session):

- Stage 2: Pure logic.
- Branch 6: Sensor abstraction.
- Branch 7: State management.
- Branch 8: Decision engine.
- Branch 9: Safety supervisor.
- Control-loop steps 4-7 (update canonical sensor state, calculate requested
  actions, apply safety priorities, generate final commands).

Evidence (this session):

- `python3 -m unittest discover -s tests -v` -> 35 tests, all passed
  (0 failures, 0 errors).
- Manual review confirmed no `gpio`, `machine.`, `network.`, `socket`, or
  `http` references inside `logic/` (only doc-comment mentions describing
  what the package deliberately avoids).
- Dashboard (`web-build/index.html`) baseline updated in the same commit as
  the public JSON mirrors; deployed and verified HTTP 200 (see Deployment
  Notes below).

Status updates (this session):

- Roadmap tasks 9-16 marked `done`.
- Branches 6 (Sensor abstraction), 7 (State management), 8 (Decision engine),
  9 (Safety supervisor) marked `implemented`.
- Overall/roadmap/branch/control-loop percentages recomputed from the
  updated task and branch statuses (see Current Progress Snapshot above).

Older changes (previous sessions):

- Created the public task-management dashboard at
  `https://phyowaisoe.com/agricontrol/taskmanagement/`.
- Hosted the blueprint PDF beside the dashboard.
- Pushed the initial source to GitHub on branch `main`.
- Added this AI continuity system so future models can resume systematically.
- Added the prompt and test library so future models have task-level,
  stage-level, branch-level, gate-level, and workflow-level prompts.
- Added a dashboard communication report feature that can explain what is not
  done, where owner help is needed, what is unknown, and what is blocked in
  multiple-choice, long-text, or structured handoff formats.
- Added a multi-agent coordination layer showing which AI model is doing what,
  what each role has done, what comes next, and where owner help is needed.
- Added owner and AI-agent guides for using the infrastructure.

Blueprint area (older sessions):

- Product definition.
- Roadmap reporting.
- Branch readiness reporting.
- Completion gate reporting.
- Central control-loop reporting.
- Prompt and test library for all blueprint stages, branches, tasks, gates, and
  reusable verification workflows.
- Owner communication reporting for open work, help requests, unknowns, and
  blockers.
- Multi-agent coordination and handoff reporting.

Evidence (older sessions):

- Public dashboard returned HTTP 200 after deployment.
- Public blueprint PDF returned HTTP 200 after deployment.
- Dashboard inline JavaScript parsed successfully.
- GitHub `main` was updated with the initial dashboard source.
- Prompt library generated 82 task prompts, 12 stage packs, 16 branch packs, 5
  gate prompts, and 7 reusable test workflows.
- Public prompt library Markdown returned HTTP 200 after deployment.
- Public prompt library JSON returned HTTP 200 after deployment.
- Dashboard communication report JavaScript parsed successfully.
- Agent registry JSON was added and mirrored to the public dashboard bundle.
- User and AI-agent guides were added and mirrored to the public dashboard
  bundle.

Status updates (older sessions, superseded above where noted):

- Product definition is marked `verified`.
- Protocol, observability, and testing are marked `drafted`.
- Roadmap steps 5-8 are marked `done`.

## Known Unknowns

These must not be guessed:

- Exact RC servo model at CN3 (power source stability is confirmed; the
  model itself is not recorded).
- Pump and fan GPIO/relay pin assignment (not built into the ESP32-C3M-TRY
  eval board; this is new wiring specific to the AgriControl greenhouse
  build, not something the board's manual answers).
- Exact `platform-espressif32` and Arduino-ESP32 core versions in use, to
  pin in `firmware/platformio.ini` for reproducible builds.
- Real WiFi credentials for `firmware/include/secrets.h`.
- Whether the placeholder runtime tuning constants (10s stale-data timeout,
  5-message recovery threshold, 2048-byte max request body) are acceptable.

Resolved: exact board, complete pin map, OLED/NeoPixel/buzzer wiring
(sourced from the owner-provided `ESP32-C3M-TRY-R1-20230701.pdf`); firmware
toolchain (PlatformIO, Arduino framework, C++ -- not MicroPython); servo
power stability (roadmap task 23). See Completed Work above.

## Next Work

Stage 2 (Pure logic, tasks 9-16) is done: `logic/` implements canonical
sensor state, system/actuator state, the stateful decision engine, and the
safety supervisor, verified by 35 passing host-runnable tests in `tests/`.

Stage 1 (tasks 1-4) is fully done. Stage 3 (Local physical outputs): servo
tasks (20, 23) are done from direct hardware observation; OLED/NeoPixel/
buzzer/combined-output test environments are drafted in `firmware/`
(PlatformIO) but unverified by a build or hardware run. Stage 4 (ESP
runtime, tasks 24-30) is drafted in `firmware/src/runtime.cpp` and
`include/`, also unverified -- it has never been through `pio run`.

Follow the blueprint order. The next open tasks are:

1. Build and upload `firmware/`'s `test_oled`, `test_neopixel`, and
   `test_buzzer` PlatformIO environments on the physical board and record
   the results as evidence (roadmap tasks 17-19, `active`).
2. Build and upload `env:test_all_outputs` (roadmap task 21, `active`,
   drafted) once 17-19 have hardware evidence.
3. Connect hardcoded decisions to outputs (roadmap task 22) - needs the
   owner to first answer the pump/fan pin question in
   `data/agent-coordination.json` (`agent-02-hardware`), since this board has
   no built-in pump/fan output.
4. Get `env:runtime` actually building (roadmap tasks 24-30, `active`,
   drafted): fix whatever compile errors turn up, add real WiFi credentials
   to `firmware/include/secrets.h`, and test `POST /sensor` against the
   real board (e.g. with `curl`).

Before starting a task, use the matching prompt in
`docs/PROMPT_TEST_LIBRARY.md` and the matching verification prompt before
marking progress complete.

Use the dashboard's Communication Report section to ask the owner for hardware
facts or decisions in multiple-choice, long-text, or structured handoff form.

Use the dashboard's AI Agent Board to record which model is assigned to each
role, what it is doing, what it has done, and whether it needs owner input.

## Deployment Notes

Production server path:

```text
/var/www/html/agricontrol/taskmanagement/
```

Deployment command:

```bash
rsync -avz --delete --rsync-path='sudo rsync' web-build/ phyowaisoe-server:/var/www/html/agricontrol/taskmanagement/
```

Verification commands:

```bash
curl -I -L --max-time 20 https://phyowaisoe.com/agricontrol/taskmanagement/
curl -I -L --max-time 20 https://phyowaisoe.com/agricontrol/taskmanagement/ESP32_Virtual_Control_Lab_Blueprint.pdf
curl -I -L --max-time 20 https://phyowaisoe.com/agricontrol/taskmanagement/data/progress-baseline.json
curl -I -L --max-time 20 https://phyowaisoe.com/agricontrol/taskmanagement/data/agent-coordination.json
curl -I -L --max-time 20 https://phyowaisoe.com/agricontrol/taskmanagement/docs/USER_GUIDE.md
curl -I -L --max-time 20 https://phyowaisoe.com/agricontrol/taskmanagement/docs/AI_AGENT_GUIDE.md
curl -I -L --max-time 20 https://phyowaisoe.com/agricontrol/taskmanagement/docs/PROMPT_TEST_LIBRARY.md
curl -I -L --max-time 20 https://phyowaisoe.com/agricontrol/taskmanagement/data/prompt-test-library.json
```
