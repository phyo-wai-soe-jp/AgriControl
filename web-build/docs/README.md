# AgriControl

AgriControl is the project workspace for an ESP32 Virtual Control Lab: a
digital-twin and hardware-in-the-loop control platform for a greenhouse-style
controller.

Public progress dashboard:

https://phyowaisoe.com/agricontrol/taskmanagement/

## Source Of Truth

The project is guided by `ESP32_Virtual_Control_Lab_Blueprint.pdf`. The core
design rule is that no interface, sensor, actuator, or communication method may
bypass the central control loop.

## Repository Map

- `ESP32_Virtual_Control_Lab_Blueprint.pdf` - complete system blueprint.
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
- `logic/` - host-runnable pure logic: canonical sensor state, system and
  actuator state, the stateful decision engine, and the safety supervisor.
- `tests/` - unit, boundary, conflict, and sequence tests for `logic/`
  (`python3 -m unittest discover -s tests`).
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
