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
- `data/progress-baseline.json` - machine-readable blueprint progress model.
- `AGENTS.md` - instructions for coding agents working in this repo.

## Current Progress Model

The dashboard tracks:

- 12 blueprint development stages.
- 82 roadmap tasks.
- 16 architecture branches.
- 12 central control-loop steps.
- Gate A-E completion criteria.

Progress edits in the browser are saved locally unless exported. Durable status
updates should be written back to `data/progress-baseline.json` and
`docs/PROJECT_STATE.md`.

## Continue The Project

Start with `AGENTS.md`, then read `docs/PROJECT_STATE.md` and
`docs/AI_CONTINUITY_SYSTEM.md`. Work through the blueprint roadmap in order,
starting with the first open task that unlocks the next vertical slice.

