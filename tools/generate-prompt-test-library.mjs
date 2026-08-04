import { mkdir, readFile, writeFile } from "node:fs/promises";

const baselinePath = new URL("../data/progress-baseline.json", import.meta.url);
const docsOutputPath = new URL("../docs/PROMPT_TEST_LIBRARY.md", import.meta.url);
const dataOutputPath = new URL("../data/prompt-test-library.json", import.meta.url);
const publicDocsOutputPath = new URL("../web-build/docs/PROMPT_TEST_LIBRARY.md", import.meta.url);
const publicDataOutputPath = new URL("../web-build/data/prompt-test-library.json", import.meta.url);

const baseline = JSON.parse(await readFile(baselinePath, "utf8"));

const stageBlueprint = {
  1: {
    branchIds: [1, 4, 11, 13],
    output: "A confirmed hardware and requirements foundation: board, firmware toolchain and version, pin map, wiring checks, first use case, safe states, protocol, and acceptance tests.",
    implementationFocus: "Collect facts, write durable specifications, and avoid guessing hardware details.",
    testFocus: "Verify the recorded facts against hardware evidence, commands, photos, serial output, or explicit user confirmation.",
    hazards: ["Do not invent board variants or pin mappings.", "Do not mark wiring verified without evidence.", "Do not start platform features before the foundation is stable."]
  },
  2: {
    branchIds: [6, 7, 8, 9, 13],
    output: "Pure logic modules for canonical sensors, system state, actuator state, decision rules, safety overrides, and deterministic tests.",
    implementationFocus: "Build host-runnable logic before firmware integration, keeping decision and safety separate.",
    testFocus: "Run unit, boundary, conflict, and sequence tests for temperature, irrigation, hysteresis, and safety priority behavior.",
    hazards: ["Decision logic must not call hardware or network code.", "Safety supervisor must have final authority.", "Hysteresis tests require sequences, not only isolated values."]
  },
  3: {
    branchIds: [10, 11, 12, 13],
    output: "Verified local output drivers for OLED, NeoPixel, buzzer, servo, and combined output behavior.",
    implementationFocus: "Test each physical output independently, then through the actuator manager boundary.",
    testFocus: "Record hardware observations, state-change-only buzzer behavior, OLED warning priority, servo angles, and power stability.",
    hazards: ["Servo power must not reset the ESP.", "Drivers must only be called by the actuator manager.", "Do not report commanded output as measured physical state."]
  },
  4: {
    branchIds: [5, 7, 12, 13],
    output: "Non-blocking ESP runtime with shared state, events, stale-data detection, recovery, HTTP server, and validation limits.",
    implementationFocus: "Keep communication reliable while never blocking safety or output tasks.",
    testFocus: "Exercise communication states, oversized input, malformed JSON, stale data, recovery, and runtime responsiveness.",
    hazards: ["Communication layer must not evaluate behavior rules.", "Safety timeouts use ESP monotonic time.", "Request-size limits must be explicit."]
  },
  5: {
    branchIds: [4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
    output: "First vertical slice: virtual temperature input to ESP validation, decision, safety, servo, OLED, JSON response, timeout, and recovery.",
    implementationFocus: "Build only temperature first and prove the complete path before adding irrigation or scenarios.",
    testFocus: "Validate threshold boundaries, repeated messages, invalid values, timeout safe state, and recovery after stable messages.",
    hazards: ["Do not add soil, tank, rain, MQTT, or database work in this slice.", "The website and FastAPI must not become the control authority.", "Every response must include reasons and rule IDs."]
  },
  6: {
    branchIds: [2, 3, 4, 5, 12, 13],
    output: "Local FastAPI bridge and browser controls for temperature, ESP response display, virtual window, event log, and hundreds of updates.",
    implementationFocus: "Create a transparent bridge and dashboard; keep ESP decisions authoritative.",
    testFocus: "Verify session IDs, sequence increments, bridge forwarding, connection errors, displayed commands, event log, and high-frequency updates.",
    hazards: ["FastAPI coordinates and verifies; it does not decide.", "The browser sends sensor state and displays results; it does not bypass the ESP.", "Logs must capture meaningful transitions."]
  },
  7: {
    branchIds: [2, 6, 7, 8, 9, 10, 11, 12, 13],
    output: "Greenhouse MVP inputs and outputs: soil moisture, tank level, rain, pump hysteresis, low-tank and rain protection, virtual pump/fan, warnings, and OLED pages.",
    implementationFocus: "Extend the proven vertical slice while preserving canonical state, safety overrides, and truthful actuator vocabulary.",
    testFocus: "Test moisture thresholds, tank threshold, rain override, fan/window temperature rules, warnings, and commanded versus simulated states.",
    hazards: ["Low tank and rain override irrigation.", "Pump hysteresis must keep prior state between 30% and 40%.", "Simulated state must remain separate from commanded state."]
  },
  8: {
    branchIds: [2, 3, 12, 13],
    output: "Scenario engine with normal, hot, dry-soil, low-tank, rain, invalid-data, and communication-loss scenarios plus automatic PASS/FAIL comparison.",
    implementationFocus: "Turn known blueprint behavior into repeatable scenario timelines with expected commands, modes, alarms, and response times.",
    testFocus: "Run every scenario and record expected versus actual results with pass/fail evidence.",
    hazards: ["Scenario logic must test the ESP path, not replace it.", "Expected results must include alarm and response time.", "Invalid data must be rejected before state mutation."]
  },
  9: {
    branchIds: [2, 9, 10, 12, 13],
    output: "Closed-loop actuator simulation with feedback, delays, failed starts, stuck faults, incorrect servo position, and ESP fault response.",
    implementationFocus: "Add feedback evidence so the ESP can detect mismatch and failure without pretending commands equal physical truth.",
    testFocus: "Inject delayed, failed, stuck-on, stuck-off, and wrong-position feedback and confirm ESP safety behavior and logged faults.",
    hazards: ["Commanded state is not measured state.", "Fault evidence must be explicit.", "Feedback faults must influence safety or recovery behavior."]
  },
  10: {
    branchIds: [3, 4, 12, 13, 14],
    output: "Recording, replay, rule versioning, endurance tests, watchdog decision, and documented limits.",
    implementationFocus: "Make experiments reproducible and regressions visible before broader platform expansion.",
    testFocus: "Replay identical sequences against changed firmware or rule versions, run endurance updates, and document unrecovered failures.",
    hazards: ["Record protocol and rule versions.", "Do not add a watchdog until runtime behavior is understood.", "Known limits must be explicit."]
  },
  11: {
    branchIds: [6, 7, 10, 11, 13, 15],
    output: "Physical migration of sensors and pump with per-sensor source selection and feedback where possible.",
    implementationFocus: "Replace virtual components one by one without rewriting decision or safety code.",
    testFocus: "Verify virtual, physical, hybrid, and disabled source modes and prove decision/safety behavior is unchanged.",
    hazards: ["Virtual mode must remain available.", "Network values do not become GPIO signals.", "Physical feedback must be truthful and named."]
  },
  12: {
    branchIds: [3, 12, 13, 16],
    output: "Platform growth only when justified: MQTT, multiple devices, persistent storage, authentication, remote access, and reusable packaging.",
    implementationFocus: "Add platform features only after the connected control loop is observable, testable, and stable.",
    testFocus: "Verify each platform addition is justified by a real workflow and does not weaken local-first operation or ESP authority.",
    hazards: ["Do not let non-critical features delay the proven control loop.", "Remote dashboards must not bypass safety.", "Persistent data must support replay, history, or customer workflow."]
  }
};

const workflowPrompts = [
  {
    id: "GLOBAL-ORIENT-001",
    title: "Project Orientation Prompt",
    category: "global",
    prompt: [
      "You are continuing AgriControl, an ESP32-C3 digital-twin and hardware-in-the-loop greenhouse control lab.",
      "Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, data/prompt-test-library.json, and the blueprint PDF before editing.",
      "Summarize the current stage, first open roadmap task, affected branches, known blockers, and the next smallest implementation slice.",
      "Do not make assumptions about hardware facts that are not recorded. Do not bypass the central control loop."
    ],
    expected_output: ["Current status summary", "Next task choice", "Affected blueprint branches and gates", "Risk and blocker list"],
    test_prompt: "Verify that the orientation summary cites repository files, chooses the earliest useful open task, and does not invent board, wiring, or firmware facts."
  },
  {
    id: "GLOBAL-IMPLEMENT-001",
    title: "Single-Slice Implementation Prompt",
    category: "global",
    prompt: [
      "Select one blueprint roadmap task or one tightly related group of tasks.",
      "Implement only the smallest coherent slice needed to move that task forward.",
      "Preserve the branch boundaries: communication moves data, sensor abstraction normalizes inputs, decision requests actions, safety creates final commands, actuator manager applies outputs, observability records events.",
      "Add tests or evidence appropriate to the risk. Update docs/PROJECT_STATE.md and data/progress-baseline.json only for statuses supported by evidence."
    ],
    expected_output: ["Source changes", "Verification evidence", "Status updates", "Next task recommendation"],
    test_prompt: "Review the diff and confirm the change is scoped to one slice, includes evidence, preserves ESP control authority, and updates durable state only when justified."
  },
  {
    id: "GLOBAL-TEST-001",
    title: "Independent Verification Prompt",
    category: "global",
    prompt: [
      "Act as a verification agent for AgriControl.",
      "Read the blueprint, current project state, progress baseline, and changed files.",
      "Create and run the most relevant tests for the touched branches and gates.",
      "Report pass/fail results, exact commands or hardware observations, uncovered risks, and whether any status may be advanced."
    ],
    expected_output: ["Test commands", "Pass/fail table", "Evidence references", "Status recommendation"],
    test_prompt: "Check that the verification covers normal behavior, boundaries, failure paths, stale data or recovery when relevant, and central-loop integrity."
  },
  {
    id: "GLOBAL-REVIEW-001",
    title: "Architecture Review Prompt",
    category: "global",
    prompt: [
      "Review the current AgriControl change for architecture violations.",
      "Prioritize bugs, safety risks, behavior regressions, missing tests, and branch-boundary leaks.",
      "Look specifically for browser or FastAPI decision authority, hardware calls from decision logic, stale-data safety gaps, untruthful actuator state labels, and missing event evidence."
    ],
    expected_output: ["Findings by severity", "File and line references", "Required fixes", "Residual risk"],
    test_prompt: "Confirm every finding is tied to a blueprint rule or acceptance gate and that no unrelated style-only feedback dominates the review."
  },
  {
    id: "GLOBAL-STATE-001",
    title: "State Update And Handoff Prompt",
    category: "global",
    prompt: [
      "After a verified change, update the durable handoff state.",
      "Write what changed, why, affected blueprint area, evidence, status updates, blockers, and next task in docs/PROJECT_STATE.md.",
      "Update data/progress-baseline.json only when a roadmap, branch, gate, or metric status has evidence.",
      "Mirror public docs and JSON into web-build/docs and web-build/data before deployment."
    ],
    expected_output: ["Updated project state", "Updated progress data when needed", "Public mirrored files", "Verification summary"],
    test_prompt: "Verify project state, baseline JSON, and public mirrored files agree with each other and contain no unsupported progress claims."
  },
  {
    id: "GLOBAL-DEPLOY-001",
    title: "Dashboard Deploy Prompt",
    category: "global",
    prompt: [
      "Deploy dashboard and public handoff files when reporting artifacts change.",
      "Validate web-build/index.html script syntax, validate JSON files, then sync web-build/ to /var/www/html/agricontrol/taskmanagement/.",
      "Verify the public dashboard, blueprint PDF, prompt library, project state, AI continuity guide, and JSON endpoints return HTTP 200.",
      "Commit and push the complete source update to GitHub."
    ],
    expected_output: ["Deployment evidence", "Verified public URLs", "Git commit hash", "Remaining issues"],
    test_prompt: "Confirm all required public URLs return HTTP 200 and the pushed GitHub commit matches local HEAD."
  }
];

const branchExtra = {
  1: {
    contracts: ["Sensors, actuators, ranges, rules, limits, safe states, and acceptance tests are written down."],
    testCases: ["Specification completeness review", "Trace every sensor and actuator to one range/state and initial implementation."],
    deliverables: ["Requirements spec", "Safe-state table", "Acceptance test list"]
  },
  2: {
    contracts: ["Produces virtual sensor values and scenario events for the FastAPI bridge.", "Displays decisions, commands, events, tests, and virtual actuator feedback."],
    testCases: ["Slider, toggle, exact input, automatic interval", "Noise, frozen value, disconnected sensor, impossible value, delay, spike"],
    deliverables: ["Simulation UI", "Scenario runner", "Virtual actuator display"]
  },
  3: {
    contracts: ["Accepts website sensor data, creates sessions and sequences, forwards to ESP, stores logs, replays sessions, and compares results."],
    testCases: ["POST sensor message", "GET status", "POST scenario", "GET events", "Connection error handling"],
    deliverables: ["FastAPI routes", "Session handling", "Replay/log storage"]
  },
  4: {
    contracts: ["Defines versioned messages, validation rules, response shape, sequence behavior, boot IDs, and rejection conditions."],
    testCases: ["Unknown field", "Missing field", "Oversized body", "Duplicate sequence", "Impossible value", "Protocol version mismatch"],
    deliverables: ["Protocol schema", "Validation rules", "Response schema"]
  },
  5: {
    contracts: ["Connects/reconnects Wi-Fi, accepts local HTTP, limits request size, parses JSON, returns structured errors, and reports communication state."],
    testCases: ["OFFLINE to CONNECTING to ONLINE", "DATA_ACTIVE", "DATA_STALE", "RECONNECTING", "Non-blocking safety loop"],
    deliverables: ["ESP communication module", "Structured rejection errors", "Communication state events"]
  },
  6: {
    contracts: ["Adapts virtual, physical, hybrid, and disabled sources into the same canonical sensor model."],
    testCases: ["Temperature range -10 to 60 C", "Moisture 0 to 100%", "Tank 0 to 100%", "Rain boolean", "Quality and age"],
    deliverables: ["Canonical sensor record", "Source mode handling", "Validation helpers"]
  },
  7: {
    contracts: ["Maintains one authoritative sensor, system, and actuator state used by decision, safety, display, and reporting."],
    testCases: ["BOOT to CONNECTING to READY", "AUTOMATIC to WARNING/SAFE/FAULT", "RECOVERY to AUTOMATIC", "Reject impossible flag combinations"],
    deliverables: ["State model", "Transition rules", "State update events"]
  },
  8: {
    contracts: ["Calculates requested actions, triggered rule IDs, human-readable reasons, and decision IDs under valid normal conditions."],
    testCases: ["Temperature <= 28 C", "28 C < temperature <= 35 C", "Temperature > 35 C", "Moisture hysteresis sequences"],
    deliverables: ["Decision engine", "Rule IDs", "Reason text", "Pure logic tests"]
  },
  9: {
    contracts: ["Applies emergency, safety, equipment protection, automatic, manual, and optimization priorities to produce final commands."],
    testCases: ["Low tank overrides pump ON", "Stale data safe state", "Controller fault critical alarm", "Emergency stop"],
    deliverables: ["Safety supervisor", "Override reasons", "Safe-state matrix tests"]
  },
  10: {
    contracts: ["Separates requested_state, commanded_state, simulated_state, measured_state, and fault_state."],
    testCases: ["Command differs from request after safety", "Simulated startup delay", "Stuck on/off", "Measured unavailable"],
    deliverables: ["Actuator state model", "Feedback handler", "Fault evidence"]
  },
  11: {
    contracts: ["Applies OLED, NeoPixel, buzzer, and servo behavior only through the actuator manager."],
    testCases: ["OLED summary pages", "Warning interruption", "NeoPixel colors", "Buzzer state-change-only tones", "Servo 10/90/170 degrees"],
    deliverables: ["Physical drivers", "Output integration", "Hardware verification notes"]
  },
  12: {
    contracts: ["Records structured events from every branch and exposes them through serial, ESP responses, FastAPI storage, and website timeline."],
    testCases: ["SENSOR_RECEIVED", "SENSOR_REJECTED", "RULE_TRIGGERED", "SAFETY_OVERRIDE", "COMMAND_CHANGED", "FAULT_DETECTED"],
    deliverables: ["Event schema", "Event storage", "Timeline rendering"]
  },
  13: {
    contracts: ["Verifies unit, boundary, sequence, integration, failure, endurance, and replay behavior from the beginning."],
    testCases: ["40 C -> window fully open", "28.0/28.1/35.0/35.1", "Bad JSON", "Timeout", "Thousands of updates"],
    deliverables: ["Test IDs", "Expected results", "Completion gates"]
  },
  14: {
    contracts: ["Records protocol and rule versions, input timing and values, decisions, overrides, commands, feedback, faults, and test results."],
    testCases: ["Replay identical sequence", "Compare old and new firmware behavior", "Regression report"],
    deliverables: ["Recorder", "Replay engine", "Comparison report"]
  },
  15: {
    contracts: ["Replaces virtual parts gradually while preserving canonical state and decision/safety code."],
    testCases: ["Real temperature replacement", "Per-sensor source selection", "Virtual mode remains available"],
    deliverables: ["Physical sensor adapter", "Source selection", "Migration tests"]
  },
  16: {
    contracts: ["Adds MQTT, multi-device, database, authentication, and SaaS packaging only when justified by stable core behavior."],
    testCases: ["Multiple devices justify MQTT", "History justifies database", "Remote users justify auth", "Customer workflow justifies SaaS"],
    deliverables: ["Platform architecture", "Security plan", "Remote dashboard constraints"]
  }
};

const testWorkflows = [
  {
    id: "TEST-WF-UNIT-001",
    title: "Pure Logic Unit Test Prompt",
    scope: "Decision, safety, state, protocol, and adapters",
    prompt: "Create host-runnable unit tests for pure logic. Cover normal rules, rejection cases, safe-state overrides, and event outputs. Tests must run without hardware.",
    required_cases: ["Temperature thresholds", "Irrigation hysteresis", "Low tank override", "Rain override", "Invalid sensor ranges", "State transition legality"]
  },
  {
    id: "TEST-WF-BOUNDARY-001",
    title: "Exact Boundary Test Prompt",
    scope: "Decision and validation thresholds",
    prompt: "Create tests at exact threshold values and just around each threshold. Include temperature 28.0, 28.1, 35.0, 35.1 C; moisture 29.9, 30.0, 40.0, 40.1%; tank 14.9, 15.0%; and invalid range edges.",
    required_cases: ["Expected command", "Triggered rule ID", "Reason text", "No floating-point ambiguity", "Previous pump state for hysteresis"]
  },
  {
    id: "TEST-WF-SEQUENCE-001",
    title: "Stateful Sequence Test Prompt",
    scope: "Hysteresis, recovery, stale data, and replay",
    prompt: "Create sequence tests where previous state matters. Include moisture 50 -> 20 -> 35 -> 45%, communication active -> stale -> recovery, and repeated browser session sequences.",
    required_cases: ["Previous actuator state", "Monotonic timestamps", "Stable valid recovery count", "Event order", "Replay repeatability"]
  },
  {
    id: "TEST-WF-INTEGRATION-001",
    title: "End-To-End Integration Test Prompt",
    scope: "Website, FastAPI, ESP, actuator manager, outputs, and feedback",
    prompt: "Test the connected path from website input through FastAPI, ESP validation, decision, safety, outputs, virtual feedback, event storage, and dashboard result.",
    required_cases: ["Versioned request", "ESP response", "Servo/OLED/LED/buzzer command", "Website display", "Event timeline", "PASS/FAIL result"]
  },
  {
    id: "TEST-WF-FAILURE-001",
    title: "Failure And Safety Test Prompt",
    scope: "Bad input, communication loss, actuator faults, and emergency handling",
    prompt: "Inject failures and confirm the system enters the correct safe state, logs the reason, and recovers only after defined valid evidence.",
    required_cases: ["Bad JSON", "Timeout", "Wi-Fi loss", "Low tank", "Failed startup", "Stuck on", "Stuck off", "Emergency stop"]
  },
  {
    id: "TEST-WF-ENDURANCE-001",
    title: "Endurance And Stability Test Prompt",
    scope: "Runtime reliability and long-duration behavior",
    prompt: "Run long-duration updates and record memory, response time, reconnection behavior, event volume, and unrecovered failures. Do not add watchdog behavior until this evidence exists.",
    required_cases: ["Hundreds of browser updates", "Thousands of ESP updates", "No blocking safety loop", "No unrecovered failure", "Known limit documentation"]
  },
  {
    id: "TEST-WF-REPLAY-001",
    title: "Recording And Replay Test Prompt",
    scope: "Regression detection",
    prompt: "Record protocol/rule versions, input timing, decisions, overrides, commands, feedback, faults, and test results, then replay against changed firmware or rule versions and produce a comparison report.",
    required_cases: ["Same input sequence", "Version comparison", "Expected versus actual commands", "Safety override comparison", "Regression summary"]
  }
];

function pad(value) {
  return String(value).padStart(2, "0");
}

function list(items) {
  return items.map((item) => `- ${item}`).join("\n");
}

function branchNames(ids) {
  return ids.map((id) => {
    const branch = baseline.branches.find((item) => item.id === id);
    return `B${id}: ${branch?.name || "Unknown"}`;
  });
}

function makeTaskPrompt(task) {
  const stage = baseline.stages.find((item) => item.id === task.stage);
  const detail = stageBlueprint[task.stage];
  const branches = branchNames(detail.branchIds);
  return {
    id: `TASK-S${pad(task.stage)}-${pad(task.id)}`,
    task_id: task.id,
    stage_id: task.stage,
    title: task.title,
    category: "roadmap-task",
    implementation_prompt: [
      `You are implementing AgriControl roadmap task ${task.id}: ${task.title}`,
      `Blueprint stage: Stage ${task.stage} - ${stage.name}.`,
      `Affected branches: ${branches.join("; ")}.`,
      "Read AGENTS.md, docs/PROJECT_STATE.md, docs/AI_CONTINUITY_SYSTEM.md, data/progress-baseline.json, and the blueprint PDF before editing.",
      `Objective: deliver the smallest durable change that advances this task and supports ${stage.intent}`,
      `Stage output target: ${detail.output}`,
      `Implementation focus: ${detail.implementationFocus}`,
      "Architecture constraints:",
      "- The ESP32 remains the control authority.",
      "- No interface, sensor, actuator, or communication method may bypass the central control loop.",
      "- Decision logic requests actions but does not call GPIO, PWM, OLED, Wi-Fi, HTTP, or browser APIs.",
      "- Safety supervisor has final authority over every command.",
      "- Separate requested_state, commanded_state, simulated_state, measured_state, and fault_state.",
      "Required deliverables:",
      "- Source, documentation, hardware note, or test artifact appropriate to this task.",
      "- Evidence showing what was verified.",
      "- Updated docs/PROJECT_STATE.md if project state changed.",
      "- Updated data/progress-baseline.json only if status advancement is supported by evidence.",
      "Stop condition: if required hardware facts are missing, record the blocker instead of guessing."
    ].join("\n"),
    test_prompt: [
      `You are testing AgriControl roadmap task ${task.id}: ${task.title}`,
      `Verify the task within Stage ${task.stage} - ${stage.name}.`,
      `Use this stage test focus: ${detail.testFocus}`,
      "Test requirements:",
      "- Confirm the change preserves the central control loop.",
      "- Confirm touched branch contracts still hold.",
      "- Include normal, boundary, negative, failure, sequence, or hardware-observation checks as relevant.",
      "- Capture exact commands, outputs, serial logs, screenshots, HTTP responses, or hardware observations as evidence.",
      "- State whether the task may be marked done, must remain active, or is blocked.",
      `Known hazards to check: ${detail.hazards.join(" ")}`
    ].join("\n")
  };
}

function makeStagePromptPack(stage) {
  const detail = stageBlueprint[stage.id];
  const stageTasks = baseline.tasks.filter((task) => task.stage === stage.id);
  return {
    id: `STAGE-${pad(stage.id)}`,
    stage_id: stage.id,
    title: stage.name,
    category: "stage",
    task_ids: stageTasks.map((task) => task.id),
    branch_ids: detail.branchIds,
    implementation_prompt: [
      `You are completing Stage ${stage.id}: ${stage.name} for AgriControl.`,
      `Stage intent: ${stage.intent}`,
      `Output target: ${detail.output}`,
      `Implementation focus: ${detail.implementationFocus}`,
      `Tasks in scope: ${stageTasks.map((task) => `${task.id}. ${task.title}`).join(" ")}`,
      "Work in roadmap order unless a blocker is documented.",
      "Keep changes narrow enough to verify in one session.",
      "Update project state and progress baseline only with evidence."
    ].join("\n"),
    test_prompt: [
      `Verify Stage ${stage.id}: ${stage.name}.`,
      `Test focus: ${detail.testFocus}`,
      "For every task marked done, provide evidence.",
      "For every branch advanced, provide contract-level verification.",
      "For every gate criterion touched, provide pass/fail output.",
      `Hazards: ${detail.hazards.join(" ")}`
    ].join("\n"),
    expected_outputs: [detail.output],
    hazards: detail.hazards
  };
}

function makeBranchPromptPack(branch) {
  const extra = branchExtra[branch.id];
  return {
    id: `BRANCH-${pad(branch.id)}`,
    branch_id: branch.id,
    title: branch.name,
    category: "branch",
    implementation_prompt: [
      `You are implementing Branch ${branch.id}: ${branch.name}.`,
      `Purpose: ${branch.purpose}`,
      "Read the blueprint branch definition and preserve its boundary.",
      "Deliver only the source, documentation, or tests that belong to this branch.",
      "Do not let this branch take over another branch responsibility.",
      `Contracts:\n${list(extra.contracts)}`,
      `Deliverables:\n${list(extra.deliverables)}`
    ].join("\n"),
    test_prompt: [
      `Verify Branch ${branch.id}: ${branch.name}.`,
      "Check that its input and output contracts are explicit and that data crosses boundaries through named structures or APIs.",
      "Check that behavior is observable through structured events when relevant.",
      `Required checks:\n${list(extra.testCases)}`
    ].join("\n"),
    contracts: extra.contracts,
    required_test_cases: extra.testCases,
    deliverables: extra.deliverables
  };
}

function makeGateTestPrompt(gate) {
  return {
    id: `GATE-${gate.id}`,
    gate_id: gate.id,
    title: gate.name,
    category: "completion-gate",
    verification_prompt: [
      `You are verifying Gate ${gate.id}: ${gate.name}.`,
      "Read the blueprint, current project state, progress baseline, and all source relevant to the gate.",
      "For each criterion, run or define a concrete test and record pass, fail, blocked, or not applicable.",
      "A criterion may be marked done only when evidence exists.",
      "Report exact commands, HTTP responses, test IDs, serial logs, screenshots, or hardware observations.",
      `Criteria:\n${list(gate.criteria.map((item) => item.title))}`
    ].join("\n"),
    criteria: gate.criteria.map((item) => item.title),
    expected_output: ["Gate result table", "Evidence per criterion", "Blockers", "Status update recommendation"]
  };
}

const taskPromptPacks = baseline.tasks.map(makeTaskPrompt);
const stagePromptPacks = baseline.stages.map(makeStagePromptPack);
const branchPromptPacks = baseline.branches.map(makeBranchPromptPack);
const gateTestPrompts = baseline.completion_gates.map(makeGateTestPrompt);

const catalog = {
  project: baseline.project,
  library: {
    title: "AgriControl Prompt And Test Library",
    version: "1.0",
    updated_at: "2026-08-04T00:00:00+09:00",
    source_blueprint: baseline.blueprint.title,
    purpose: "Provide structured prompts and test prompts for every stage, branch, roadmap task, gate, and recurring workflow required to complete AgriControl."
  },
  usage_order: [
    "Run GLOBAL-ORIENT-001 at the start of a new AI session.",
    "Choose the earliest unblocked task from data/progress-baseline.json.",
    "Use the matching TASK prompt for implementation.",
    "Use the matching TASK test prompt plus relevant TEST-WF prompts for verification.",
    "Use branch and gate prompts when a branch status or gate criterion may advance.",
    "Use GLOBAL-STATE-001 and GLOBAL-DEPLOY-001 before handoff, deployment, and GitHub push."
  ],
  global_prompts: workflowPrompts,
  stage_prompt_packs: stagePromptPacks,
  branch_prompt_packs: branchPromptPacks,
  task_prompt_packs: taskPromptPacks,
  gate_test_prompts: gateTestPrompts,
  test_workflow_prompts: testWorkflows
};

function renderMarkdown() {
  const lines = [];
  lines.push("# AgriControl Prompt And Test Library");
  lines.push("");
  lines.push("Last updated: 2026-08-04 JST");
  lines.push("");
  lines.push("This library gives future AI models a complete set of structured prompts and verification prompts for finishing AgriControl from the blueprint. It is intentionally tied to the 12 stages, 16 branches, 82 roadmap tasks, central control loop, and Gate A-E completion criteria.");
  lines.push("");
  lines.push("## How To Use");
  lines.push("");
  lines.push(list(catalog.usage_order));
  lines.push("");
  lines.push("## Universal Constraints");
  lines.push("");
  lines.push("- The ESP32 remains the control authority.");
  lines.push("- Browser and FastAPI components coordinate, simulate, display, log, replay, and verify; they do not decide actuator behavior.");
  lines.push("- Inputs must become canonical sensor state before decision logic reads them.");
  lines.push("- Decision logic requests actions; safety supervisor produces final commands.");
  lines.push("- Actuator state must distinguish requested, commanded, simulated, measured, and fault evidence.");
  lines.push("- Every meaningful branch must emit structured events.");
  lines.push("- Do not mark progress done without evidence.");
  lines.push("");
  lines.push("## Global Prompts");
  for (const item of workflowPrompts) {
    lines.push("");
    lines.push(`### ${item.id} - ${item.title}`);
    lines.push("");
    lines.push("Implementation prompt:");
    lines.push("");
    lines.push("```text");
    lines.push(item.prompt.join("\n"));
    lines.push("```");
    lines.push("");
    lines.push("Test prompt:");
    lines.push("");
    lines.push("```text");
    lines.push(item.test_prompt);
    lines.push("```");
    lines.push("");
    lines.push("Expected output:");
    lines.push("");
    lines.push(list(item.expected_output));
  }
  lines.push("");
  lines.push("## Stage Prompt Packs");
  for (const item of stagePromptPacks) {
    lines.push("");
    lines.push(`### ${item.id} - ${item.title}`);
    lines.push("");
    lines.push(`Tasks: ${item.task_ids.join(", ")}`);
    lines.push("");
    lines.push(`Branches: ${branchNames(item.branch_ids).join("; ")}`);
    lines.push("");
    lines.push("Implementation prompt:");
    lines.push("");
    lines.push("```text");
    lines.push(item.implementation_prompt);
    lines.push("```");
    lines.push("");
    lines.push("Test prompt:");
    lines.push("");
    lines.push("```text");
    lines.push(item.test_prompt);
    lines.push("```");
  }
  lines.push("");
  lines.push("## Branch Prompt Packs");
  for (const item of branchPromptPacks) {
    lines.push("");
    lines.push(`### ${item.id} - ${item.title}`);
    lines.push("");
    lines.push("Implementation prompt:");
    lines.push("");
    lines.push("```text");
    lines.push(item.implementation_prompt);
    lines.push("```");
    lines.push("");
    lines.push("Test prompt:");
    lines.push("");
    lines.push("```text");
    lines.push(item.test_prompt);
    lines.push("```");
  }
  lines.push("");
  lines.push("## Roadmap Task Prompts");
  for (const item of taskPromptPacks) {
    lines.push("");
    lines.push(`### ${item.id} - ${item.title}`);
    lines.push("");
    lines.push("Implementation prompt:");
    lines.push("");
    lines.push("```text");
    lines.push(item.implementation_prompt);
    lines.push("```");
    lines.push("");
    lines.push("Test prompt:");
    lines.push("");
    lines.push("```text");
    lines.push(item.test_prompt);
    lines.push("```");
  }
  lines.push("");
  lines.push("## Completion Gate Test Prompts");
  for (const item of gateTestPrompts) {
    lines.push("");
    lines.push(`### ${item.id} - ${item.title}`);
    lines.push("");
    lines.push("```text");
    lines.push(item.verification_prompt);
    lines.push("```");
  }
  lines.push("");
  lines.push("## Reusable Test Workflow Prompts");
  for (const item of testWorkflows) {
    lines.push("");
    lines.push(`### ${item.id} - ${item.title}`);
    lines.push("");
    lines.push(`Scope: ${item.scope}`);
    lines.push("");
    lines.push("```text");
    lines.push(item.prompt);
    lines.push("```");
    lines.push("");
    lines.push("Required cases:");
    lines.push("");
    lines.push(list(item.required_cases));
  }
  lines.push("");
  lines.push("## Machine-Readable Catalog");
  lines.push("");
  lines.push("The same library is available as `data/prompt-test-library.json` and publicly as `web-build/data/prompt-test-library.json`.");
  lines.push("");
  return `${lines.join("\n")}\n`;
}

await mkdir(new URL("../docs/", import.meta.url), { recursive: true });
await mkdir(new URL("../data/", import.meta.url), { recursive: true });
await mkdir(new URL("../web-build/docs/", import.meta.url), { recursive: true });
await mkdir(new URL("../web-build/data/", import.meta.url), { recursive: true });

const json = `${JSON.stringify(catalog, null, 2)}\n`;
const markdown = renderMarkdown();

await writeFile(docsOutputPath, markdown);
await writeFile(dataOutputPath, json);
await writeFile(publicDocsOutputPath, markdown);
await writeFile(publicDataOutputPath, json);

console.log(`Generated ${taskPromptPacks.length} task prompts, ${stagePromptPacks.length} stage packs, ${branchPromptPacks.length} branch packs, ${gateTestPrompts.length} gate prompts, and ${testWorkflows.length} test workflows.`);
