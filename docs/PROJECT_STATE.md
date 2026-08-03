# AgriControl Project State

Last updated: 2026-08-04 JST

## Live Links

- Public dashboard: https://phyowaisoe.com/agricontrol/taskmanagement/
- GitHub repository: https://github.com/phyo-wai-soe-jp/AgriControl.git
- Blueprint PDF: `ESP32_Virtual_Control_Lab_Blueprint.pdf`
- Public blueprint PDF: https://phyowaisoe.com/agricontrol/taskmanagement/ESP32_Virtual_Control_Lab_Blueprint.pdf

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

## Current Progress Snapshot

Baseline progress is intentionally conservative:

- Overall progress: 11%
- Roadmap execution: 6%
- Branch readiness: 22%
- Completion gates: 0%
- Central control-loop coverage: 18%

These numbers come from the blueprint-derived model in
`data/progress-baseline.json`. Browser-local edits on the public dashboard do
not change durable project state until they are exported and committed.

## Completed Work

Date: 2026-08-04 JST

Changed:

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

Blueprint area:

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

Evidence:

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

Status updates:

- Product definition is marked `verified`.
- Protocol, sensor abstraction, state management, decision engine, safety
  supervisor, observability, and testing are marked `drafted`.
- Roadmap steps 5-8 are marked `done`.
- Roadmap steps 9-12 are marked `active`.

## Known Unknowns

These must not be guessed:

- Exact ESP32-C3 board.
- MicroPython version.
- Complete pin map.
- OLED, NeoPixel, buzzer, and servo wiring verification.
- Real hardware power behavior, especially servo power stability.

## Next Work

Follow the blueprint order. The next open tasks are:

1. Confirm the exact ESP32-C3 board.
2. Record the MicroPython version.
3. Create the complete pin map.
4. Verify OLED, NeoPixel, buzzer, and servo wiring.
5. Finish canonical sensor, system state, decision engine, and safety
   supervisor structures.

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
