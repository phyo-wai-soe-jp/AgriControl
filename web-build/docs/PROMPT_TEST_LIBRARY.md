# AgriControl Prompt And Test Library

Last updated: 2026-08-04 JST

This library gives future AI models a complete set of structured prompts and verification prompts for finishing AgriControl from the blueprint. It is intentionally tied to the 12 stages, 16 branches, 82 roadmap tasks, central control loop, and Gate A-E completion criteria.

## How To Use

- Run GLOBAL-ORIENT-001 at the start of a new AI session.
- Choose the earliest unblocked task from data/progress-baseline.json.
- Use the matching TASK prompt for implementation.
- Use the matching TASK test prompt plus relevant TEST-WF prompts for verification.
- Use branch and gate prompts when a branch status or gate criterion may advance.
- Use GLOBAL-STATE-001 and GLOBAL-DEPLOY-001 before handoff, deployment, and GitHub push.

## Universal Constraints

- The ESP32 remains the control authority.
- Browser and FastAPI components coordinate, simulate, display, log, replay, and verify; they do not decide actuator behavior.
- Inputs must become canonical sensor state before decision logic reads them.
- Decision logic requests actions; safety supervisor produces final commands.
- Actuator state must distinguish requested, commanded, simulated, measured, and fault evidence.
- Every meaningful branch must emit structured events.
- Do not mark progress done without evidence.

## Global Prompts

### GLOBAL-ORIENT-001 - Project Orientation Prompt

Implementation prompt:

```text
You are continuing AgriControl, an ESP32-C3 digital-twin and hardware-in-the-loop greenhouse control lab.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, data/prompt-test-library.json, and the blueprint PDF before editing.
Summarize the current stage, first open roadmap task, affected branches, known blockers, and the next smallest implementation slice.
Do not make assumptions about hardware facts that are not recorded. Do not bypass the central control loop.
```

Test prompt:

```text
Verify that the orientation summary cites repository files, chooses the earliest useful open task, and does not invent board, wiring, or firmware facts.
```

Expected output:

- Current status summary
- Next task choice
- Affected blueprint branches and gates
- Risk and blocker list

### GLOBAL-IMPLEMENT-001 - Single-Slice Implementation Prompt

Implementation prompt:

```text
Select one blueprint roadmap task or one tightly related group of tasks.
Implement only the smallest coherent slice needed to move that task forward.
Preserve the branch boundaries: communication moves data, sensor abstraction normalizes inputs, decision requests actions, safety creates final commands, actuator manager applies outputs, observability records events.
Add tests or evidence appropriate to the risk. Update docs/PROJECT_STATE.md and data/progress-baseline.json only for statuses supported by evidence.
```

Test prompt:

```text
Review the diff and confirm the change is scoped to one slice, includes evidence, preserves ESP control authority, and updates durable state only when justified.
```

Expected output:

- Source changes
- Verification evidence
- Status updates
- Next task recommendation

### GLOBAL-TEST-001 - Independent Verification Prompt

Implementation prompt:

```text
Act as a verification agent for AgriControl.
Read the blueprint, current project state, progress baseline, and changed files.
Create and run the most relevant tests for the touched branches and gates.
Report pass/fail results, exact commands or hardware observations, uncovered risks, and whether any status may be advanced.
```

Test prompt:

```text
Check that the verification covers normal behavior, boundaries, failure paths, stale data or recovery when relevant, and central-loop integrity.
```

Expected output:

- Test commands
- Pass/fail table
- Evidence references
- Status recommendation

### GLOBAL-REVIEW-001 - Architecture Review Prompt

Implementation prompt:

```text
Review the current AgriControl change for architecture violations.
Prioritize bugs, safety risks, behavior regressions, missing tests, and branch-boundary leaks.
Look specifically for browser or FastAPI decision authority, hardware calls from decision logic, stale-data safety gaps, untruthful actuator state labels, and missing event evidence.
```

Test prompt:

```text
Confirm every finding is tied to a blueprint rule or acceptance gate and that no unrelated style-only feedback dominates the review.
```

Expected output:

- Findings by severity
- File and line references
- Required fixes
- Residual risk

### GLOBAL-STATE-001 - State Update And Handoff Prompt

Implementation prompt:

```text
After a verified change, update the durable handoff state.
Write what changed, why, affected blueprint area, evidence, status updates, blockers, and next task in docs/PROJECT_STATE.md.
Update data/progress-baseline.json only when a roadmap, branch, gate, or metric status has evidence.
Mirror public docs and JSON into web-build/docs and web-build/data before deployment.
```

Test prompt:

```text
Verify project state, baseline JSON, and public mirrored files agree with each other and contain no unsupported progress claims.
```

Expected output:

- Updated project state
- Updated progress data when needed
- Public mirrored files
- Verification summary

### GLOBAL-DEPLOY-001 - Dashboard Deploy Prompt

Implementation prompt:

```text
Deploy dashboard and public handoff files when reporting artifacts change.
Validate web-build/index.html script syntax, validate JSON files, then sync web-build/ to /var/www/html/agricontrol/taskmanagement/.
Verify the public dashboard, blueprint PDF, prompt library, project state, AI continuity guide, and JSON endpoints return HTTP 200.
Commit and push the complete source update to GitHub.
```

Test prompt:

```text
Confirm all required public URLs return HTTP 200 and the pushed GitHub commit matches local HEAD.
```

Expected output:

- Deployment evidence
- Verified public URLs
- Git commit hash
- Remaining issues

## Stage Prompt Packs

### STAGE-01 - Foundations

Tasks: 1, 2, 3, 4, 5, 6, 7, 8

Branches: B1: Product definition; B4: Protocol; B11: Physical outputs; B13: Testing

Implementation prompt:

```text
You are completing Stage 1: Foundations for AgriControl.
Stage intent: Board, wiring, use case, safe states, protocol, and acceptance tests.
Output target: A confirmed hardware and requirements foundation: board, firmware toolchain and version, pin map, wiring checks, first use case, safe states, protocol, and acceptance tests.
Implementation focus: Collect facts, write durable specifications, and avoid guessing hardware details.
Tasks in scope: 1. Confirm the exact ESP32-C3 board. 2. Record the firmware toolchain and version. 3. Create the complete pin map. 4. Verify OLED, NeoPixel, buzzer, and servo wiring. 5. Define the first use case. 6. Define safe states. 7. Define the communication protocol. 8. Define acceptance tests.
Work in roadmap order unless a blocker is documented.
Keep changes narrow enough to verify in one session.
Update project state and progress baseline only with evidence.
```

Test prompt:

```text
Verify Stage 1: Foundations.
Test focus: Verify the recorded facts against hardware evidence, commands, photos, serial output, or explicit user confirmation.
For every task marked done, provide evidence.
For every branch advanced, provide contract-level verification.
For every gate criterion touched, provide pass/fail output.
Hazards: Do not invent board variants or pin mappings. Do not mark wiring verified without evidence. Do not start platform features before the foundation is stable.
```

### STAGE-02 - Pure logic

Tasks: 9, 10, 11, 12, 13, 14, 15, 16

Branches: B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B13: Testing

Implementation prompt:

```text
You are completing Stage 2: Pure logic for AgriControl.
Stage intent: Canonical state, decision rules, safety supervisor, and sequence tests.
Output target: Pure logic modules for canonical sensors, system state, actuator state, decision rules, safety overrides, and deterministic tests.
Implementation focus: Build host-runnable logic before firmware integration, keeping decision and safety separate.
Tasks in scope: 9. Create canonical sensor structures. 10. Create system and actuator state structures. 11. Implement the stateful decision engine on the computer. 12. Implement the safety supervisor. 13. Test normal conditions. 14. Test exact boundaries. 15. Test conflicting rules. 16. Test state sequences.
Work in roadmap order unless a blocker is documented.
Keep changes narrow enough to verify in one session.
Update project state and progress baseline only with evidence.
```

Test prompt:

```text
Verify Stage 2: Pure logic.
Test focus: Run unit, boundary, conflict, and sequence tests for temperature, irrigation, hysteresis, and safety priority behavior.
For every task marked done, provide evidence.
For every branch advanced, provide contract-level verification.
For every gate criterion touched, provide pass/fail output.
Hazards: Decision logic must not call hardware or network code. Safety supervisor must have final authority. Hysteresis tests require sequences, not only isolated values.
```

### STAGE-03 - Local physical outputs

Tasks: 17, 18, 19, 20, 21, 22, 23

Branches: B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing

Implementation prompt:

```text
You are completing Stage 3: Local physical outputs for AgriControl.
Stage intent: OLED, NeoPixel, buzzer, servo, and output integration.
Output target: Verified local output drivers for OLED, NeoPixel, buzzer, servo, and combined output behavior.
Implementation focus: Test each physical output independently, then through the actuator manager boundary.
Tasks in scope: 17. Test OLED independently. 18. Test NeoPixel independently. 19. Test buzzer independently. 20. Test servo independently. 21. Test all outputs together. 22. Connect hardcoded decisions to outputs. 23. Confirm servo power does not reset the ESP.
Work in roadmap order unless a blocker is documented.
Keep changes narrow enough to verify in one session.
Update project state and progress baseline only with evidence.
```

Test prompt:

```text
Verify Stage 3: Local physical outputs.
Test focus: Record hardware observations, state-change-only buzzer behavior, OLED warning priority, servo angles, and power stability.
For every task marked done, provide evidence.
For every branch advanced, provide contract-level verification.
For every gate criterion touched, provide pass/fail output.
Hazards: Servo power must not reset the ESP. Drivers must only be called by the actuator manager. Do not report commanded output as measured physical state.
```

### STAGE-04 - ESP runtime

Tasks: 24, 25, 26, 27, 28, 29, 30

Branches: B5: ESP communication; B7: State management; B12: Observability; B13: Testing

Implementation prompt:

```text
You are completing Stage 4: ESP runtime for AgriControl.
Stage intent: Async runtime, shared state, events, stale data, recovery, and HTTP.
Output target: Non-blocking ESP runtime with shared state, events, stale-data detection, recovery, HTTP server, and validation limits.
Implementation focus: Keep communication reliable while never blocking safety or output tasks.
Tasks in scope: 24. Build the asynchronous runtime. 25. Add shared state management. 26. Add the event system. 27. Add stale-data detection. 28. Add recovery logic. 29. Add the HTTP server. 30. Add request-size and validation limits.
Work in roadmap order unless a blocker is documented.
Keep changes narrow enough to verify in one session.
Update project state and progress baseline only with evidence.
```

Test prompt:

```text
Verify Stage 4: ESP runtime.
Test focus: Exercise communication states, oversized input, malformed JSON, stale data, recovery, and runtime responsiveness.
For every task marked done, provide evidence.
For every branch advanced, provide contract-level verification.
For every gate criterion touched, provide pass/fail output.
Hazards: Communication layer must not evaluate behavior rules. Safety timeouts use ESP monotonic time. Request-size limits must be explicit.
```

### STAGE-05 - First vertical slice

Tasks: 31, 32, 33, 34, 35, 36, 37, 38, 39, 40

Branches: B4: Protocol; B5: ESP communication; B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing

Implementation prompt:

```text
You are completing Stage 5: First vertical slice for AgriControl.
Stage intent: Temperature input to ESP decision, servo, OLED, JSON response, and recovery.
Output target: First vertical slice: virtual temperature input to ESP validation, decision, safety, servo, OLED, JSON response, timeout, and recovery.
Implementation focus: Build only temperature first and prove the complete path before adding irrigation or scenarios.
Tasks in scope: 31. Implement only virtual temperature. 32. Send temperature with curl. 33. Validate the message. 34. Calculate the window command. 35. Apply the servo command. 36. Display the reason on OLED. 37. Return the decision as JSON. 38. Test repeated messages. 39. Test invalid values. 40. Test timeout and recovery.
Work in roadmap order unless a blocker is documented.
Keep changes narrow enough to verify in one session.
Update project state and progress baseline only with evidence.
```

Test prompt:

```text
Verify Stage 5: First vertical slice.
Test focus: Validate threshold boundaries, repeated messages, invalid values, timeout safe state, and recovery after stable messages.
For every task marked done, provide evidence.
For every branch advanced, provide contract-level verification.
For every gate criterion touched, provide pass/fail output.
Hazards: Do not add soil, tank, rain, MQTT, or database work in this slice. The website and FastAPI must not become the control authority. Every response must include reasons and rule IDs.
```

### STAGE-06 - Browser and FastAPI

Tasks: 41, 42, 43, 44, 45, 46, 47, 48

Branches: B2: Website simulation; B3: FastAPI bridge; B4: Protocol; B5: ESP communication; B12: Observability; B13: Testing

Implementation prompt:

```text
You are completing Stage 6: Browser and FastAPI for AgriControl.
Stage intent: Bridge, website controls, virtual window, event log, and endurance updates.
Output target: Local FastAPI bridge and browser controls for temperature, ESP response display, virtual window, event log, and hundreds of updates.
Implementation focus: Create a transparent bridge and dashboard; keep ESP decisions authoritative.
Tasks in scope: 41. Create the local FastAPI bridge. 42. Forward temperature to the ESP. 43. Create the website connection panel. 44. Create one temperature slider. 45. Display the ESP response. 46. Display the virtual window. 47. Add an event log. 48. Run hundreds of updates.
Work in roadmap order unless a blocker is documented.
Keep changes narrow enough to verify in one session.
Update project state and progress baseline only with evidence.
```

Test prompt:

```text
Verify Stage 6: Browser and FastAPI.
Test focus: Verify session IDs, sequence increments, bridge forwarding, connection errors, displayed commands, event log, and high-frequency updates.
For every task marked done, provide evidence.
For every branch advanced, provide contract-level verification.
For every gate criterion touched, provide pass/fail output.
Hazards: FastAPI coordinates and verifies; it does not decide. The browser sends sensor state and displays results; it does not bypass the ESP. Logs must capture meaningful transitions.
```

### STAGE-07 - Irrigation slice

Tasks: 49, 50, 51, 52, 53, 54, 55, 56, 57

Branches: B2: Website simulation; B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing

Implementation prompt:

```text
You are completing Stage 7: Irrigation slice for AgriControl.
Stage intent: Soil, tank, rain, pump hysteresis, protections, virtual actuators, warnings.
Output target: Greenhouse MVP inputs and outputs: soil moisture, tank level, rain, pump hysteresis, low-tank and rain protection, virtual pump/fan, warnings, and OLED pages.
Implementation focus: Extend the proven vertical slice while preserving canonical state, safety overrides, and truthful actuator vocabulary.
Tasks in scope: 49. Add soil moisture. 50. Add tank level. 51. Add rain. 52. Add pump hysteresis. 53. Add low-tank protection. 54. Add rain protection. 55. Add virtual pump and fan. 56. Connect LED and buzzer warnings. 57. Add corresponding OLED pages.
Work in roadmap order unless a blocker is documented.
Keep changes narrow enough to verify in one session.
Update project state and progress baseline only with evidence.
```

Test prompt:

```text
Verify Stage 7: Irrigation slice.
Test focus: Test moisture thresholds, tank threshold, rain override, fan/window temperature rules, warnings, and commanded versus simulated states.
For every task marked done, provide evidence.
For every branch advanced, provide contract-level verification.
For every gate criterion touched, provide pass/fail output.
Hazards: Low tank and rain override irrigation. Pump hysteresis must keep prior state between 30% and 40%. Simulated state must remain separate from commanded state.
```

### STAGE-08 - Scenario testing

Tasks: 58, 59, 60

Branches: B2: Website simulation; B3: FastAPI bridge; B12: Observability; B13: Testing

Implementation prompt:

```text
You are completing Stage 8: Scenario testing for AgriControl.
Stage intent: Preset scenarios with expected commands, alarm, mode, response time, and pass/fail.
Output target: Scenario engine with normal, hot, dry-soil, low-tank, rain, invalid-data, and communication-loss scenarios plus automatic PASS/FAIL comparison.
Implementation focus: Turn known blueprint behavior into repeatable scenario timelines with expected commands, modes, alarms, and response times.
Tasks in scope: 58. Add normal, hot, dry-soil, low-tank, rain, invalid-data, and communication-loss scenarios. 59. Define expected commands, mode, alarm, and response time. 60. Add automatic PASS/FAIL comparison.
Work in roadmap order unless a blocker is documented.
Keep changes narrow enough to verify in one session.
Update project state and progress baseline only with evidence.
```

Test prompt:

```text
Verify Stage 8: Scenario testing.
Test focus: Run every scenario and record expected versus actual results with pass/fail evidence.
For every task marked done, provide evidence.
For every branch advanced, provide contract-level verification.
For every gate criterion touched, provide pass/fail output.
Hazards: Scenario logic must test the ESP path, not replace it. Expected results must include alarm and response time. Invalid data must be rejected before state mutation.
```

### STAGE-09 - Closed-loop simulation

Tasks: 61, 62, 63, 64, 65, 66

Branches: B2: Website simulation; B9: Safety supervisor; B10: Actuator abstraction; B12: Observability; B13: Testing

Implementation prompt:

```text
You are completing Stage 9: Closed-loop simulation for AgriControl.
Stage intent: Actuator feedback, delays, failed starts, stuck faults, and servo mismatch.
Output target: Closed-loop actuator simulation with feedback, delays, failed starts, stuck faults, incorrect servo position, and ESP fault response.
Implementation focus: Add feedback evidence so the ESP can detect mismatch and failure without pretending commands equal physical truth.
Tasks in scope: 61. Add simulated actuator feedback. 62. Add startup delays. 63. Add failed startup. 64. Add stuck-on and stuck-off faults. 65. Add incorrect virtual servo position. 66. Make the ESP respond to feedback faults.
Work in roadmap order unless a blocker is documented.
Keep changes narrow enough to verify in one session.
Update project state and progress baseline only with evidence.
```

Test prompt:

```text
Verify Stage 9: Closed-loop simulation.
Test focus: Inject delayed, failed, stuck-on, stuck-off, and wrong-position feedback and confirm ESP safety behavior and logged faults.
For every task marked done, provide evidence.
For every branch advanced, provide contract-level verification.
For every gate criterion touched, provide pass/fail output.
Hazards: Commanded state is not measured state. Fault evidence must be explicit. Feedback faults must influence safety or recovery behavior.
```

### STAGE-10 - Reliability

Tasks: 67, 68, 69, 70, 71

Branches: B3: FastAPI bridge; B4: Protocol; B12: Observability; B13: Testing; B14: Recording and replay

Implementation prompt:

```text
You are completing Stage 10: Reliability for AgriControl.
Stage intent: Recording, replay, rule versions, endurance, watchdog decision, and limits.
Output target: Recording, replay, rule versioning, endurance tests, watchdog decision, and documented limits.
Implementation focus: Make experiments reproducible and regressions visible before broader platform expansion.
Tasks in scope: 67. Add recording and replay. 68. Add rule versioning. 69. Run long-duration tests. 70. Add a watchdog only after runtime stability. 71. Document known limits.
Work in roadmap order unless a blocker is documented.
Keep changes narrow enough to verify in one session.
Update project state and progress baseline only with evidence.
```

Test prompt:

```text
Verify Stage 10: Reliability.
Test focus: Replay identical sequences against changed firmware or rule versions, run endurance updates, and document unrecovered failures.
For every task marked done, provide evidence.
For every branch advanced, provide contract-level verification.
For every gate criterion touched, provide pass/fail output.
Hazards: Record protocol and rule versions. Do not add a watchdog until runtime behavior is understood. Known limits must be explicit.
```

### STAGE-11 - Physical migration

Tasks: 72, 73, 74, 75, 76

Branches: B6: Sensor abstraction; B7: State management; B10: Actuator abstraction; B11: Physical outputs; B13: Testing; B15: Physical expansion

Implementation prompt:

```text
You are completing Stage 11: Physical migration for AgriControl.
Stage intent: Physical sensors, source selection, pump driver, and feedback evidence.
Output target: Physical migration of sensors and pump with per-sensor source selection and feedback where possible.
Implementation focus: Replace virtual components one by one without rewriting decision or safety code.
Tasks in scope: 72. Add a real temperature sensor. 73. Add per-sensor source selection. 74. Add real soil, tank, and rain sensors. 75. Add a properly driven pump. 76. Add physical feedback where possible.
Work in roadmap order unless a blocker is documented.
Keep changes narrow enough to verify in one session.
Update project state and progress baseline only with evidence.
```

Test prompt:

```text
Verify Stage 11: Physical migration.
Test focus: Verify virtual, physical, hybrid, and disabled source modes and prove decision/safety behavior is unchanged.
For every task marked done, provide evidence.
For every branch advanced, provide contract-level verification.
For every gate criterion touched, provide pass/fail output.
Hazards: Virtual mode must remain available. Network values do not become GPIO signals. Physical feedback must be truthful and named.
```

### STAGE-12 - Platform growth

Tasks: 77, 78, 79, 80, 81, 82

Branches: B3: FastAPI bridge; B12: Observability; B13: Testing; B16: Platform expansion

Implementation prompt:

```text
You are completing Stage 12: Platform growth for AgriControl.
Stage intent: MQTT, multi-device, storage, authentication, remote access, and packaging.
Output target: Platform growth only when justified: MQTT, multiple devices, persistent storage, authentication, remote access, and reusable packaging.
Implementation focus: Add platform features only after the connected control loop is observable, testable, and stable.
Tasks in scope: 77. Add MQTT. 78. Add multiple ESP devices. 79. Add persistent storage. 80. Add authentication. 81. Add remote access. 82. Package the system as a reusable control and testing platform.
Work in roadmap order unless a blocker is documented.
Keep changes narrow enough to verify in one session.
Update project state and progress baseline only with evidence.
```

Test prompt:

```text
Verify Stage 12: Platform growth.
Test focus: Verify each platform addition is justified by a real workflow and does not weaken local-first operation or ESP authority.
For every task marked done, provide evidence.
For every branch advanced, provide contract-level verification.
For every gate criterion touched, provide pass/fail output.
Hazards: Do not let non-critical features delay the proven control loop. Remote dashboards must not bypass safety. Persistent data must support replay, history, or customer workflow.
```

## Branch Prompt Packs

### BRANCH-01 - Product definition

Implementation prompt:

```text
You are implementing Branch 1: Product definition.
Purpose: Mission, sensors, actuators, qualities, constraints.
Read the blueprint branch definition and preserve its boundary.
Deliver only the source, documentation, or tests that belong to this branch.
Do not let this branch take over another branch responsibility.
Contracts:
- Sensors, actuators, ranges, rules, limits, safe states, and acceptance tests are written down.
Deliverables:
- Requirements spec
- Safe-state table
- Acceptance test list
```

Test prompt:

```text
Verify Branch 1: Product definition.
Check that its input and output contracts are explicit and that data crosses boundaries through named structures or APIs.
Check that behavior is observable through structured events when relevant.
Required checks:
- Specification completeness review
- Trace every sensor and actuator to one range/state and initial implementation.
```

### BRANCH-02 - Website simulation

Implementation prompt:

```text
You are implementing Branch 2: Website simulation.
Purpose: Virtual conditions, scenarios, faults, dashboards.
Read the blueprint branch definition and preserve its boundary.
Deliver only the source, documentation, or tests that belong to this branch.
Do not let this branch take over another branch responsibility.
Contracts:
- Produces virtual sensor values and scenario events for the FastAPI bridge.
- Displays decisions, commands, events, tests, and virtual actuator feedback.
Deliverables:
- Simulation UI
- Scenario runner
- Virtual actuator display
```

Test prompt:

```text
Verify Branch 2: Website simulation.
Check that its input and output contracts are explicit and that data crosses boundaries through named structures or APIs.
Check that behavior is observable through structured events when relevant.
Required checks:
- Slider, toggle, exact input, automatic interval
- Noise, frozen value, disconnected sensor, impossible value, delay, spike
```

### BRANCH-03 - FastAPI bridge

Implementation prompt:

```text
You are implementing Branch 3: FastAPI bridge.
Purpose: Browser-to-ESP communication, sessions, logs, replay, tests.
Read the blueprint branch definition and preserve its boundary.
Deliver only the source, documentation, or tests that belong to this branch.
Do not let this branch take over another branch responsibility.
Contracts:
- Accepts website sensor data, creates sessions and sequences, forwards to ESP, stores logs, replays sessions, and compares results.
Deliverables:
- FastAPI routes
- Session handling
- Replay/log storage
```

Test prompt:

```text
Verify Branch 3: FastAPI bridge.
Check that its input and output contracts are explicit and that data crosses boundaries through named structures or APIs.
Check that behavior is observable through structured events when relevant.
Required checks:
- POST sensor message
- GET status
- POST scenario
- GET events
- Connection error handling
```

### BRANCH-04 - Protocol

Implementation prompt:

```text
You are implementing Branch 4: Protocol.
Purpose: Stable messages and validation rules.
Read the blueprint branch definition and preserve its boundary.
Deliver only the source, documentation, or tests that belong to this branch.
Do not let this branch take over another branch responsibility.
Contracts:
- Defines versioned messages, validation rules, response shape, sequence behavior, boot IDs, and rejection conditions.
Deliverables:
- Protocol schema
- Validation rules
- Response schema
```

Test prompt:

```text
Verify Branch 4: Protocol.
Check that its input and output contracts are explicit and that data crosses boundaries through named structures or APIs.
Check that behavior is observable through structured events when relevant.
Required checks:
- Unknown field
- Missing field
- Oversized body
- Duplicate sequence
- Impossible value
- Protocol version mismatch
```

### BRANCH-05 - ESP communication

Implementation prompt:

```text
You are implementing Branch 5: ESP communication.
Purpose: Move data without deciding behavior.
Read the blueprint branch definition and preserve its boundary.
Deliver only the source, documentation, or tests that belong to this branch.
Do not let this branch take over another branch responsibility.
Contracts:
- Connects/reconnects Wi-Fi, accepts local HTTP, limits request size, parses JSON, returns structured errors, and reports communication state.
Deliverables:
- ESP communication module
- Structured rejection errors
- Communication state events
```

Test prompt:

```text
Verify Branch 5: ESP communication.
Check that its input and output contracts are explicit and that data crosses boundaries through named structures or APIs.
Check that behavior is observable through structured events when relevant.
Required checks:
- OFFLINE to CONNECTING to ONLINE
- DATA_ACTIVE
- DATA_STALE
- RECONNECTING
- Non-blocking safety loop
```

### BRANCH-06 - Sensor abstraction

Implementation prompt:

```text
You are implementing Branch 6: Sensor abstraction.
Purpose: Virtual and physical inputs become canonical state.
Read the blueprint branch definition and preserve its boundary.
Deliver only the source, documentation, or tests that belong to this branch.
Do not let this branch take over another branch responsibility.
Contracts:
- Adapts virtual, physical, hybrid, and disabled sources into the same canonical sensor model.
Deliverables:
- Canonical sensor record
- Source mode handling
- Validation helpers
```

Test prompt:

```text
Verify Branch 6: Sensor abstraction.
Check that its input and output contracts are explicit and that data crosses boundaries through named structures or APIs.
Check that behavior is observable through structured events when relevant.
Required checks:
- Temperature range -10 to 60 C
- Moisture 0 to 100%
- Tank 0 to 100%
- Rain boolean
- Quality and age
```

### BRANCH-07 - State management

Implementation prompt:

```text
You are implementing Branch 7: State management.
Purpose: Authoritative sensor, system, and actuator state.
Read the blueprint branch definition and preserve its boundary.
Deliver only the source, documentation, or tests that belong to this branch.
Do not let this branch take over another branch responsibility.
Contracts:
- Maintains one authoritative sensor, system, and actuator state used by decision, safety, display, and reporting.
Deliverables:
- State model
- Transition rules
- State update events
```

Test prompt:

```text
Verify Branch 7: State management.
Check that its input and output contracts are explicit and that data crosses boundaries through named structures or APIs.
Check that behavior is observable through structured events when relevant.
Required checks:
- BOOT to CONNECTING to READY
- AUTOMATIC to WARNING/SAFE/FAULT
- RECOVERY to AUTOMATIC
- Reject impossible flag combinations
```

### BRANCH-08 - Decision engine

Implementation prompt:

```text
You are implementing Branch 8: Decision engine.
Purpose: Normal requested actions with reasons and rule IDs.
Read the blueprint branch definition and preserve its boundary.
Deliver only the source, documentation, or tests that belong to this branch.
Do not let this branch take over another branch responsibility.
Contracts:
- Calculates requested actions, triggered rule IDs, human-readable reasons, and decision IDs under valid normal conditions.
Deliverables:
- Decision engine
- Rule IDs
- Reason text
- Pure logic tests
```

Test prompt:

```text
Verify Branch 8: Decision engine.
Check that its input and output contracts are explicit and that data crosses boundaries through named structures or APIs.
Check that behavior is observable through structured events when relevant.
Required checks:
- Temperature <= 28 C
- 28 C < temperature <= 35 C
- Temperature > 35 C
- Moisture hysteresis sequences
```

### BRANCH-09 - Safety supervisor

Implementation prompt:

```text
You are implementing Branch 9: Safety supervisor.
Purpose: Final authority and conflict resolution.
Read the blueprint branch definition and preserve its boundary.
Deliver only the source, documentation, or tests that belong to this branch.
Do not let this branch take over another branch responsibility.
Contracts:
- Applies emergency, safety, equipment protection, automatic, manual, and optimization priorities to produce final commands.
Deliverables:
- Safety supervisor
- Override reasons
- Safe-state matrix tests
```

Test prompt:

```text
Verify Branch 9: Safety supervisor.
Check that its input and output contracts are explicit and that data crosses boundaries through named structures or APIs.
Check that behavior is observable through structured events when relevant.
Required checks:
- Low tank overrides pump ON
- Stale data safe state
- Controller fault critical alarm
- Emergency stop
```

### BRANCH-10 - Actuator abstraction

Implementation prompt:

```text
You are implementing Branch 10: Actuator abstraction.
Purpose: Requested, commanded, simulated, measured, and fault states.
Read the blueprint branch definition and preserve its boundary.
Deliver only the source, documentation, or tests that belong to this branch.
Do not let this branch take over another branch responsibility.
Contracts:
- Separates requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Deliverables:
- Actuator state model
- Feedback handler
- Fault evidence
```

Test prompt:

```text
Verify Branch 10: Actuator abstraction.
Check that its input and output contracts are explicit and that data crosses boundaries through named structures or APIs.
Check that behavior is observable through structured events when relevant.
Required checks:
- Command differs from request after safety
- Simulated startup delay
- Stuck on/off
- Measured unavailable
```

### BRANCH-11 - Physical outputs

Implementation prompt:

```text
You are implementing Branch 11: Physical outputs.
Purpose: OLED, LED, buzzer, and servo behavior.
Read the blueprint branch definition and preserve its boundary.
Deliver only the source, documentation, or tests that belong to this branch.
Do not let this branch take over another branch responsibility.
Contracts:
- Applies OLED, NeoPixel, buzzer, and servo behavior only through the actuator manager.
Deliverables:
- Physical drivers
- Output integration
- Hardware verification notes
```

Test prompt:

```text
Verify Branch 11: Physical outputs.
Check that its input and output contracts are explicit and that data crosses boundaries through named structures or APIs.
Check that behavior is observable through structured events when relevant.
Required checks:
- OLED summary pages
- Warning interruption
- NeoPixel colors
- Buzzer state-change-only tones
- Servo 10/90/170 degrees
```

### BRANCH-12 - Observability

Implementation prompt:

```text
You are implementing Branch 12: Observability.
Purpose: Meaningful events and state changes.
Read the blueprint branch definition and preserve its boundary.
Deliver only the source, documentation, or tests that belong to this branch.
Do not let this branch take over another branch responsibility.
Contracts:
- Records structured events from every branch and exposes them through serial, ESP responses, FastAPI storage, and website timeline.
Deliverables:
- Event schema
- Event storage
- Timeline rendering
```

Test prompt:

```text
Verify Branch 12: Observability.
Check that its input and output contracts are explicit and that data crosses boundaries through named structures or APIs.
Check that behavior is observable through structured events when relevant.
Required checks:
- SENSOR_RECEIVED
- SENSOR_REJECTED
- RULE_TRIGGERED
- SAFETY_OVERRIDE
- COMMAND_CHANGED
- FAULT_DETECTED
```

### BRANCH-13 - Testing

Implementation prompt:

```text
You are implementing Branch 13: Testing.
Purpose: Logic, integration, failure, endurance, and replay verification.
Read the blueprint branch definition and preserve its boundary.
Deliver only the source, documentation, or tests that belong to this branch.
Do not let this branch take over another branch responsibility.
Contracts:
- Verifies unit, boundary, sequence, integration, failure, endurance, and replay behavior from the beginning.
Deliverables:
- Test IDs
- Expected results
- Completion gates
```

Test prompt:

```text
Verify Branch 13: Testing.
Check that its input and output contracts are explicit and that data crosses boundaries through named structures or APIs.
Check that behavior is observable through structured events when relevant.
Required checks:
- 40 C -> window fully open
- 28.0/28.1/35.0/35.1
- Bad JSON
- Timeout
- Thousands of updates
```

### BRANCH-14 - Recording and replay

Implementation prompt:

```text
You are implementing Branch 14: Recording and replay.
Purpose: Experiment reproduction and regression comparison.
Read the blueprint branch definition and preserve its boundary.
Deliver only the source, documentation, or tests that belong to this branch.
Do not let this branch take over another branch responsibility.
Contracts:
- Records protocol and rule versions, input timing and values, decisions, overrides, commands, feedback, faults, and test results.
Deliverables:
- Recorder
- Replay engine
- Comparison report
```

Test prompt:

```text
Verify Branch 14: Recording and replay.
Check that its input and output contracts are explicit and that data crosses boundaries through named structures or APIs.
Check that behavior is observable through structured events when relevant.
Required checks:
- Replay identical sequence
- Compare old and new firmware behavior
- Regression report
```

### BRANCH-15 - Physical expansion

Implementation prompt:

```text
You are implementing Branch 15: Physical expansion.
Purpose: Gradual replacement of virtual components.
Read the blueprint branch definition and preserve its boundary.
Deliver only the source, documentation, or tests that belong to this branch.
Do not let this branch take over another branch responsibility.
Contracts:
- Replaces virtual parts gradually while preserving canonical state and decision/safety code.
Deliverables:
- Physical sensor adapter
- Source selection
- Migration tests
```

Test prompt:

```text
Verify Branch 15: Physical expansion.
Check that its input and output contracts are explicit and that data crosses boundaries through named structures or APIs.
Check that behavior is observable through structured events when relevant.
Required checks:
- Real temperature replacement
- Per-sensor source selection
- Virtual mode remains available
```

### BRANCH-16 - Platform expansion

Implementation prompt:

```text
You are implementing Branch 16: Platform expansion.
Purpose: MQTT, multi-device, database, authentication, SaaS.
Read the blueprint branch definition and preserve its boundary.
Deliver only the source, documentation, or tests that belong to this branch.
Do not let this branch take over another branch responsibility.
Contracts:
- Adds MQTT, multi-device, database, authentication, and SaaS packaging only when justified by stable core behavior.
Deliverables:
- Platform architecture
- Security plan
- Remote dashboard constraints
```

Test prompt:

```text
Verify Branch 16: Platform expansion.
Check that its input and output contracts are explicit and that data crosses boundaries through named structures or APIs.
Check that behavior is observable through structured events when relevant.
Required checks:
- Multiple devices justify MQTT
- History justifies database
- Remote users justify auth
- Customer workflow justifies SaaS
```

## Roadmap Task Prompts

### TASK-S01-01 - Confirm the exact ESP32-C3 board.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 1: Confirm the exact ESP32-C3 board.
Blueprint stage: Stage 1 - Foundations.
Affected branches: B1: Product definition; B4: Protocol; B11: Physical outputs; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Board, wiring, use case, safe states, protocol, and acceptance tests.
Stage output target: A confirmed hardware and requirements foundation: board, firmware toolchain and version, pin map, wiring checks, first use case, safe states, protocol, and acceptance tests.
Implementation focus: Collect facts, write durable specifications, and avoid guessing hardware details.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 1: Confirm the exact ESP32-C3 board.
Verify the task within Stage 1 - Foundations.
Use this stage test focus: Verify the recorded facts against hardware evidence, commands, photos, serial output, or explicit user confirmation.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not invent board variants or pin mappings. Do not mark wiring verified without evidence. Do not start platform features before the foundation is stable.
```

### TASK-S01-02 - Record the firmware toolchain and version.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 2: Record the firmware toolchain and version.
Blueprint stage: Stage 1 - Foundations.
Affected branches: B1: Product definition; B4: Protocol; B11: Physical outputs; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Board, wiring, use case, safe states, protocol, and acceptance tests.
Stage output target: A confirmed hardware and requirements foundation: board, firmware toolchain and version, pin map, wiring checks, first use case, safe states, protocol, and acceptance tests.
Implementation focus: Collect facts, write durable specifications, and avoid guessing hardware details.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 2: Record the firmware toolchain and version.
Verify the task within Stage 1 - Foundations.
Use this stage test focus: Verify the recorded facts against hardware evidence, commands, photos, serial output, or explicit user confirmation.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not invent board variants or pin mappings. Do not mark wiring verified without evidence. Do not start platform features before the foundation is stable.
```

### TASK-S01-03 - Create the complete pin map.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 3: Create the complete pin map.
Blueprint stage: Stage 1 - Foundations.
Affected branches: B1: Product definition; B4: Protocol; B11: Physical outputs; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Board, wiring, use case, safe states, protocol, and acceptance tests.
Stage output target: A confirmed hardware and requirements foundation: board, firmware toolchain and version, pin map, wiring checks, first use case, safe states, protocol, and acceptance tests.
Implementation focus: Collect facts, write durable specifications, and avoid guessing hardware details.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 3: Create the complete pin map.
Verify the task within Stage 1 - Foundations.
Use this stage test focus: Verify the recorded facts against hardware evidence, commands, photos, serial output, or explicit user confirmation.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not invent board variants or pin mappings. Do not mark wiring verified without evidence. Do not start platform features before the foundation is stable.
```

### TASK-S01-04 - Verify OLED, NeoPixel, buzzer, and servo wiring.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 4: Verify OLED, NeoPixel, buzzer, and servo wiring.
Blueprint stage: Stage 1 - Foundations.
Affected branches: B1: Product definition; B4: Protocol; B11: Physical outputs; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Board, wiring, use case, safe states, protocol, and acceptance tests.
Stage output target: A confirmed hardware and requirements foundation: board, firmware toolchain and version, pin map, wiring checks, first use case, safe states, protocol, and acceptance tests.
Implementation focus: Collect facts, write durable specifications, and avoid guessing hardware details.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 4: Verify OLED, NeoPixel, buzzer, and servo wiring.
Verify the task within Stage 1 - Foundations.
Use this stage test focus: Verify the recorded facts against hardware evidence, commands, photos, serial output, or explicit user confirmation.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not invent board variants or pin mappings. Do not mark wiring verified without evidence. Do not start platform features before the foundation is stable.
```

### TASK-S01-05 - Define the first use case.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 5: Define the first use case.
Blueprint stage: Stage 1 - Foundations.
Affected branches: B1: Product definition; B4: Protocol; B11: Physical outputs; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Board, wiring, use case, safe states, protocol, and acceptance tests.
Stage output target: A confirmed hardware and requirements foundation: board, firmware toolchain and version, pin map, wiring checks, first use case, safe states, protocol, and acceptance tests.
Implementation focus: Collect facts, write durable specifications, and avoid guessing hardware details.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 5: Define the first use case.
Verify the task within Stage 1 - Foundations.
Use this stage test focus: Verify the recorded facts against hardware evidence, commands, photos, serial output, or explicit user confirmation.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not invent board variants or pin mappings. Do not mark wiring verified without evidence. Do not start platform features before the foundation is stable.
```

### TASK-S01-06 - Define safe states.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 6: Define safe states.
Blueprint stage: Stage 1 - Foundations.
Affected branches: B1: Product definition; B4: Protocol; B11: Physical outputs; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Board, wiring, use case, safe states, protocol, and acceptance tests.
Stage output target: A confirmed hardware and requirements foundation: board, firmware toolchain and version, pin map, wiring checks, first use case, safe states, protocol, and acceptance tests.
Implementation focus: Collect facts, write durable specifications, and avoid guessing hardware details.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 6: Define safe states.
Verify the task within Stage 1 - Foundations.
Use this stage test focus: Verify the recorded facts against hardware evidence, commands, photos, serial output, or explicit user confirmation.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not invent board variants or pin mappings. Do not mark wiring verified without evidence. Do not start platform features before the foundation is stable.
```

### TASK-S01-07 - Define the communication protocol.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 7: Define the communication protocol.
Blueprint stage: Stage 1 - Foundations.
Affected branches: B1: Product definition; B4: Protocol; B11: Physical outputs; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Board, wiring, use case, safe states, protocol, and acceptance tests.
Stage output target: A confirmed hardware and requirements foundation: board, firmware toolchain and version, pin map, wiring checks, first use case, safe states, protocol, and acceptance tests.
Implementation focus: Collect facts, write durable specifications, and avoid guessing hardware details.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 7: Define the communication protocol.
Verify the task within Stage 1 - Foundations.
Use this stage test focus: Verify the recorded facts against hardware evidence, commands, photos, serial output, or explicit user confirmation.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not invent board variants or pin mappings. Do not mark wiring verified without evidence. Do not start platform features before the foundation is stable.
```

### TASK-S01-08 - Define acceptance tests.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 8: Define acceptance tests.
Blueprint stage: Stage 1 - Foundations.
Affected branches: B1: Product definition; B4: Protocol; B11: Physical outputs; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Board, wiring, use case, safe states, protocol, and acceptance tests.
Stage output target: A confirmed hardware and requirements foundation: board, firmware toolchain and version, pin map, wiring checks, first use case, safe states, protocol, and acceptance tests.
Implementation focus: Collect facts, write durable specifications, and avoid guessing hardware details.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 8: Define acceptance tests.
Verify the task within Stage 1 - Foundations.
Use this stage test focus: Verify the recorded facts against hardware evidence, commands, photos, serial output, or explicit user confirmation.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not invent board variants or pin mappings. Do not mark wiring verified without evidence. Do not start platform features before the foundation is stable.
```

### TASK-S02-09 - Create canonical sensor structures.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 9: Create canonical sensor structures.
Blueprint stage: Stage 2 - Pure logic.
Affected branches: B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Canonical state, decision rules, safety supervisor, and sequence tests.
Stage output target: Pure logic modules for canonical sensors, system state, actuator state, decision rules, safety overrides, and deterministic tests.
Implementation focus: Build host-runnable logic before firmware integration, keeping decision and safety separate.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 9: Create canonical sensor structures.
Verify the task within Stage 2 - Pure logic.
Use this stage test focus: Run unit, boundary, conflict, and sequence tests for temperature, irrigation, hysteresis, and safety priority behavior.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Decision logic must not call hardware or network code. Safety supervisor must have final authority. Hysteresis tests require sequences, not only isolated values.
```

### TASK-S02-10 - Create system and actuator state structures.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 10: Create system and actuator state structures.
Blueprint stage: Stage 2 - Pure logic.
Affected branches: B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Canonical state, decision rules, safety supervisor, and sequence tests.
Stage output target: Pure logic modules for canonical sensors, system state, actuator state, decision rules, safety overrides, and deterministic tests.
Implementation focus: Build host-runnable logic before firmware integration, keeping decision and safety separate.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 10: Create system and actuator state structures.
Verify the task within Stage 2 - Pure logic.
Use this stage test focus: Run unit, boundary, conflict, and sequence tests for temperature, irrigation, hysteresis, and safety priority behavior.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Decision logic must not call hardware or network code. Safety supervisor must have final authority. Hysteresis tests require sequences, not only isolated values.
```

### TASK-S02-11 - Implement the stateful decision engine on the computer.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 11: Implement the stateful decision engine on the computer.
Blueprint stage: Stage 2 - Pure logic.
Affected branches: B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Canonical state, decision rules, safety supervisor, and sequence tests.
Stage output target: Pure logic modules for canonical sensors, system state, actuator state, decision rules, safety overrides, and deterministic tests.
Implementation focus: Build host-runnable logic before firmware integration, keeping decision and safety separate.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 11: Implement the stateful decision engine on the computer.
Verify the task within Stage 2 - Pure logic.
Use this stage test focus: Run unit, boundary, conflict, and sequence tests for temperature, irrigation, hysteresis, and safety priority behavior.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Decision logic must not call hardware or network code. Safety supervisor must have final authority. Hysteresis tests require sequences, not only isolated values.
```

### TASK-S02-12 - Implement the safety supervisor.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 12: Implement the safety supervisor.
Blueprint stage: Stage 2 - Pure logic.
Affected branches: B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Canonical state, decision rules, safety supervisor, and sequence tests.
Stage output target: Pure logic modules for canonical sensors, system state, actuator state, decision rules, safety overrides, and deterministic tests.
Implementation focus: Build host-runnable logic before firmware integration, keeping decision and safety separate.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 12: Implement the safety supervisor.
Verify the task within Stage 2 - Pure logic.
Use this stage test focus: Run unit, boundary, conflict, and sequence tests for temperature, irrigation, hysteresis, and safety priority behavior.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Decision logic must not call hardware or network code. Safety supervisor must have final authority. Hysteresis tests require sequences, not only isolated values.
```

### TASK-S02-13 - Test normal conditions.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 13: Test normal conditions.
Blueprint stage: Stage 2 - Pure logic.
Affected branches: B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Canonical state, decision rules, safety supervisor, and sequence tests.
Stage output target: Pure logic modules for canonical sensors, system state, actuator state, decision rules, safety overrides, and deterministic tests.
Implementation focus: Build host-runnable logic before firmware integration, keeping decision and safety separate.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 13: Test normal conditions.
Verify the task within Stage 2 - Pure logic.
Use this stage test focus: Run unit, boundary, conflict, and sequence tests for temperature, irrigation, hysteresis, and safety priority behavior.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Decision logic must not call hardware or network code. Safety supervisor must have final authority. Hysteresis tests require sequences, not only isolated values.
```

### TASK-S02-14 - Test exact boundaries.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 14: Test exact boundaries.
Blueprint stage: Stage 2 - Pure logic.
Affected branches: B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Canonical state, decision rules, safety supervisor, and sequence tests.
Stage output target: Pure logic modules for canonical sensors, system state, actuator state, decision rules, safety overrides, and deterministic tests.
Implementation focus: Build host-runnable logic before firmware integration, keeping decision and safety separate.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 14: Test exact boundaries.
Verify the task within Stage 2 - Pure logic.
Use this stage test focus: Run unit, boundary, conflict, and sequence tests for temperature, irrigation, hysteresis, and safety priority behavior.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Decision logic must not call hardware or network code. Safety supervisor must have final authority. Hysteresis tests require sequences, not only isolated values.
```

### TASK-S02-15 - Test conflicting rules.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 15: Test conflicting rules.
Blueprint stage: Stage 2 - Pure logic.
Affected branches: B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Canonical state, decision rules, safety supervisor, and sequence tests.
Stage output target: Pure logic modules for canonical sensors, system state, actuator state, decision rules, safety overrides, and deterministic tests.
Implementation focus: Build host-runnable logic before firmware integration, keeping decision and safety separate.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 15: Test conflicting rules.
Verify the task within Stage 2 - Pure logic.
Use this stage test focus: Run unit, boundary, conflict, and sequence tests for temperature, irrigation, hysteresis, and safety priority behavior.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Decision logic must not call hardware or network code. Safety supervisor must have final authority. Hysteresis tests require sequences, not only isolated values.
```

### TASK-S02-16 - Test state sequences.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 16: Test state sequences.
Blueprint stage: Stage 2 - Pure logic.
Affected branches: B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Canonical state, decision rules, safety supervisor, and sequence tests.
Stage output target: Pure logic modules for canonical sensors, system state, actuator state, decision rules, safety overrides, and deterministic tests.
Implementation focus: Build host-runnable logic before firmware integration, keeping decision and safety separate.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 16: Test state sequences.
Verify the task within Stage 2 - Pure logic.
Use this stage test focus: Run unit, boundary, conflict, and sequence tests for temperature, irrigation, hysteresis, and safety priority behavior.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Decision logic must not call hardware or network code. Safety supervisor must have final authority. Hysteresis tests require sequences, not only isolated values.
```

### TASK-S03-17 - Test OLED independently.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 17: Test OLED independently.
Blueprint stage: Stage 3 - Local physical outputs.
Affected branches: B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports OLED, NeoPixel, buzzer, servo, and output integration.
Stage output target: Verified local output drivers for OLED, NeoPixel, buzzer, servo, and combined output behavior.
Implementation focus: Test each physical output independently, then through the actuator manager boundary.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 17: Test OLED independently.
Verify the task within Stage 3 - Local physical outputs.
Use this stage test focus: Record hardware observations, state-change-only buzzer behavior, OLED warning priority, servo angles, and power stability.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Servo power must not reset the ESP. Drivers must only be called by the actuator manager. Do not report commanded output as measured physical state.
```

### TASK-S03-18 - Test NeoPixel independently.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 18: Test NeoPixel independently.
Blueprint stage: Stage 3 - Local physical outputs.
Affected branches: B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports OLED, NeoPixel, buzzer, servo, and output integration.
Stage output target: Verified local output drivers for OLED, NeoPixel, buzzer, servo, and combined output behavior.
Implementation focus: Test each physical output independently, then through the actuator manager boundary.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 18: Test NeoPixel independently.
Verify the task within Stage 3 - Local physical outputs.
Use this stage test focus: Record hardware observations, state-change-only buzzer behavior, OLED warning priority, servo angles, and power stability.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Servo power must not reset the ESP. Drivers must only be called by the actuator manager. Do not report commanded output as measured physical state.
```

### TASK-S03-19 - Test buzzer independently.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 19: Test buzzer independently.
Blueprint stage: Stage 3 - Local physical outputs.
Affected branches: B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports OLED, NeoPixel, buzzer, servo, and output integration.
Stage output target: Verified local output drivers for OLED, NeoPixel, buzzer, servo, and combined output behavior.
Implementation focus: Test each physical output independently, then through the actuator manager boundary.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 19: Test buzzer independently.
Verify the task within Stage 3 - Local physical outputs.
Use this stage test focus: Record hardware observations, state-change-only buzzer behavior, OLED warning priority, servo angles, and power stability.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Servo power must not reset the ESP. Drivers must only be called by the actuator manager. Do not report commanded output as measured physical state.
```

### TASK-S03-20 - Test servo independently.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 20: Test servo independently.
Blueprint stage: Stage 3 - Local physical outputs.
Affected branches: B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports OLED, NeoPixel, buzzer, servo, and output integration.
Stage output target: Verified local output drivers for OLED, NeoPixel, buzzer, servo, and combined output behavior.
Implementation focus: Test each physical output independently, then through the actuator manager boundary.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 20: Test servo independently.
Verify the task within Stage 3 - Local physical outputs.
Use this stage test focus: Record hardware observations, state-change-only buzzer behavior, OLED warning priority, servo angles, and power stability.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Servo power must not reset the ESP. Drivers must only be called by the actuator manager. Do not report commanded output as measured physical state.
```

### TASK-S03-21 - Test all outputs together.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 21: Test all outputs together.
Blueprint stage: Stage 3 - Local physical outputs.
Affected branches: B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports OLED, NeoPixel, buzzer, servo, and output integration.
Stage output target: Verified local output drivers for OLED, NeoPixel, buzzer, servo, and combined output behavior.
Implementation focus: Test each physical output independently, then through the actuator manager boundary.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 21: Test all outputs together.
Verify the task within Stage 3 - Local physical outputs.
Use this stage test focus: Record hardware observations, state-change-only buzzer behavior, OLED warning priority, servo angles, and power stability.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Servo power must not reset the ESP. Drivers must only be called by the actuator manager. Do not report commanded output as measured physical state.
```

### TASK-S03-22 - Connect hardcoded decisions to outputs.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 22: Connect hardcoded decisions to outputs.
Blueprint stage: Stage 3 - Local physical outputs.
Affected branches: B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports OLED, NeoPixel, buzzer, servo, and output integration.
Stage output target: Verified local output drivers for OLED, NeoPixel, buzzer, servo, and combined output behavior.
Implementation focus: Test each physical output independently, then through the actuator manager boundary.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 22: Connect hardcoded decisions to outputs.
Verify the task within Stage 3 - Local physical outputs.
Use this stage test focus: Record hardware observations, state-change-only buzzer behavior, OLED warning priority, servo angles, and power stability.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Servo power must not reset the ESP. Drivers must only be called by the actuator manager. Do not report commanded output as measured physical state.
```

### TASK-S03-23 - Confirm servo power does not reset the ESP.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 23: Confirm servo power does not reset the ESP.
Blueprint stage: Stage 3 - Local physical outputs.
Affected branches: B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports OLED, NeoPixel, buzzer, servo, and output integration.
Stage output target: Verified local output drivers for OLED, NeoPixel, buzzer, servo, and combined output behavior.
Implementation focus: Test each physical output independently, then through the actuator manager boundary.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 23: Confirm servo power does not reset the ESP.
Verify the task within Stage 3 - Local physical outputs.
Use this stage test focus: Record hardware observations, state-change-only buzzer behavior, OLED warning priority, servo angles, and power stability.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Servo power must not reset the ESP. Drivers must only be called by the actuator manager. Do not report commanded output as measured physical state.
```

### TASK-S04-24 - Build the asynchronous runtime.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 24: Build the asynchronous runtime.
Blueprint stage: Stage 4 - ESP runtime.
Affected branches: B5: ESP communication; B7: State management; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Async runtime, shared state, events, stale data, recovery, and HTTP.
Stage output target: Non-blocking ESP runtime with shared state, events, stale-data detection, recovery, HTTP server, and validation limits.
Implementation focus: Keep communication reliable while never blocking safety or output tasks.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 24: Build the asynchronous runtime.
Verify the task within Stage 4 - ESP runtime.
Use this stage test focus: Exercise communication states, oversized input, malformed JSON, stale data, recovery, and runtime responsiveness.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Communication layer must not evaluate behavior rules. Safety timeouts use ESP monotonic time. Request-size limits must be explicit.
```

### TASK-S04-25 - Add shared state management.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 25: Add shared state management.
Blueprint stage: Stage 4 - ESP runtime.
Affected branches: B5: ESP communication; B7: State management; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Async runtime, shared state, events, stale data, recovery, and HTTP.
Stage output target: Non-blocking ESP runtime with shared state, events, stale-data detection, recovery, HTTP server, and validation limits.
Implementation focus: Keep communication reliable while never blocking safety or output tasks.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 25: Add shared state management.
Verify the task within Stage 4 - ESP runtime.
Use this stage test focus: Exercise communication states, oversized input, malformed JSON, stale data, recovery, and runtime responsiveness.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Communication layer must not evaluate behavior rules. Safety timeouts use ESP monotonic time. Request-size limits must be explicit.
```

### TASK-S04-26 - Add the event system.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 26: Add the event system.
Blueprint stage: Stage 4 - ESP runtime.
Affected branches: B5: ESP communication; B7: State management; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Async runtime, shared state, events, stale data, recovery, and HTTP.
Stage output target: Non-blocking ESP runtime with shared state, events, stale-data detection, recovery, HTTP server, and validation limits.
Implementation focus: Keep communication reliable while never blocking safety or output tasks.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 26: Add the event system.
Verify the task within Stage 4 - ESP runtime.
Use this stage test focus: Exercise communication states, oversized input, malformed JSON, stale data, recovery, and runtime responsiveness.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Communication layer must not evaluate behavior rules. Safety timeouts use ESP monotonic time. Request-size limits must be explicit.
```

### TASK-S04-27 - Add stale-data detection.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 27: Add stale-data detection.
Blueprint stage: Stage 4 - ESP runtime.
Affected branches: B5: ESP communication; B7: State management; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Async runtime, shared state, events, stale data, recovery, and HTTP.
Stage output target: Non-blocking ESP runtime with shared state, events, stale-data detection, recovery, HTTP server, and validation limits.
Implementation focus: Keep communication reliable while never blocking safety or output tasks.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 27: Add stale-data detection.
Verify the task within Stage 4 - ESP runtime.
Use this stage test focus: Exercise communication states, oversized input, malformed JSON, stale data, recovery, and runtime responsiveness.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Communication layer must not evaluate behavior rules. Safety timeouts use ESP monotonic time. Request-size limits must be explicit.
```

### TASK-S04-28 - Add recovery logic.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 28: Add recovery logic.
Blueprint stage: Stage 4 - ESP runtime.
Affected branches: B5: ESP communication; B7: State management; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Async runtime, shared state, events, stale data, recovery, and HTTP.
Stage output target: Non-blocking ESP runtime with shared state, events, stale-data detection, recovery, HTTP server, and validation limits.
Implementation focus: Keep communication reliable while never blocking safety or output tasks.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 28: Add recovery logic.
Verify the task within Stage 4 - ESP runtime.
Use this stage test focus: Exercise communication states, oversized input, malformed JSON, stale data, recovery, and runtime responsiveness.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Communication layer must not evaluate behavior rules. Safety timeouts use ESP monotonic time. Request-size limits must be explicit.
```

### TASK-S04-29 - Add the HTTP server.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 29: Add the HTTP server.
Blueprint stage: Stage 4 - ESP runtime.
Affected branches: B5: ESP communication; B7: State management; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Async runtime, shared state, events, stale data, recovery, and HTTP.
Stage output target: Non-blocking ESP runtime with shared state, events, stale-data detection, recovery, HTTP server, and validation limits.
Implementation focus: Keep communication reliable while never blocking safety or output tasks.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 29: Add the HTTP server.
Verify the task within Stage 4 - ESP runtime.
Use this stage test focus: Exercise communication states, oversized input, malformed JSON, stale data, recovery, and runtime responsiveness.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Communication layer must not evaluate behavior rules. Safety timeouts use ESP monotonic time. Request-size limits must be explicit.
```

### TASK-S04-30 - Add request-size and validation limits.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 30: Add request-size and validation limits.
Blueprint stage: Stage 4 - ESP runtime.
Affected branches: B5: ESP communication; B7: State management; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Async runtime, shared state, events, stale data, recovery, and HTTP.
Stage output target: Non-blocking ESP runtime with shared state, events, stale-data detection, recovery, HTTP server, and validation limits.
Implementation focus: Keep communication reliable while never blocking safety or output tasks.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 30: Add request-size and validation limits.
Verify the task within Stage 4 - ESP runtime.
Use this stage test focus: Exercise communication states, oversized input, malformed JSON, stale data, recovery, and runtime responsiveness.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Communication layer must not evaluate behavior rules. Safety timeouts use ESP monotonic time. Request-size limits must be explicit.
```

### TASK-S05-31 - Implement only virtual temperature.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 31: Implement only virtual temperature.
Blueprint stage: Stage 5 - First vertical slice.
Affected branches: B4: Protocol; B5: ESP communication; B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Temperature input to ESP decision, servo, OLED, JSON response, and recovery.
Stage output target: First vertical slice: virtual temperature input to ESP validation, decision, safety, servo, OLED, JSON response, timeout, and recovery.
Implementation focus: Build only temperature first and prove the complete path before adding irrigation or scenarios.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 31: Implement only virtual temperature.
Verify the task within Stage 5 - First vertical slice.
Use this stage test focus: Validate threshold boundaries, repeated messages, invalid values, timeout safe state, and recovery after stable messages.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not add soil, tank, rain, MQTT, or database work in this slice. The website and FastAPI must not become the control authority. Every response must include reasons and rule IDs.
```

### TASK-S05-32 - Send temperature with curl.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 32: Send temperature with curl.
Blueprint stage: Stage 5 - First vertical slice.
Affected branches: B4: Protocol; B5: ESP communication; B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Temperature input to ESP decision, servo, OLED, JSON response, and recovery.
Stage output target: First vertical slice: virtual temperature input to ESP validation, decision, safety, servo, OLED, JSON response, timeout, and recovery.
Implementation focus: Build only temperature first and prove the complete path before adding irrigation or scenarios.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 32: Send temperature with curl.
Verify the task within Stage 5 - First vertical slice.
Use this stage test focus: Validate threshold boundaries, repeated messages, invalid values, timeout safe state, and recovery after stable messages.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not add soil, tank, rain, MQTT, or database work in this slice. The website and FastAPI must not become the control authority. Every response must include reasons and rule IDs.
```

### TASK-S05-33 - Validate the message.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 33: Validate the message.
Blueprint stage: Stage 5 - First vertical slice.
Affected branches: B4: Protocol; B5: ESP communication; B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Temperature input to ESP decision, servo, OLED, JSON response, and recovery.
Stage output target: First vertical slice: virtual temperature input to ESP validation, decision, safety, servo, OLED, JSON response, timeout, and recovery.
Implementation focus: Build only temperature first and prove the complete path before adding irrigation or scenarios.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 33: Validate the message.
Verify the task within Stage 5 - First vertical slice.
Use this stage test focus: Validate threshold boundaries, repeated messages, invalid values, timeout safe state, and recovery after stable messages.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not add soil, tank, rain, MQTT, or database work in this slice. The website and FastAPI must not become the control authority. Every response must include reasons and rule IDs.
```

### TASK-S05-34 - Calculate the window command.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 34: Calculate the window command.
Blueprint stage: Stage 5 - First vertical slice.
Affected branches: B4: Protocol; B5: ESP communication; B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Temperature input to ESP decision, servo, OLED, JSON response, and recovery.
Stage output target: First vertical slice: virtual temperature input to ESP validation, decision, safety, servo, OLED, JSON response, timeout, and recovery.
Implementation focus: Build only temperature first and prove the complete path before adding irrigation or scenarios.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 34: Calculate the window command.
Verify the task within Stage 5 - First vertical slice.
Use this stage test focus: Validate threshold boundaries, repeated messages, invalid values, timeout safe state, and recovery after stable messages.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not add soil, tank, rain, MQTT, or database work in this slice. The website and FastAPI must not become the control authority. Every response must include reasons and rule IDs.
```

### TASK-S05-35 - Apply the servo command.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 35: Apply the servo command.
Blueprint stage: Stage 5 - First vertical slice.
Affected branches: B4: Protocol; B5: ESP communication; B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Temperature input to ESP decision, servo, OLED, JSON response, and recovery.
Stage output target: First vertical slice: virtual temperature input to ESP validation, decision, safety, servo, OLED, JSON response, timeout, and recovery.
Implementation focus: Build only temperature first and prove the complete path before adding irrigation or scenarios.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 35: Apply the servo command.
Verify the task within Stage 5 - First vertical slice.
Use this stage test focus: Validate threshold boundaries, repeated messages, invalid values, timeout safe state, and recovery after stable messages.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not add soil, tank, rain, MQTT, or database work in this slice. The website and FastAPI must not become the control authority. Every response must include reasons and rule IDs.
```

### TASK-S05-36 - Display the reason on OLED.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 36: Display the reason on OLED.
Blueprint stage: Stage 5 - First vertical slice.
Affected branches: B4: Protocol; B5: ESP communication; B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Temperature input to ESP decision, servo, OLED, JSON response, and recovery.
Stage output target: First vertical slice: virtual temperature input to ESP validation, decision, safety, servo, OLED, JSON response, timeout, and recovery.
Implementation focus: Build only temperature first and prove the complete path before adding irrigation or scenarios.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 36: Display the reason on OLED.
Verify the task within Stage 5 - First vertical slice.
Use this stage test focus: Validate threshold boundaries, repeated messages, invalid values, timeout safe state, and recovery after stable messages.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not add soil, tank, rain, MQTT, or database work in this slice. The website and FastAPI must not become the control authority. Every response must include reasons and rule IDs.
```

### TASK-S05-37 - Return the decision as JSON.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 37: Return the decision as JSON.
Blueprint stage: Stage 5 - First vertical slice.
Affected branches: B4: Protocol; B5: ESP communication; B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Temperature input to ESP decision, servo, OLED, JSON response, and recovery.
Stage output target: First vertical slice: virtual temperature input to ESP validation, decision, safety, servo, OLED, JSON response, timeout, and recovery.
Implementation focus: Build only temperature first and prove the complete path before adding irrigation or scenarios.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 37: Return the decision as JSON.
Verify the task within Stage 5 - First vertical slice.
Use this stage test focus: Validate threshold boundaries, repeated messages, invalid values, timeout safe state, and recovery after stable messages.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not add soil, tank, rain, MQTT, or database work in this slice. The website and FastAPI must not become the control authority. Every response must include reasons and rule IDs.
```

### TASK-S05-38 - Test repeated messages.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 38: Test repeated messages.
Blueprint stage: Stage 5 - First vertical slice.
Affected branches: B4: Protocol; B5: ESP communication; B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Temperature input to ESP decision, servo, OLED, JSON response, and recovery.
Stage output target: First vertical slice: virtual temperature input to ESP validation, decision, safety, servo, OLED, JSON response, timeout, and recovery.
Implementation focus: Build only temperature first and prove the complete path before adding irrigation or scenarios.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 38: Test repeated messages.
Verify the task within Stage 5 - First vertical slice.
Use this stage test focus: Validate threshold boundaries, repeated messages, invalid values, timeout safe state, and recovery after stable messages.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not add soil, tank, rain, MQTT, or database work in this slice. The website and FastAPI must not become the control authority. Every response must include reasons and rule IDs.
```

### TASK-S05-39 - Test invalid values.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 39: Test invalid values.
Blueprint stage: Stage 5 - First vertical slice.
Affected branches: B4: Protocol; B5: ESP communication; B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Temperature input to ESP decision, servo, OLED, JSON response, and recovery.
Stage output target: First vertical slice: virtual temperature input to ESP validation, decision, safety, servo, OLED, JSON response, timeout, and recovery.
Implementation focus: Build only temperature first and prove the complete path before adding irrigation or scenarios.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 39: Test invalid values.
Verify the task within Stage 5 - First vertical slice.
Use this stage test focus: Validate threshold boundaries, repeated messages, invalid values, timeout safe state, and recovery after stable messages.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not add soil, tank, rain, MQTT, or database work in this slice. The website and FastAPI must not become the control authority. Every response must include reasons and rule IDs.
```

### TASK-S05-40 - Test timeout and recovery.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 40: Test timeout and recovery.
Blueprint stage: Stage 5 - First vertical slice.
Affected branches: B4: Protocol; B5: ESP communication; B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Temperature input to ESP decision, servo, OLED, JSON response, and recovery.
Stage output target: First vertical slice: virtual temperature input to ESP validation, decision, safety, servo, OLED, JSON response, timeout, and recovery.
Implementation focus: Build only temperature first and prove the complete path before adding irrigation or scenarios.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 40: Test timeout and recovery.
Verify the task within Stage 5 - First vertical slice.
Use this stage test focus: Validate threshold boundaries, repeated messages, invalid values, timeout safe state, and recovery after stable messages.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not add soil, tank, rain, MQTT, or database work in this slice. The website and FastAPI must not become the control authority. Every response must include reasons and rule IDs.
```

### TASK-S06-41 - Create the local FastAPI bridge.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 41: Create the local FastAPI bridge.
Blueprint stage: Stage 6 - Browser and FastAPI.
Affected branches: B2: Website simulation; B3: FastAPI bridge; B4: Protocol; B5: ESP communication; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Bridge, website controls, virtual window, event log, and endurance updates.
Stage output target: Local FastAPI bridge and browser controls for temperature, ESP response display, virtual window, event log, and hundreds of updates.
Implementation focus: Create a transparent bridge and dashboard; keep ESP decisions authoritative.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 41: Create the local FastAPI bridge.
Verify the task within Stage 6 - Browser and FastAPI.
Use this stage test focus: Verify session IDs, sequence increments, bridge forwarding, connection errors, displayed commands, event log, and high-frequency updates.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: FastAPI coordinates and verifies; it does not decide. The browser sends sensor state and displays results; it does not bypass the ESP. Logs must capture meaningful transitions.
```

### TASK-S06-42 - Forward temperature to the ESP.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 42: Forward temperature to the ESP.
Blueprint stage: Stage 6 - Browser and FastAPI.
Affected branches: B2: Website simulation; B3: FastAPI bridge; B4: Protocol; B5: ESP communication; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Bridge, website controls, virtual window, event log, and endurance updates.
Stage output target: Local FastAPI bridge and browser controls for temperature, ESP response display, virtual window, event log, and hundreds of updates.
Implementation focus: Create a transparent bridge and dashboard; keep ESP decisions authoritative.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 42: Forward temperature to the ESP.
Verify the task within Stage 6 - Browser and FastAPI.
Use this stage test focus: Verify session IDs, sequence increments, bridge forwarding, connection errors, displayed commands, event log, and high-frequency updates.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: FastAPI coordinates and verifies; it does not decide. The browser sends sensor state and displays results; it does not bypass the ESP. Logs must capture meaningful transitions.
```

### TASK-S06-43 - Create the website connection panel.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 43: Create the website connection panel.
Blueprint stage: Stage 6 - Browser and FastAPI.
Affected branches: B2: Website simulation; B3: FastAPI bridge; B4: Protocol; B5: ESP communication; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Bridge, website controls, virtual window, event log, and endurance updates.
Stage output target: Local FastAPI bridge and browser controls for temperature, ESP response display, virtual window, event log, and hundreds of updates.
Implementation focus: Create a transparent bridge and dashboard; keep ESP decisions authoritative.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 43: Create the website connection panel.
Verify the task within Stage 6 - Browser and FastAPI.
Use this stage test focus: Verify session IDs, sequence increments, bridge forwarding, connection errors, displayed commands, event log, and high-frequency updates.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: FastAPI coordinates and verifies; it does not decide. The browser sends sensor state and displays results; it does not bypass the ESP. Logs must capture meaningful transitions.
```

### TASK-S06-44 - Create one temperature slider.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 44: Create one temperature slider.
Blueprint stage: Stage 6 - Browser and FastAPI.
Affected branches: B2: Website simulation; B3: FastAPI bridge; B4: Protocol; B5: ESP communication; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Bridge, website controls, virtual window, event log, and endurance updates.
Stage output target: Local FastAPI bridge and browser controls for temperature, ESP response display, virtual window, event log, and hundreds of updates.
Implementation focus: Create a transparent bridge and dashboard; keep ESP decisions authoritative.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 44: Create one temperature slider.
Verify the task within Stage 6 - Browser and FastAPI.
Use this stage test focus: Verify session IDs, sequence increments, bridge forwarding, connection errors, displayed commands, event log, and high-frequency updates.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: FastAPI coordinates and verifies; it does not decide. The browser sends sensor state and displays results; it does not bypass the ESP. Logs must capture meaningful transitions.
```

### TASK-S06-45 - Display the ESP response.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 45: Display the ESP response.
Blueprint stage: Stage 6 - Browser and FastAPI.
Affected branches: B2: Website simulation; B3: FastAPI bridge; B4: Protocol; B5: ESP communication; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Bridge, website controls, virtual window, event log, and endurance updates.
Stage output target: Local FastAPI bridge and browser controls for temperature, ESP response display, virtual window, event log, and hundreds of updates.
Implementation focus: Create a transparent bridge and dashboard; keep ESP decisions authoritative.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 45: Display the ESP response.
Verify the task within Stage 6 - Browser and FastAPI.
Use this stage test focus: Verify session IDs, sequence increments, bridge forwarding, connection errors, displayed commands, event log, and high-frequency updates.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: FastAPI coordinates and verifies; it does not decide. The browser sends sensor state and displays results; it does not bypass the ESP. Logs must capture meaningful transitions.
```

### TASK-S06-46 - Display the virtual window.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 46: Display the virtual window.
Blueprint stage: Stage 6 - Browser and FastAPI.
Affected branches: B2: Website simulation; B3: FastAPI bridge; B4: Protocol; B5: ESP communication; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Bridge, website controls, virtual window, event log, and endurance updates.
Stage output target: Local FastAPI bridge and browser controls for temperature, ESP response display, virtual window, event log, and hundreds of updates.
Implementation focus: Create a transparent bridge and dashboard; keep ESP decisions authoritative.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 46: Display the virtual window.
Verify the task within Stage 6 - Browser and FastAPI.
Use this stage test focus: Verify session IDs, sequence increments, bridge forwarding, connection errors, displayed commands, event log, and high-frequency updates.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: FastAPI coordinates and verifies; it does not decide. The browser sends sensor state and displays results; it does not bypass the ESP. Logs must capture meaningful transitions.
```

### TASK-S06-47 - Add an event log.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 47: Add an event log.
Blueprint stage: Stage 6 - Browser and FastAPI.
Affected branches: B2: Website simulation; B3: FastAPI bridge; B4: Protocol; B5: ESP communication; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Bridge, website controls, virtual window, event log, and endurance updates.
Stage output target: Local FastAPI bridge and browser controls for temperature, ESP response display, virtual window, event log, and hundreds of updates.
Implementation focus: Create a transparent bridge and dashboard; keep ESP decisions authoritative.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 47: Add an event log.
Verify the task within Stage 6 - Browser and FastAPI.
Use this stage test focus: Verify session IDs, sequence increments, bridge forwarding, connection errors, displayed commands, event log, and high-frequency updates.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: FastAPI coordinates and verifies; it does not decide. The browser sends sensor state and displays results; it does not bypass the ESP. Logs must capture meaningful transitions.
```

### TASK-S06-48 - Run hundreds of updates.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 48: Run hundreds of updates.
Blueprint stage: Stage 6 - Browser and FastAPI.
Affected branches: B2: Website simulation; B3: FastAPI bridge; B4: Protocol; B5: ESP communication; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Bridge, website controls, virtual window, event log, and endurance updates.
Stage output target: Local FastAPI bridge and browser controls for temperature, ESP response display, virtual window, event log, and hundreds of updates.
Implementation focus: Create a transparent bridge and dashboard; keep ESP decisions authoritative.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 48: Run hundreds of updates.
Verify the task within Stage 6 - Browser and FastAPI.
Use this stage test focus: Verify session IDs, sequence increments, bridge forwarding, connection errors, displayed commands, event log, and high-frequency updates.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: FastAPI coordinates and verifies; it does not decide. The browser sends sensor state and displays results; it does not bypass the ESP. Logs must capture meaningful transitions.
```

### TASK-S07-49 - Add soil moisture.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 49: Add soil moisture.
Blueprint stage: Stage 7 - Irrigation slice.
Affected branches: B2: Website simulation; B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Soil, tank, rain, pump hysteresis, protections, virtual actuators, warnings.
Stage output target: Greenhouse MVP inputs and outputs: soil moisture, tank level, rain, pump hysteresis, low-tank and rain protection, virtual pump/fan, warnings, and OLED pages.
Implementation focus: Extend the proven vertical slice while preserving canonical state, safety overrides, and truthful actuator vocabulary.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 49: Add soil moisture.
Verify the task within Stage 7 - Irrigation slice.
Use this stage test focus: Test moisture thresholds, tank threshold, rain override, fan/window temperature rules, warnings, and commanded versus simulated states.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Low tank and rain override irrigation. Pump hysteresis must keep prior state between 30% and 40%. Simulated state must remain separate from commanded state.
```

### TASK-S07-50 - Add tank level.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 50: Add tank level.
Blueprint stage: Stage 7 - Irrigation slice.
Affected branches: B2: Website simulation; B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Soil, tank, rain, pump hysteresis, protections, virtual actuators, warnings.
Stage output target: Greenhouse MVP inputs and outputs: soil moisture, tank level, rain, pump hysteresis, low-tank and rain protection, virtual pump/fan, warnings, and OLED pages.
Implementation focus: Extend the proven vertical slice while preserving canonical state, safety overrides, and truthful actuator vocabulary.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 50: Add tank level.
Verify the task within Stage 7 - Irrigation slice.
Use this stage test focus: Test moisture thresholds, tank threshold, rain override, fan/window temperature rules, warnings, and commanded versus simulated states.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Low tank and rain override irrigation. Pump hysteresis must keep prior state between 30% and 40%. Simulated state must remain separate from commanded state.
```

### TASK-S07-51 - Add rain.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 51: Add rain.
Blueprint stage: Stage 7 - Irrigation slice.
Affected branches: B2: Website simulation; B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Soil, tank, rain, pump hysteresis, protections, virtual actuators, warnings.
Stage output target: Greenhouse MVP inputs and outputs: soil moisture, tank level, rain, pump hysteresis, low-tank and rain protection, virtual pump/fan, warnings, and OLED pages.
Implementation focus: Extend the proven vertical slice while preserving canonical state, safety overrides, and truthful actuator vocabulary.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 51: Add rain.
Verify the task within Stage 7 - Irrigation slice.
Use this stage test focus: Test moisture thresholds, tank threshold, rain override, fan/window temperature rules, warnings, and commanded versus simulated states.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Low tank and rain override irrigation. Pump hysteresis must keep prior state between 30% and 40%. Simulated state must remain separate from commanded state.
```

### TASK-S07-52 - Add pump hysteresis.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 52: Add pump hysteresis.
Blueprint stage: Stage 7 - Irrigation slice.
Affected branches: B2: Website simulation; B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Soil, tank, rain, pump hysteresis, protections, virtual actuators, warnings.
Stage output target: Greenhouse MVP inputs and outputs: soil moisture, tank level, rain, pump hysteresis, low-tank and rain protection, virtual pump/fan, warnings, and OLED pages.
Implementation focus: Extend the proven vertical slice while preserving canonical state, safety overrides, and truthful actuator vocabulary.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 52: Add pump hysteresis.
Verify the task within Stage 7 - Irrigation slice.
Use this stage test focus: Test moisture thresholds, tank threshold, rain override, fan/window temperature rules, warnings, and commanded versus simulated states.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Low tank and rain override irrigation. Pump hysteresis must keep prior state between 30% and 40%. Simulated state must remain separate from commanded state.
```

### TASK-S07-53 - Add low-tank protection.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 53: Add low-tank protection.
Blueprint stage: Stage 7 - Irrigation slice.
Affected branches: B2: Website simulation; B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Soil, tank, rain, pump hysteresis, protections, virtual actuators, warnings.
Stage output target: Greenhouse MVP inputs and outputs: soil moisture, tank level, rain, pump hysteresis, low-tank and rain protection, virtual pump/fan, warnings, and OLED pages.
Implementation focus: Extend the proven vertical slice while preserving canonical state, safety overrides, and truthful actuator vocabulary.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 53: Add low-tank protection.
Verify the task within Stage 7 - Irrigation slice.
Use this stage test focus: Test moisture thresholds, tank threshold, rain override, fan/window temperature rules, warnings, and commanded versus simulated states.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Low tank and rain override irrigation. Pump hysteresis must keep prior state between 30% and 40%. Simulated state must remain separate from commanded state.
```

### TASK-S07-54 - Add rain protection.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 54: Add rain protection.
Blueprint stage: Stage 7 - Irrigation slice.
Affected branches: B2: Website simulation; B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Soil, tank, rain, pump hysteresis, protections, virtual actuators, warnings.
Stage output target: Greenhouse MVP inputs and outputs: soil moisture, tank level, rain, pump hysteresis, low-tank and rain protection, virtual pump/fan, warnings, and OLED pages.
Implementation focus: Extend the proven vertical slice while preserving canonical state, safety overrides, and truthful actuator vocabulary.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 54: Add rain protection.
Verify the task within Stage 7 - Irrigation slice.
Use this stage test focus: Test moisture thresholds, tank threshold, rain override, fan/window temperature rules, warnings, and commanded versus simulated states.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Low tank and rain override irrigation. Pump hysteresis must keep prior state between 30% and 40%. Simulated state must remain separate from commanded state.
```

### TASK-S07-55 - Add virtual pump and fan.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 55: Add virtual pump and fan.
Blueprint stage: Stage 7 - Irrigation slice.
Affected branches: B2: Website simulation; B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Soil, tank, rain, pump hysteresis, protections, virtual actuators, warnings.
Stage output target: Greenhouse MVP inputs and outputs: soil moisture, tank level, rain, pump hysteresis, low-tank and rain protection, virtual pump/fan, warnings, and OLED pages.
Implementation focus: Extend the proven vertical slice while preserving canonical state, safety overrides, and truthful actuator vocabulary.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 55: Add virtual pump and fan.
Verify the task within Stage 7 - Irrigation slice.
Use this stage test focus: Test moisture thresholds, tank threshold, rain override, fan/window temperature rules, warnings, and commanded versus simulated states.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Low tank and rain override irrigation. Pump hysteresis must keep prior state between 30% and 40%. Simulated state must remain separate from commanded state.
```

### TASK-S07-56 - Connect LED and buzzer warnings.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 56: Connect LED and buzzer warnings.
Blueprint stage: Stage 7 - Irrigation slice.
Affected branches: B2: Website simulation; B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Soil, tank, rain, pump hysteresis, protections, virtual actuators, warnings.
Stage output target: Greenhouse MVP inputs and outputs: soil moisture, tank level, rain, pump hysteresis, low-tank and rain protection, virtual pump/fan, warnings, and OLED pages.
Implementation focus: Extend the proven vertical slice while preserving canonical state, safety overrides, and truthful actuator vocabulary.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 56: Connect LED and buzzer warnings.
Verify the task within Stage 7 - Irrigation slice.
Use this stage test focus: Test moisture thresholds, tank threshold, rain override, fan/window temperature rules, warnings, and commanded versus simulated states.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Low tank and rain override irrigation. Pump hysteresis must keep prior state between 30% and 40%. Simulated state must remain separate from commanded state.
```

### TASK-S07-57 - Add corresponding OLED pages.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 57: Add corresponding OLED pages.
Blueprint stage: Stage 7 - Irrigation slice.
Affected branches: B2: Website simulation; B6: Sensor abstraction; B7: State management; B8: Decision engine; B9: Safety supervisor; B10: Actuator abstraction; B11: Physical outputs; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Soil, tank, rain, pump hysteresis, protections, virtual actuators, warnings.
Stage output target: Greenhouse MVP inputs and outputs: soil moisture, tank level, rain, pump hysteresis, low-tank and rain protection, virtual pump/fan, warnings, and OLED pages.
Implementation focus: Extend the proven vertical slice while preserving canonical state, safety overrides, and truthful actuator vocabulary.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 57: Add corresponding OLED pages.
Verify the task within Stage 7 - Irrigation slice.
Use this stage test focus: Test moisture thresholds, tank threshold, rain override, fan/window temperature rules, warnings, and commanded versus simulated states.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Low tank and rain override irrigation. Pump hysteresis must keep prior state between 30% and 40%. Simulated state must remain separate from commanded state.
```

### TASK-S08-58 - Add normal, hot, dry-soil, low-tank, rain, invalid-data, and communication-loss scenarios.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 58: Add normal, hot, dry-soil, low-tank, rain, invalid-data, and communication-loss scenarios.
Blueprint stage: Stage 8 - Scenario testing.
Affected branches: B2: Website simulation; B3: FastAPI bridge; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Preset scenarios with expected commands, alarm, mode, response time, and pass/fail.
Stage output target: Scenario engine with normal, hot, dry-soil, low-tank, rain, invalid-data, and communication-loss scenarios plus automatic PASS/FAIL comparison.
Implementation focus: Turn known blueprint behavior into repeatable scenario timelines with expected commands, modes, alarms, and response times.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 58: Add normal, hot, dry-soil, low-tank, rain, invalid-data, and communication-loss scenarios.
Verify the task within Stage 8 - Scenario testing.
Use this stage test focus: Run every scenario and record expected versus actual results with pass/fail evidence.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Scenario logic must test the ESP path, not replace it. Expected results must include alarm and response time. Invalid data must be rejected before state mutation.
```

### TASK-S08-59 - Define expected commands, mode, alarm, and response time.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 59: Define expected commands, mode, alarm, and response time.
Blueprint stage: Stage 8 - Scenario testing.
Affected branches: B2: Website simulation; B3: FastAPI bridge; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Preset scenarios with expected commands, alarm, mode, response time, and pass/fail.
Stage output target: Scenario engine with normal, hot, dry-soil, low-tank, rain, invalid-data, and communication-loss scenarios plus automatic PASS/FAIL comparison.
Implementation focus: Turn known blueprint behavior into repeatable scenario timelines with expected commands, modes, alarms, and response times.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 59: Define expected commands, mode, alarm, and response time.
Verify the task within Stage 8 - Scenario testing.
Use this stage test focus: Run every scenario and record expected versus actual results with pass/fail evidence.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Scenario logic must test the ESP path, not replace it. Expected results must include alarm and response time. Invalid data must be rejected before state mutation.
```

### TASK-S08-60 - Add automatic PASS/FAIL comparison.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 60: Add automatic PASS/FAIL comparison.
Blueprint stage: Stage 8 - Scenario testing.
Affected branches: B2: Website simulation; B3: FastAPI bridge; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Preset scenarios with expected commands, alarm, mode, response time, and pass/fail.
Stage output target: Scenario engine with normal, hot, dry-soil, low-tank, rain, invalid-data, and communication-loss scenarios plus automatic PASS/FAIL comparison.
Implementation focus: Turn known blueprint behavior into repeatable scenario timelines with expected commands, modes, alarms, and response times.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 60: Add automatic PASS/FAIL comparison.
Verify the task within Stage 8 - Scenario testing.
Use this stage test focus: Run every scenario and record expected versus actual results with pass/fail evidence.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Scenario logic must test the ESP path, not replace it. Expected results must include alarm and response time. Invalid data must be rejected before state mutation.
```

### TASK-S09-61 - Add simulated actuator feedback.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 61: Add simulated actuator feedback.
Blueprint stage: Stage 9 - Closed-loop simulation.
Affected branches: B2: Website simulation; B9: Safety supervisor; B10: Actuator abstraction; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Actuator feedback, delays, failed starts, stuck faults, and servo mismatch.
Stage output target: Closed-loop actuator simulation with feedback, delays, failed starts, stuck faults, incorrect servo position, and ESP fault response.
Implementation focus: Add feedback evidence so the ESP can detect mismatch and failure without pretending commands equal physical truth.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 61: Add simulated actuator feedback.
Verify the task within Stage 9 - Closed-loop simulation.
Use this stage test focus: Inject delayed, failed, stuck-on, stuck-off, and wrong-position feedback and confirm ESP safety behavior and logged faults.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Commanded state is not measured state. Fault evidence must be explicit. Feedback faults must influence safety or recovery behavior.
```

### TASK-S09-62 - Add startup delays.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 62: Add startup delays.
Blueprint stage: Stage 9 - Closed-loop simulation.
Affected branches: B2: Website simulation; B9: Safety supervisor; B10: Actuator abstraction; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Actuator feedback, delays, failed starts, stuck faults, and servo mismatch.
Stage output target: Closed-loop actuator simulation with feedback, delays, failed starts, stuck faults, incorrect servo position, and ESP fault response.
Implementation focus: Add feedback evidence so the ESP can detect mismatch and failure without pretending commands equal physical truth.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 62: Add startup delays.
Verify the task within Stage 9 - Closed-loop simulation.
Use this stage test focus: Inject delayed, failed, stuck-on, stuck-off, and wrong-position feedback and confirm ESP safety behavior and logged faults.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Commanded state is not measured state. Fault evidence must be explicit. Feedback faults must influence safety or recovery behavior.
```

### TASK-S09-63 - Add failed startup.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 63: Add failed startup.
Blueprint stage: Stage 9 - Closed-loop simulation.
Affected branches: B2: Website simulation; B9: Safety supervisor; B10: Actuator abstraction; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Actuator feedback, delays, failed starts, stuck faults, and servo mismatch.
Stage output target: Closed-loop actuator simulation with feedback, delays, failed starts, stuck faults, incorrect servo position, and ESP fault response.
Implementation focus: Add feedback evidence so the ESP can detect mismatch and failure without pretending commands equal physical truth.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 63: Add failed startup.
Verify the task within Stage 9 - Closed-loop simulation.
Use this stage test focus: Inject delayed, failed, stuck-on, stuck-off, and wrong-position feedback and confirm ESP safety behavior and logged faults.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Commanded state is not measured state. Fault evidence must be explicit. Feedback faults must influence safety or recovery behavior.
```

### TASK-S09-64 - Add stuck-on and stuck-off faults.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 64: Add stuck-on and stuck-off faults.
Blueprint stage: Stage 9 - Closed-loop simulation.
Affected branches: B2: Website simulation; B9: Safety supervisor; B10: Actuator abstraction; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Actuator feedback, delays, failed starts, stuck faults, and servo mismatch.
Stage output target: Closed-loop actuator simulation with feedback, delays, failed starts, stuck faults, incorrect servo position, and ESP fault response.
Implementation focus: Add feedback evidence so the ESP can detect mismatch and failure without pretending commands equal physical truth.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 64: Add stuck-on and stuck-off faults.
Verify the task within Stage 9 - Closed-loop simulation.
Use this stage test focus: Inject delayed, failed, stuck-on, stuck-off, and wrong-position feedback and confirm ESP safety behavior and logged faults.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Commanded state is not measured state. Fault evidence must be explicit. Feedback faults must influence safety or recovery behavior.
```

### TASK-S09-65 - Add incorrect virtual servo position.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 65: Add incorrect virtual servo position.
Blueprint stage: Stage 9 - Closed-loop simulation.
Affected branches: B2: Website simulation; B9: Safety supervisor; B10: Actuator abstraction; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Actuator feedback, delays, failed starts, stuck faults, and servo mismatch.
Stage output target: Closed-loop actuator simulation with feedback, delays, failed starts, stuck faults, incorrect servo position, and ESP fault response.
Implementation focus: Add feedback evidence so the ESP can detect mismatch and failure without pretending commands equal physical truth.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 65: Add incorrect virtual servo position.
Verify the task within Stage 9 - Closed-loop simulation.
Use this stage test focus: Inject delayed, failed, stuck-on, stuck-off, and wrong-position feedback and confirm ESP safety behavior and logged faults.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Commanded state is not measured state. Fault evidence must be explicit. Feedback faults must influence safety or recovery behavior.
```

### TASK-S09-66 - Make the ESP respond to feedback faults.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 66: Make the ESP respond to feedback faults.
Blueprint stage: Stage 9 - Closed-loop simulation.
Affected branches: B2: Website simulation; B9: Safety supervisor; B10: Actuator abstraction; B12: Observability; B13: Testing.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Actuator feedback, delays, failed starts, stuck faults, and servo mismatch.
Stage output target: Closed-loop actuator simulation with feedback, delays, failed starts, stuck faults, incorrect servo position, and ESP fault response.
Implementation focus: Add feedback evidence so the ESP can detect mismatch and failure without pretending commands equal physical truth.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 66: Make the ESP respond to feedback faults.
Verify the task within Stage 9 - Closed-loop simulation.
Use this stage test focus: Inject delayed, failed, stuck-on, stuck-off, and wrong-position feedback and confirm ESP safety behavior and logged faults.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Commanded state is not measured state. Fault evidence must be explicit. Feedback faults must influence safety or recovery behavior.
```

### TASK-S10-67 - Add recording and replay.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 67: Add recording and replay.
Blueprint stage: Stage 10 - Reliability.
Affected branches: B3: FastAPI bridge; B4: Protocol; B12: Observability; B13: Testing; B14: Recording and replay.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Recording, replay, rule versions, endurance, watchdog decision, and limits.
Stage output target: Recording, replay, rule versioning, endurance tests, watchdog decision, and documented limits.
Implementation focus: Make experiments reproducible and regressions visible before broader platform expansion.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 67: Add recording and replay.
Verify the task within Stage 10 - Reliability.
Use this stage test focus: Replay identical sequences against changed firmware or rule versions, run endurance updates, and document unrecovered failures.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Record protocol and rule versions. Do not add a watchdog until runtime behavior is understood. Known limits must be explicit.
```

### TASK-S10-68 - Add rule versioning.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 68: Add rule versioning.
Blueprint stage: Stage 10 - Reliability.
Affected branches: B3: FastAPI bridge; B4: Protocol; B12: Observability; B13: Testing; B14: Recording and replay.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Recording, replay, rule versions, endurance, watchdog decision, and limits.
Stage output target: Recording, replay, rule versioning, endurance tests, watchdog decision, and documented limits.
Implementation focus: Make experiments reproducible and regressions visible before broader platform expansion.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 68: Add rule versioning.
Verify the task within Stage 10 - Reliability.
Use this stage test focus: Replay identical sequences against changed firmware or rule versions, run endurance updates, and document unrecovered failures.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Record protocol and rule versions. Do not add a watchdog until runtime behavior is understood. Known limits must be explicit.
```

### TASK-S10-69 - Run long-duration tests.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 69: Run long-duration tests.
Blueprint stage: Stage 10 - Reliability.
Affected branches: B3: FastAPI bridge; B4: Protocol; B12: Observability; B13: Testing; B14: Recording and replay.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Recording, replay, rule versions, endurance, watchdog decision, and limits.
Stage output target: Recording, replay, rule versioning, endurance tests, watchdog decision, and documented limits.
Implementation focus: Make experiments reproducible and regressions visible before broader platform expansion.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 69: Run long-duration tests.
Verify the task within Stage 10 - Reliability.
Use this stage test focus: Replay identical sequences against changed firmware or rule versions, run endurance updates, and document unrecovered failures.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Record protocol and rule versions. Do not add a watchdog until runtime behavior is understood. Known limits must be explicit.
```

### TASK-S10-70 - Add a watchdog only after runtime stability.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 70: Add a watchdog only after runtime stability.
Blueprint stage: Stage 10 - Reliability.
Affected branches: B3: FastAPI bridge; B4: Protocol; B12: Observability; B13: Testing; B14: Recording and replay.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Recording, replay, rule versions, endurance, watchdog decision, and limits.
Stage output target: Recording, replay, rule versioning, endurance tests, watchdog decision, and documented limits.
Implementation focus: Make experiments reproducible and regressions visible before broader platform expansion.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 70: Add a watchdog only after runtime stability.
Verify the task within Stage 10 - Reliability.
Use this stage test focus: Replay identical sequences against changed firmware or rule versions, run endurance updates, and document unrecovered failures.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Record protocol and rule versions. Do not add a watchdog until runtime behavior is understood. Known limits must be explicit.
```

### TASK-S10-71 - Document known limits.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 71: Document known limits.
Blueprint stage: Stage 10 - Reliability.
Affected branches: B3: FastAPI bridge; B4: Protocol; B12: Observability; B13: Testing; B14: Recording and replay.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Recording, replay, rule versions, endurance, watchdog decision, and limits.
Stage output target: Recording, replay, rule versioning, endurance tests, watchdog decision, and documented limits.
Implementation focus: Make experiments reproducible and regressions visible before broader platform expansion.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 71: Document known limits.
Verify the task within Stage 10 - Reliability.
Use this stage test focus: Replay identical sequences against changed firmware or rule versions, run endurance updates, and document unrecovered failures.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Record protocol and rule versions. Do not add a watchdog until runtime behavior is understood. Known limits must be explicit.
```

### TASK-S11-72 - Add a real temperature sensor.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 72: Add a real temperature sensor.
Blueprint stage: Stage 11 - Physical migration.
Affected branches: B6: Sensor abstraction; B7: State management; B10: Actuator abstraction; B11: Physical outputs; B13: Testing; B15: Physical expansion.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Physical sensors, source selection, pump driver, and feedback evidence.
Stage output target: Physical migration of sensors and pump with per-sensor source selection and feedback where possible.
Implementation focus: Replace virtual components one by one without rewriting decision or safety code.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 72: Add a real temperature sensor.
Verify the task within Stage 11 - Physical migration.
Use this stage test focus: Verify virtual, physical, hybrid, and disabled source modes and prove decision/safety behavior is unchanged.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Virtual mode must remain available. Network values do not become GPIO signals. Physical feedback must be truthful and named.
```

### TASK-S11-73 - Add per-sensor source selection.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 73: Add per-sensor source selection.
Blueprint stage: Stage 11 - Physical migration.
Affected branches: B6: Sensor abstraction; B7: State management; B10: Actuator abstraction; B11: Physical outputs; B13: Testing; B15: Physical expansion.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Physical sensors, source selection, pump driver, and feedback evidence.
Stage output target: Physical migration of sensors and pump with per-sensor source selection and feedback where possible.
Implementation focus: Replace virtual components one by one without rewriting decision or safety code.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 73: Add per-sensor source selection.
Verify the task within Stage 11 - Physical migration.
Use this stage test focus: Verify virtual, physical, hybrid, and disabled source modes and prove decision/safety behavior is unchanged.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Virtual mode must remain available. Network values do not become GPIO signals. Physical feedback must be truthful and named.
```

### TASK-S11-74 - Add real soil, tank, and rain sensors.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 74: Add real soil, tank, and rain sensors.
Blueprint stage: Stage 11 - Physical migration.
Affected branches: B6: Sensor abstraction; B7: State management; B10: Actuator abstraction; B11: Physical outputs; B13: Testing; B15: Physical expansion.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Physical sensors, source selection, pump driver, and feedback evidence.
Stage output target: Physical migration of sensors and pump with per-sensor source selection and feedback where possible.
Implementation focus: Replace virtual components one by one without rewriting decision or safety code.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 74: Add real soil, tank, and rain sensors.
Verify the task within Stage 11 - Physical migration.
Use this stage test focus: Verify virtual, physical, hybrid, and disabled source modes and prove decision/safety behavior is unchanged.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Virtual mode must remain available. Network values do not become GPIO signals. Physical feedback must be truthful and named.
```

### TASK-S11-75 - Add a properly driven pump.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 75: Add a properly driven pump.
Blueprint stage: Stage 11 - Physical migration.
Affected branches: B6: Sensor abstraction; B7: State management; B10: Actuator abstraction; B11: Physical outputs; B13: Testing; B15: Physical expansion.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Physical sensors, source selection, pump driver, and feedback evidence.
Stage output target: Physical migration of sensors and pump with per-sensor source selection and feedback where possible.
Implementation focus: Replace virtual components one by one without rewriting decision or safety code.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 75: Add a properly driven pump.
Verify the task within Stage 11 - Physical migration.
Use this stage test focus: Verify virtual, physical, hybrid, and disabled source modes and prove decision/safety behavior is unchanged.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Virtual mode must remain available. Network values do not become GPIO signals. Physical feedback must be truthful and named.
```

### TASK-S11-76 - Add physical feedback where possible.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 76: Add physical feedback where possible.
Blueprint stage: Stage 11 - Physical migration.
Affected branches: B6: Sensor abstraction; B7: State management; B10: Actuator abstraction; B11: Physical outputs; B13: Testing; B15: Physical expansion.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports Physical sensors, source selection, pump driver, and feedback evidence.
Stage output target: Physical migration of sensors and pump with per-sensor source selection and feedback where possible.
Implementation focus: Replace virtual components one by one without rewriting decision or safety code.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 76: Add physical feedback where possible.
Verify the task within Stage 11 - Physical migration.
Use this stage test focus: Verify virtual, physical, hybrid, and disabled source modes and prove decision/safety behavior is unchanged.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Virtual mode must remain available. Network values do not become GPIO signals. Physical feedback must be truthful and named.
```

### TASK-S12-77 - Add MQTT.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 77: Add MQTT.
Blueprint stage: Stage 12 - Platform growth.
Affected branches: B3: FastAPI bridge; B12: Observability; B13: Testing; B16: Platform expansion.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports MQTT, multi-device, storage, authentication, remote access, and packaging.
Stage output target: Platform growth only when justified: MQTT, multiple devices, persistent storage, authentication, remote access, and reusable packaging.
Implementation focus: Add platform features only after the connected control loop is observable, testable, and stable.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 77: Add MQTT.
Verify the task within Stage 12 - Platform growth.
Use this stage test focus: Verify each platform addition is justified by a real workflow and does not weaken local-first operation or ESP authority.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not let non-critical features delay the proven control loop. Remote dashboards must not bypass safety. Persistent data must support replay, history, or customer workflow.
```

### TASK-S12-78 - Add multiple ESP devices.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 78: Add multiple ESP devices.
Blueprint stage: Stage 12 - Platform growth.
Affected branches: B3: FastAPI bridge; B12: Observability; B13: Testing; B16: Platform expansion.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports MQTT, multi-device, storage, authentication, remote access, and packaging.
Stage output target: Platform growth only when justified: MQTT, multiple devices, persistent storage, authentication, remote access, and reusable packaging.
Implementation focus: Add platform features only after the connected control loop is observable, testable, and stable.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 78: Add multiple ESP devices.
Verify the task within Stage 12 - Platform growth.
Use this stage test focus: Verify each platform addition is justified by a real workflow and does not weaken local-first operation or ESP authority.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not let non-critical features delay the proven control loop. Remote dashboards must not bypass safety. Persistent data must support replay, history, or customer workflow.
```

### TASK-S12-79 - Add persistent storage.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 79: Add persistent storage.
Blueprint stage: Stage 12 - Platform growth.
Affected branches: B3: FastAPI bridge; B12: Observability; B13: Testing; B16: Platform expansion.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports MQTT, multi-device, storage, authentication, remote access, and packaging.
Stage output target: Platform growth only when justified: MQTT, multiple devices, persistent storage, authentication, remote access, and reusable packaging.
Implementation focus: Add platform features only after the connected control loop is observable, testable, and stable.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 79: Add persistent storage.
Verify the task within Stage 12 - Platform growth.
Use this stage test focus: Verify each platform addition is justified by a real workflow and does not weaken local-first operation or ESP authority.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not let non-critical features delay the proven control loop. Remote dashboards must not bypass safety. Persistent data must support replay, history, or customer workflow.
```

### TASK-S12-80 - Add authentication.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 80: Add authentication.
Blueprint stage: Stage 12 - Platform growth.
Affected branches: B3: FastAPI bridge; B12: Observability; B13: Testing; B16: Platform expansion.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports MQTT, multi-device, storage, authentication, remote access, and packaging.
Stage output target: Platform growth only when justified: MQTT, multiple devices, persistent storage, authentication, remote access, and reusable packaging.
Implementation focus: Add platform features only after the connected control loop is observable, testable, and stable.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 80: Add authentication.
Verify the task within Stage 12 - Platform growth.
Use this stage test focus: Verify each platform addition is justified by a real workflow and does not weaken local-first operation or ESP authority.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not let non-critical features delay the proven control loop. Remote dashboards must not bypass safety. Persistent data must support replay, history, or customer workflow.
```

### TASK-S12-81 - Add remote access.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 81: Add remote access.
Blueprint stage: Stage 12 - Platform growth.
Affected branches: B3: FastAPI bridge; B12: Observability; B13: Testing; B16: Platform expansion.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports MQTT, multi-device, storage, authentication, remote access, and packaging.
Stage output target: Platform growth only when justified: MQTT, multiple devices, persistent storage, authentication, remote access, and reusable packaging.
Implementation focus: Add platform features only after the connected control loop is observable, testable, and stable.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 81: Add remote access.
Verify the task within Stage 12 - Platform growth.
Use this stage test focus: Verify each platform addition is justified by a real workflow and does not weaken local-first operation or ESP authority.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not let non-critical features delay the proven control loop. Remote dashboards must not bypass safety. Persistent data must support replay, history, or customer workflow.
```

### TASK-S12-82 - Package the system as a reusable control and testing platform.

Implementation prompt:

```text
You are implementing AgriControl roadmap task 82: Package the system as a reusable control and testing platform.
Blueprint stage: Stage 12 - Platform growth.
Affected branches: B3: FastAPI bridge; B12: Observability; B13: Testing; B16: Platform expansion.
Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.
Objective: deliver the smallest durable change that advances this task and supports MQTT, multi-device, storage, authentication, remote access, and packaging.
Stage output target: Platform growth only when justified: MQTT, multiple devices, persistent storage, authentication, remote access, and reusable packaging.
Implementation focus: Add platform features only after the connected control loop is observable, testable, and stable.
Architecture constraints:
- The ESP32 remains the control authority.
- No interface, sensor, actuator, or communication method may bypass the central control loop.
- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.
- Safety supervisor has final authority over every command.
- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.
Required deliverables:
- Source, documentation, hardware note, or test artifact appropriate to this task.
- Evidence showing what was verified.
- Updated docs/PROJECT_STATE.md if project state changed.
- Updated data/progress-baseline.json only if status advancement is supported by evidence.
Stop condition: if required hardware facts are missing, record the blocker instead of guessing.
```

Test prompt:

```text
You are testing AgriControl roadmap task 82: Package the system as a reusable control and testing platform.
Verify the task within Stage 12 - Platform growth.
Use this stage test focus: Verify each platform addition is justified by a real workflow and does not weaken local-first operation or ESP authority.
Test requirements:
- Confirm the change preserves the central control loop.
- Confirm touched branch contracts still hold.
- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.
- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.
- State whether the task may be marked done, must remain active, or is blocked.
Known hazards to check: Do not let non-critical features delay the proven control loop. Remote dashboards must not bypass safety. Persistent data must support replay, history, or customer workflow.
```

## Completion Gate Test Prompts

### GATE-A - First vertical slice

```text
You are verifying Gate A: First vertical slice.
Read the blueprint, current project state, progress baseline, and all source relevant to the gate.
For each criterion, run or define a concrete test and record pass, fail, blocked, or not applicable.
A criterion may be marked done only when evidence exists.
Report exact commands, HTTP responses, test IDs, serial logs, screenshots, or hardware observations.
Criteria:
- Temperature message accepted and validated
- Correct window command at all boundaries
- Servo moves without resetting the ESP
- OLED shows value and reason
- Website receives the response
- Timeout enters defined safe state
- Recovery requires stable valid messages
```

### GATE-B - Greenhouse MVP

```text
You are verifying Gate B: Greenhouse MVP.
Read the blueprint, current project state, progress baseline, and all source relevant to the gate.
For each criterion, run or define a concrete test and record pass, fail, blocked, or not applicable.
A criterion may be marked done only when evidence exists.
Report exact commands, HTTP responses, test IDs, serial logs, screenshots, or hardware observations.
Criteria:
- Temperature, soil, tank, and rain supported
- Pump hysteresis works
- Low tank and rain override irrigation
- OLED, LED, buzzer, and servo are coherent
- Preset scenarios pass automatically
- Commanded and simulated states are separate
```

### GATE-C - Test platform

```text
You are verifying Gate C: Test platform.
Read the blueprint, current project state, progress baseline, and all source relevant to the gate.
For each criterion, run or define a concrete test and record pass, fail, blocked, or not applicable.
A criterion may be marked done only when evidence exists.
Report exact commands, HTTP responses, test IDs, serial logs, screenshots, or hardware observations.
Criteria:
- Actuator failures can be injected
- Feedback faults change ESP behavior
- Sessions can be recorded and replayed
- Regression results compare firmware or rule versions
- Endurance run completes without unrecovered failure
```

### GATE-D - Physical migration

```text
You are verifying Gate D: Physical migration.
Read the blueprint, current project state, progress baseline, and all source relevant to the gate.
For each criterion, run or define a concrete test and record pass, fail, blocked, or not applicable.
A criterion may be marked done only when evidence exists.
Report exact commands, HTTP responses, test IDs, serial logs, screenshots, or hardware observations.
Criteria:
- At least one physical sensor can replace its virtual counterpart
- Per-sensor source selection works
- Decision and safety code does not require rewriting
- Virtual mode remains available for testing
```

### GATE-E - Platform expansion

```text
You are verifying Gate E: Platform expansion.
Read the blueprint, current project state, progress baseline, and all source relevant to the gate.
For each criterion, run or define a concrete test and record pass, fail, blocked, or not applicable.
A criterion may be marked done only when evidence exists.
Report exact commands, HTTP responses, test IDs, serial logs, screenshots, or hardware observations.
Criteria:
- Multiple devices justify MQTT
- Persistent history justifies a database
- Remote users justify authentication
- A repeatable customer workflow justifies SaaS packaging
```

## Reusable Test Workflow Prompts

### TEST-WF-UNIT-001 - Pure Logic Unit Test Prompt

Scope: Decision, safety, state, protocol, and adapters

```text
Create host-runnable unit tests for pure logic. Cover normal rules, rejection cases, safe-state overrides, and event outputs. Tests must run without hardware.
```

Required cases:

- Temperature thresholds
- Irrigation hysteresis
- Low tank override
- Rain override
- Invalid sensor ranges
- State transition legality

### TEST-WF-BOUNDARY-001 - Exact Boundary Test Prompt

Scope: Decision and validation thresholds

```text
Create tests at exact threshold values and just around each threshold. Include temperature 28.0, 28.1, 35.0, 35.1 C; moisture 29.9, 30.0, 40.0, 40.1%; tank 14.9, 15.0%; and invalid range edges.
```

Required cases:

- Expected command
- Triggered rule ID
- Reason text
- No floating-point ambiguity
- Previous pump state for hysteresis

### TEST-WF-SEQUENCE-001 - Stateful Sequence Test Prompt

Scope: Hysteresis, recovery, stale data, and replay

```text
Create sequence tests where previous state matters. Include moisture 50 -> 20 -> 35 -> 45%, communication active -> stale -> recovery, and repeated browser session sequences.
```

Required cases:

- Previous actuator state
- Monotonic timestamps
- Stable valid recovery count
- Event order
- Replay repeatability

### TEST-WF-INTEGRATION-001 - End-To-End Integration Test Prompt

Scope: Website, FastAPI, ESP, actuator manager, outputs, and feedback

```text
Test the connected path from website input through FastAPI, ESP validation, decision, safety, outputs, virtual feedback, event storage, and dashboard result.
```

Required cases:

- Versioned request
- ESP response
- Servo/OLED/LED/buzzer command
- Website display
- Event timeline
- PASS/FAIL result

### TEST-WF-FAILURE-001 - Failure And Safety Test Prompt

Scope: Bad input, communication loss, actuator faults, and emergency handling

```text
Inject failures and confirm the system enters the correct safe state, logs the reason, and recovers only after defined valid evidence.
```

Required cases:

- Bad JSON
- Timeout
- Wi-Fi loss
- Low tank
- Failed startup
- Stuck on
- Stuck off
- Emergency stop

### TEST-WF-ENDURANCE-001 - Endurance And Stability Test Prompt

Scope: Runtime reliability and long-duration behavior

```text
Run long-duration updates and record memory, response time, reconnection behavior, event volume, and unrecovered failures. Do not add watchdog behavior until this evidence exists.
```

Required cases:

- Hundreds of browser updates
- Thousands of ESP updates
- No blocking safety loop
- No unrecovered failure
- Known limit documentation

### TEST-WF-REPLAY-001 - Recording And Replay Test Prompt

Scope: Regression detection

```text
Record protocol/rule versions, input timing, decisions, overrides, commands, feedback, faults, and test results, then replay against changed firmware or rule versions and produce a comparison report.
```

Required cases:

- Same input sequence
- Version comparison
- Expected versus actual commands
- Safety override comparison
- Regression summary

## Machine-Readable Catalog

The same library is available as `data/prompt-test-library.json` and publicly as `web-build/data/prompt-test-library.json`.

