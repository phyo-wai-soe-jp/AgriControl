# AgriControl Agent Instructions

This repository is the public project workspace for AgriControl, based on the
`ESP32 Virtual Control Lab - Complete System Blueprint`.

## Read First

Before changing project status, source, firmware, backend code, or the hosted
dashboard, read these files in order:

1. `ESP32_Virtual_Control_Lab_Blueprint.pdf`
2. `docs/PROJECT_STATE.md`
3. `docs/AI_CONTINUITY_SYSTEM.md`
4. `docs/PROMPT_TEST_LIBRARY.md`
5. `data/progress-baseline.json`
6. `data/prompt-test-library.json`
7. `web-build/index.html`

## Core Rule

Do not bypass the central control loop.

Every input must become canonical sensor state. Every requested action must pass
through the safety supervisor. Every final output must produce observable events.
The ESP32 remains the control authority; browser and FastAPI components
coordinate, display, record, replay, and verify.

## Current Project Shape

- Public dashboard: `https://phyowaisoe.com/agricontrol/taskmanagement/`
- GitHub repository: `https://github.com/phyo-wai-soe-jp/AgriControl.git`
- Hosted server path: `/var/www/html/agricontrol/taskmanagement/`
- Static site source: `web-build/`
- Machine-readable baseline: `data/progress-baseline.json`
- Prompt and test library: `docs/PROMPT_TEST_LIBRARY.md`
- Machine-readable prompt catalog: `data/prompt-test-library.json`
- Public machine-readable baseline: `web-build/data/progress-baseline.json`
- Public prompt and test library: `web-build/docs/PROMPT_TEST_LIBRARY.md`
- Public machine-readable prompt catalog: `web-build/data/prompt-test-library.json`
- Public handoff docs: `web-build/docs/`
- Prompt library generator: `tools/generate-prompt-test-library.mjs`

## Status Vocabulary

Roadmap tasks and gate criteria use:

- `todo`: Not started.
- `active`: Work is in progress or ready for the next implementation pass.
- `blocked`: Known blocker exists and must be named in `docs/PROJECT_STATE.md`.
- `done`: Implemented and verified enough for the current stage.

Branches use:

- `planned`: Defined by the blueprint only.
- `drafted`: Specification, interface, or design exists.
- `implemented`: Working source exists.
- `verified`: Tests or real checks confirm behavior.

## Required Update Cycle

When continuing this project:

1. Read the latest GitHub state and local working tree.
2. Read the blueprint and current project state.
3. Read the prompt and test library.
4. Identify the next open task from the 82-step roadmap.
5. Use the matching task, stage, branch, gate, and test workflow prompts.
6. Implement only the smallest coherent slice needed for that task.
7. Keep branch boundaries explicit.
8. Update `docs/PROJECT_STATE.md` with date, status, evidence, and blockers.
9. Update `data/progress-baseline.json` when statuses change.
10. Regenerate or update the prompt library if the roadmap changes:
    `node tools/generate-prompt-test-library.mjs`.
11. Mirror public docs/data into `web-build/docs/` and `web-build/data/`.
12. Validate the static site and any new code.
13. Deploy `web-build/` to the server and push the commit to GitHub.

## Validation Baseline

For dashboard-only changes, at minimum:

- Parse the inline script in `web-build/index.html`.
- Verify the public page returns HTTP 200 after deployment.
- Verify the hosted blueprint PDF, progress JSON, and prompt library return HTTP
  200.

For future firmware/backend work, tests must map to blueprint gates and include
the relevant exact boundaries, failure cases, and recovery behavior.

## Deployment

The current production site is a static folder served by nginx.

Deploy with:

```bash
rsync -avz --delete --rsync-path='sudo rsync' web-build/ phyowaisoe-server:/var/www/html/agricontrol/taskmanagement/
```

Then verify:

```bash
curl -I -L --max-time 20 https://phyowaisoe.com/agricontrol/taskmanagement/
```

## Handoff Standard

Every meaningful change should leave enough evidence for a future agent:

- What changed.
- Why it changed.
- Which blueprint branch, stage, gate, or control-loop step it affects.
- How it was verified.
- What remains next.
