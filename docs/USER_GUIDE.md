# AgriControl User Guide

Last updated: 2026-08-04 JST

This guide explains how to use the AgriControl project infrastructure as the
project owner.

## Main Links

- Dashboard: https://phyowaisoe.com/agricontrol/taskmanagement/
- GitHub: https://github.com/phyo-wai-soe-jp/AgriControl.git
- Blueprint: https://phyowaisoe.com/agricontrol/taskmanagement/ESP32_Virtual_Control_Lab_Blueprint.pdf
- Project state: https://phyowaisoe.com/agricontrol/taskmanagement/docs/PROJECT_STATE.md
- Prompt and test library: https://phyowaisoe.com/agricontrol/taskmanagement/docs/PROMPT_TEST_LIBRARY.md
- AI model guide: https://phyowaisoe.com/agricontrol/taskmanagement/docs/AI_AGENT_GUIDE.md
- Agent coordination data: https://phyowaisoe.com/agricontrol/taskmanagement/data/agent-coordination.json

## What The Dashboard Does

The dashboard reports project progress from the blueprint:

- Roadmap progress across 82 tasks.
- Readiness across 16 project branches.
- Gate A-E completion criteria.
- Central control-loop coverage.
- AI continuity resources.
- Communication reports for questions to you.
- AI agent coordination showing which model is doing what and what is done.

## How To Use The Agent Board

Open the dashboard and go to **AI Agents**.

Each row or card shows:

- Agent role.
- Model name.
- Status.
- Current work.
- Done work.
- Next work.
- Whether your help is needed.

You can edit the model, status, current work, done work, and next work in the
dashboard. These edits are saved in your browser. To make them durable for every
future AI model, export or copy the information and ask an AI model to update
`data/agent-coordination.json`, `docs/PROJECT_STATE.md`, and the public site.

## How To Answer AI Questions

Use the **Communication Report** section when the project needs your help.

It can show:

- Multiple-choice questions.
- Long-text report.
- Structured handoff message.

Good answers include exact facts:

- Exact ESP32-C3 board model.
- MicroPython version.
- Pin map.
- Hardware wiring status.
- Servo power test result.
- Which task or agent should go next.

## What Is Local And What Is Durable

Dashboard edits are local to your browser unless exported or committed.

Durable project state lives in GitHub and public files:

- `docs/PROJECT_STATE.md`
- `data/progress-baseline.json`
- `data/agent-coordination.json`
- `docs/PROMPT_TEST_LIBRARY.md`
- `docs/AI_AGENT_GUIDE.md`

If you change status in the browser and want every AI model to see it, tell the
next AI model to copy the dashboard state into the durable files and push it.

## How To Bring Another AI Model Into The Project

Give the model this instruction:

```text
Continue the AgriControl project. First read AGENTS.md, docs/AI_AGENT_GUIDE.md,
docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md,
docs/PROMPT_TEST_LIBRARY.md, data/progress-baseline.json, and
data/agent-coordination.json. Then claim one narrow agent role, update the
agent board, and work only on the next unblocked blueprint task.
```

If the model cannot access GitHub, give it the public dashboard links above.

## How To Keep The Project Healthy

- Keep the ESP32 as the control authority.
- Do not let browser or FastAPI code decide actuator behavior.
- Do not mark tasks done without evidence.
- Ask for your help when hardware facts are unknown.
- Keep dashboard, public docs, and GitHub synchronized.
- Use the prompt and test library before implementation and verification.

