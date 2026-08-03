# AgriControl Project State

Last updated: 2026-08-04 JST (Stage 1 hardware facts + Stage 3 firmware drafts)

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
- `firmware/` - MicroPython source for the physical ESP32-C3M-TRY board:
  `boot.py` and Stage 3 output test scripts, unverified on hardware.

## Current Progress Snapshot

Baseline progress is intentionally conservative:

- Overall progress: 26%
- Roadmap execution: 21%
- Branch readiness: 37%
- Completion gates: 0%
- Central control-loop coverage: 45%

These numbers come from the blueprint-derived model in
`data/progress-baseline.json`. Browser-local edits on the public dashboard do
not change durable project state until they are exported and committed.

## Completed Work

Date: 2026-08-04 JST (Stage 1 hardware facts + Stage 3 firmware drafts)

Agent: agent-02-hardware (Claude Sonnet 5).

Changed:

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

Source of hardware facts:

- `ESP32-C3M-TRY-R1-20230701.pdf` ("ESP32-C3M-TRY 取扱説明書"), MicroFan,
  2023-07-01, provided directly by the project owner.

Evidence:

- Manual sections 1.1, 2.1-2.8, and 5.1-5.3 (board overview, peripheral
  descriptions, schematic, and pin table) cited directly for the board
  identity and pin map above.
- `firmware/*.py` syntax-checked with `python3 -m py_compile` (MicroPython
  modules such as `machine`, `neopixel`, and `ssd1306` cannot be imported or
  executed outside the physical device, so this confirms syntax only, not
  on-hardware behavior).

Status updates:

- Roadmap tasks 1, 3, 4 marked `done`.
- Roadmap task 2 marked `active`: the manual's example firmware version
  (`v1.20.0`, dated 2023-07) is not proof of what is actually flashed on the
  physical unit today; needs an on-device check.
- Roadmap tasks 17-20 marked `active`: source drafted, awaiting on-hardware
  verification and evidence.
- Branch 10 corrected to `implemented`; branch 11 advanced to `drafted`.

Blockers (owner input needed, tracked in `data/agent-coordination.json` under
`agent-02-hardware`):

1. Confirm the MicroPython version actually running on the board:
   `import sys; print(sys.implementation)` in the Thonny REPL.
2. Which RC servo model is attached to CN3 (pin D7), and is it powered
   separately from the USB 5V rail? (Roadmap task 23 - servo power must not
   reset the ESP - cannot be assessed from the manual, which only documents
   the bare 3-pin header.)
3. Which spare GPIO/relay will drive the greenhouse pump and fan? This eval
   board has no built-in pump or fan output, so this is new wiring, not
   something the manual answers.

Next task: run `firmware/test_oled.py`, `test_neopixel.py`, `test_buzzer.py`,
and `test_servo.py` on the physical board via Thonny, capture the observed
output as evidence, and answer the three blockers above before advancing
Stage 3 further (tasks 21-23).

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

- MicroPython version actually flashed on the physical unit (the owner's
  manual only documents the version available when it was written, 2023-07).
- Exact RC servo model and power source used at CN3.
- Pump and fan GPIO/relay pin assignment (not built into the ESP32-C3M-TRY
  eval board; this is new wiring specific to the AgriControl greenhouse
  build, not something the board's manual answers).
- Real hardware power behavior, especially servo power stability
  (roadmap task 23).

Resolved this session, sourced from the owner-provided
`ESP32-C3M-TRY-R1-20230701.pdf`: exact board, complete pin map, and
OLED/NeoPixel/buzzer wiring. See Completed Work above.

## Next Work

Stage 2 (Pure logic, tasks 9-16) is done: `logic/` implements canonical
sensor state, system/actuator state, the stateful decision engine, and the
safety supervisor, verified by 35 passing host-runnable tests in `tests/`.

Stage 1 hardware facts (tasks 1, 3, 4) are done, sourced from the owner's
ESP32-C3M-TRY manual. Stage 3 (Local physical outputs) test scripts are
drafted in `firmware/` for tasks 17-20 but unverified on hardware.

Follow the blueprint order. The next open tasks are:

1. Record the MicroPython version actually on the physical board. (`active`,
   `needs_owner`: run `import sys; print(sys.implementation)` in Thonny.)
2. Run `firmware/test_oled.py`, `test_neopixel.py`, `test_buzzer.py`, and
   `test_servo.py` on the physical board and record the results as evidence
   (roadmap tasks 17-20, `active`).
3. Test all outputs together (roadmap task 21) once 17-20 have hardware
   evidence.
4. Connect hardcoded decisions to outputs (roadmap task 22) and confirm
   servo power does not reset the ESP (roadmap task 23) - both need the
   owner to first answer the RC servo model/power and pump/fan pin
   questions in `data/agent-coordination.json` (`agent-02-hardware`).

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
