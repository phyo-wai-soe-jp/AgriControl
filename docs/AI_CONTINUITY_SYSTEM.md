# AI Continuity System

Last updated: 2026-08-04 JST

This file exists so another AI model can continue AgriControl systematically
without relying on conversation memory.

## Objective

Build an ESP32-C3 digital-twin and hardware-in-the-loop greenhouse control lab.
The first complete release must prove a connected loop from website sensor
input, through FastAPI and ESP32 decision/safety logic, to physical and virtual
outputs, feedback, observability, and automated verification.

## Non-Negotiable Architecture

The ESP32 is the control authority.

The browser simulates the environment. FastAPI coordinates communication,
sessions, logs, replay, and tests. Neither the browser nor FastAPI should take
over decision or safety authority.

All future implementation must preserve this flow:

1. Sensor conditions are created manually or by scenario.
2. A versioned sensor message is transmitted.
3. Protocol, session, sequence, fields, types, and ranges are validated.
4. Authoritative canonical sensor state is updated.
5. The stateful decision engine calculates requested actions.
6. The safety supervisor applies priorities and overrides.
7. Final actuator commands are generated.
8. Physical and virtual outputs are applied.
9. Simulated or measured actuator feedback is received.
10. Success, delay, mismatch, or failure is detected.
11. OLED, LED, buzzer, event history, and test result are updated.
12. The runtime repeats without blocking safety or output tasks.

## Agent Start Procedure

At the beginning of every continuation session:

1. Check `git status --short --branch`.
2. Read `AGENTS.md`.
3. Read `docs/PROJECT_STATE.md`.
4. Read `data/progress-baseline.json`.
5. Read `docs/AI_AGENT_GUIDE.md`.
6. Read `data/agent-coordination.json`.
7. Read `docs/PROMPT_TEST_LIBRARY.md`.
8. Read `data/prompt-test-library.json` when a machine-readable task prompt is
   useful.
9. Open or inspect `web-build/index.html` if reporting or dashboard behavior is
   affected.
10. Choose the next task from the roadmap, preferring the earliest open task on
   the critical path.

Do not guess hardware facts. If the exact board, MicroPython version, pin map,
or wiring evidence is missing, keep the relevant task open or blocked.

## Systematic Work Cycle

For each work session:

1. Select one blueprint stage and one small objective.
2. Claim or update one agent role in `data/agent-coordination.json`.
3. Select the matching prompt IDs from `docs/PROMPT_TEST_LIBRARY.md`.
4. Name the affected branch IDs, gate IDs, and control-loop steps.
5. Implement the smallest useful change.
6. Add or update verification evidence using the matching test prompts.
7. Update progress statuses only when evidence exists.
8. Record blockers and assumptions in `docs/PROJECT_STATE.md`.
9. Update `data/progress-baseline.json` and `data/agent-coordination.json` when
   durable status changes.
10. Regenerate `docs/PROMPT_TEST_LIBRARY.md` and
   `data/prompt-test-library.json` with
   `node tools/generate-prompt-test-library.mjs` if the roadmap, branches,
   gates, or test model changes.
11. Copy public docs/data into `web-build/docs/` and `web-build/data/`.
12. Deploy the static dashboard when public reporting changes.
13. Commit and push to GitHub.

## Indicator Model

Roadmap and gate status weights:

- `todo`: 0
- `active`: 0.45
- `blocked`: 0.15
- `done`: 1

Branch readiness weights:

- `planned`: 0
- `drafted`: 0.35
- `implemented`: 0.7
- `verified`: 1

Overall progress is the average of:

- Roadmap execution.
- Branch readiness.
- Completion gates.
- Control-loop coverage.

The dashboard currently stores browser edits in local storage. Durable changes
must be reflected in repository files.

## Current Critical Path

Follow the blueprint order. The early critical path is:

Requirements -> Contracts -> Decision and safety logic -> Physical drivers ->
ESP communication -> First vertical slice -> Scenario verification ->
Reliability -> Expansion

Avoid user accounts, cloud database, MQTT, multi-device support, AI
recommendations, SaaS packaging, and advanced animations until the first proven
control loop is stable.

## Definition Of Done

A task can be marked `done` only when there is evidence in the repo, hardware
notes, test output, or a public deployment.

A branch can be marked `implemented` only when working source exists.

A branch can be marked `verified` only when tests, hardware checks, or public
behavior confirm the intended responsibility.

A gate criterion can be marked `done` only when the behavior has been tested
against the blueprint acceptance statement.

## Handoff Template

Use this format in `docs/PROJECT_STATE.md` after meaningful work:

```text
Date:
Changed:
Blueprint area:
Evidence:
Status updates:
Blockers:
Next task:
```

## Public Reporting Checklist

When the dashboard or public handoff files change:

1. Validate `web-build/index.html` script syntax.
2. Ensure these public files exist:
   - `web-build/index.html`
   - `web-build/ESP32_Virtual_Control_Lab_Blueprint.pdf`
   - `web-build/docs/AI_CONTINUITY_SYSTEM.md`
   - `web-build/docs/PROJECT_STATE.md`
   - `web-build/docs/USER_GUIDE.md`
   - `web-build/docs/AI_AGENT_GUIDE.md`
   - `web-build/docs/PROMPT_TEST_LIBRARY.md`
   - `web-build/data/progress-baseline.json`
   - `web-build/data/agent-coordination.json`
   - `web-build/data/prompt-test-library.json`
3. Deploy `web-build/` to `/var/www/html/agricontrol/taskmanagement/`.
4. Verify the public URLs return HTTP 200.
5. Commit and push.
