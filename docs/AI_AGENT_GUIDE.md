# AgriControl AI Agent Guide

Last updated: 2026-08-04 JST

This guide is for AI models cooperating on AgriControl.

## Mission

Continue the ESP32 Virtual Control Lab systematically. The first complete
release must prove the connected loop from website sensor input, through
FastAPI and ESP32 decision/safety logic, to physical and virtual outputs,
feedback, observability, and automated verification.

## Required Read Order

Before editing or changing status, read:

1. `AGENTS.md`
2. `ESP32_Virtual_Control_Lab_Blueprint.pdf`
3. `docs/PROJECT_STATE.md`
4. `docs/AI_CONTINUITY_SYSTEM.md`
5. `docs/PROMPT_TEST_LIBRARY.md`
6. `data/progress-baseline.json`
7. `data/agent-coordination.json`
8. `web-build/index.html` if dashboard behavior is affected

## Coordination Protocol

1. Pick one agent role from `data/agent-coordination.json`.
2. Claim one narrow scope.
3. Record model name, status, current work, done work, next work, and owner
   needs.
4. Use the prompt ID that matches the current task.
5. Implement the smallest coherent slice.
6. Verify with the matching test prompt.
7. Update durable project state only when evidence exists.
8. Mirror public docs/data into `web-build/docs` and `web-build/data`.
9. Deploy and push when public reporting or source changes.

## Status Rules

Use these status values:

- `ready`: Role can start when assigned.
- `active`: Model is currently working on the named scope.
- `needs_owner`: Owner input is required.
- `blocked`: Work cannot progress without a named blocker being resolved.
- `review`: Work is complete enough for verification.
- `done`: Work is complete and evidence is recorded.

Do not use vague status labels. Do not mark `done` without evidence.

## Architecture Rules

- The ESP32 remains the control authority.
- Browser and FastAPI components coordinate, display, simulate, store, replay,
  and verify.
- Browser and FastAPI components do not decide actuator behavior.
- Sensor inputs become canonical sensor state before decision logic reads them.
- Decision engine requests actions.
- Safety supervisor has final authority over every command.
- Actuator state must keep requested, commanded, simulated, measured, and fault
  evidence separate.
- Important events must be logged as structured events.

## File Update Rules

When agent assignments change:

- Update `data/agent-coordination.json`.
- Mirror it to `web-build/data/agent-coordination.json`.
- Update `docs/PROJECT_STATE.md` when the project state changes.
- Mirror public docs to `web-build/docs`.

When progress changes:

- Update `data/progress-baseline.json`.
- Update `docs/PROJECT_STATE.md`.
- Use `docs/PROMPT_TEST_LIBRARY.md` before changing any status.

When dashboard behavior changes:

- Update `web-build/index.html`.
- Validate the inline script.
- Verify public URLs after deployment.

## Handoff Format

Every agent should leave this handoff:

```text
Agent ID:
Model:
Status:
Scope:
Doing now:
Done this session:
Evidence:
Needs owner:
Owner questions:
Next recommended agent:
Next task:
```

## Conflict Avoidance

- Do not edit unrelated files.
- Do not overwrite another agent's work without reading it.
- If the same branch, file, or task is already active, review that work before
  continuing.
- If owner facts are missing, ask through the Communication Report instead of
  guessing.

## Verification Minimums

Dashboard-only changes:

- Inline JavaScript parses.
- JSON files parse.
- Desktop and mobile layout checks pass when possible.
- Public URLs return HTTP 200 after deployment.

Firmware/backend/frontend work:

- Unit, boundary, sequence, integration, failure, endurance, or replay tests as
  required by the prompt library.
- Evidence must be written into project state before progress is advanced.

