# AgriControl Project State

Last updated: 2026-08-04 JST (Stage 7 irrigation slice, backend/UI tested)

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
- `firmware/` - PlatformIO / Arduino C++ project for the physical
  ESP32-C3M-TRY board: `main.cpp`, Stage 3 output test environments, a
  drafted Stage 4 ESP runtime (`env:runtime`), a Stage 5 first vertical
  slice with the safety supervisor wired in (`env:vertical_slice`,
  temperature only), and a Stage 7 irrigation slice
  (`env:irrigation_slice`, soil/tank/rain/pump). Unverified by a build in
  this environment.
- `backend/` - FastAPI bridge (Stage 6/7, Branch 3). Actually run and
  tested here: 17 passing pytest tests plus a live end-to-end smoke test.
- `simulator/` - website simulator (Stage 6/7, Branch 2): temperature/soil/
  tank/rain controls, response display, virtual window/fan/pump, event
  log. Functionally tested with jsdom; never opened in a real browser.

## Current Progress Snapshot

Baseline progress is intentionally conservative:

- Overall progress: 40%
- Roadmap execution: 50%
- Branch readiness: 50%
- Completion gates: 0%
- Central control-loop coverage: 61%

These numbers come from the blueprint-derived model in
`data/progress-baseline.json`. Browser-local edits on the public dashboard do
not change durable project state until they are exported and committed.

## Completed Work

Date: 2026-08-04 JST (Stage 7 irrigation slice)

Agent: agent-04-firmware-runtime, agent-05-backend, agent-06-frontend-sim
(Claude Sonnet 5).

Continuing in roadmap order: Stage 7 extends the temperature-only vertical
slice to soil moisture, tank level, rain, and pump hysteresis. Same
asymmetry as every prior session: the backend/simulator side is real,
executed, tested software; the firmware side is a reviewed C++ port,
never compiled, because there is still no PlatformIO toolchain or board
access here. The underlying algorithm for the firmware side is not new,
though -- it is a direct port of `logic/decision.py` and
`logic/safety.py`'s irrigation/low-tank rules, which were already proven
correct by 35 passing host tests back in the Stage 2 session.

Changed:

- Added `firmware/include/irrigation.h`: extends `decision.h`/`safety.h`
  *without modifying them* (`vertical_slice.cpp` is untouched and still
  works exactly as before). `FullDecision`/`evaluateFullDecision` add
  soil-moisture + rain-gated pump hysteresis (roadmap tasks 49/51/52).
  `FullSafetyResult`/`evaluateFullSafety` add the `EQUIPMENT_PROTECTION`
  priority tier for low-tank pump protection (roadmap task 53). Rain
  protection (task 54) is folded into the pump-on condition itself,
  matching `logic/decision.py`.
- Added `firmware/src/irrigation_slice.cpp` (`env:irrigation_slice`,
  roadmap tasks 49-57): validates soil_moisture/water_level_percent/rain
  (each optional, physically-plausible ranges), runs the full
  decision+safety pipeline, sets a NeoPixel status color keyed to
  `alarm_level` (task 56 -- explicit color-mapping interpretation, the
  manual's spec is ambiguous), sounds a single non-blocking `tone()` on
  alarm-level changes (task 56 -- simplified from the manual's
  "confirmation/warning/critical pattern" description specifically to
  avoid blocking the HTTP handler with `delay()`), and shows soil/tank/
  pump/fan on an extended OLED page (task 57). **Pump is reported, never
  physically driven** -- same situation as the fan: no pump GPIO/relay pin
  is assigned.
- Extended `backend/app.py`'s `SensorRequest` with optional
  `soil_moisture`, `water_level_percent`, `rain`. Only fields the caller
  actually sent are forwarded -- an omitted field means "no reading
  available" (holds previous pump state on the ESP), not "assume zero".
  Added 5 new pytest tests (17 total, all passing): field omission,
  all-four-together, partial fields, rain's 0/1 restriction, and
  non-numeric rejection.
- Extended `simulator/index.html` with soil moisture / tank level sliders
  and a rain toggle, each gated by its own "send this field" checkbox, and
  added a pump indicator next to the existing fan indicator. Added 5 new
  jsdom scenarios (all passing) plus a regression re-check confirming the
  original 6 Stage 6 scenarios still pass unchanged.

Evidence:

- `python3 -m pytest backend/tests/ -v` -> 17 passed (up from 12).
- jsdom functional tests: 5 new irrigation-UI scenarios passing, plus a
  regression re-check of the original 6 Stage 6 scenarios (window-angle
  scaling, error handling) -- all still pass.
- `firmware/include/irrigation.h` cross-checked line-by-line against
  `logic/safety.py`'s low-tank branch (`tank_level_percent < 15 -> pump
  off, fan/window pass through, overrides=["LOW-TANK"] if requested_pump`)
  to confirm the C++ port is exact, not just similar. **No `pio run`
  build** -- same caveat as every firmware file so far.

Status updates:

- Roadmap tasks 49, 50, 51, 52, 53, 54, 55 marked `done` -- justified by
  the combination of (a) a proven-correct algorithm from Stage 2's host
  tests, (b) a reviewed, line-by-line-verified C++ port, (c) real tested
  bridge support, and (d) real tested simulator UI. This is the same bar
  Stage 6 was held to.
- Roadmap tasks 56, 57 marked `active` -- NeoPixel/buzzer/OLED code exists
  but is physical-output-only with no possible host-side test; kept to the
  stricter "unverified C++" standard used for Stage 3/4/5 firmware.
- No branch status changes: branches 2, 3, 6, 7, 8, 9, 10 were already
  `implemented` from prior sessions and this work doesn't newly cross a
  threshold for any of them; branch 11 (Physical outputs) stays `drafted`
  since the new NeoPixel/buzzer/OLED code is unverified.

Blockers / open questions (tracked in `data/agent-coordination.json`):

1. Pump and fan GPIO/relay pin assignment -- still the core blocker for
   any *physical* irrigation actuation, unchanged from earlier sessions.
2. Whether the NeoPixel color mapping and single-tone buzzer pattern in
   `irrigation_slice.cpp` are acceptable, or need revision.
3. Everything already open from Stage 4/5/6 (WiFi credentials, ESP IP,
   emergency-stop switch, tuning constants) still applies.

Next task: once the board and pump/fan pins are decided, build
`env:irrigation_slice` and test soil/tank/rain scenarios against real
hardware. Until then, the highest-value remaining software-only work is
Stage 8 (scenario testing) or Stage 9 (closed-loop simulation), both of
which can build on the now-tested backend/simulator the same way Stage 7
did.

Date: 2026-08-04 JST (Stage 6 FastAPI bridge + simulator, tested)

Agent: agent-05-backend, agent-06-frontend-sim (Claude Sonnet 5).

Stage 6 is pure software (Branch 2: website simulation, Branch 3: FastAPI
bridge) -- unlike every firmware session so far, this could actually be
executed and verified in this environment. `fastapi`, `httpx`, `uvicorn`,
and `pytest` were installed and used for real, not just reviewed.

Changed:

- Added `backend/app.py`: a FastAPI bridge with `POST /api/temperature`
  (roadmap task 42), `GET /api/events` (task 47), `GET /api/health`, and
  `POST /api/session/reset`. `BridgeSession` owns one `session_id` +
  sequence counter per process start, matching the blueprint's "new
  browser start creates a new session_id" protocol rule. `EventLog` is a
  bounded ring buffer, matching `firmware/include/events.h`'s approach for
  the same reason (no unbounded growth on a long-running process).
- Added `backend/tests/test_app.py`: 12 pytest tests, **all passing** --
  health check; correct protocol shape (`session_id`/`sequence`/`values`)
  forwarded to the ESP; sequence increments across calls; ESP response
  relayed unchanged; ESP-unreachable and ESP-rejects-message both return
  HTTP 502 with the failure logged; pydantic validation rejects a missing
  `temperature` field before ever reaching the ESP; event log ordering and
  `limit` query param; session reset issues a new `session_id` and resets
  the sequence counter; `EventLog`'s ring-buffer eviction verified in
  isolation; and a 200-sequential-update run (roadmap task 48's bridge-side
  half) confirming no sequence errors or dropped events under load.
- **Live end-to-end smoke test**, not just mocked: started the real bridge
  with `uvicorn`, a throwaway `http.server`-based fake ESP, and drove the
  whole path with `curl` over real sockets. Confirmed the exact
  temperature-to-command mapping from `firmware/include/decision.h`
  (20C -> fan off/window 10, 30C -> fan on/window 90, 40C -> fan on/window
  170) round-trips correctly through the bridge.
- Added `simulator/index.html` (roadmap tasks 43-46): a connection panel
  (health check + session reset), a temperature slider, a response panel,
  a CSS-animated virtual window whose rotation scales linearly with
  `window_angle` across the same 10-170 degree range as the firmware, a
  fan on/off indicator, and an event log pulling from `GET /api/events`.
  Talks to the FastAPI bridge, never directly to the ESP, per the
  blueprint's architecture.
- Functionally tested `simulator/index.html` with a jsdom harness mocking
  `fetch()` (6 scenarios, all passing): slider-to-display sync; Send
  posts the correct body and renders the response; window rotation scales
  correctly at both angle extremes; bridge-unreachable shows an error
  state without throwing; event log renders fetched items; connection
  check shows correct connected/unreachable badges.
- Advanced branch 2 (Website simulation) and branch 3 (FastAPI bridge)
  from `planned` to `implemented`; branch 12 (Observability) from
  `drafted` back to `implemented` -- this time earned by the backend event
  log's real test coverage, not the still-unverified C++ side (see the
  system-recheck session for why that distinction matters).

Evidence:

- `python3 -m pytest backend/tests/ -v` -> 12 passed.
- Live smoke test transcript (uvicorn + fake ESP + curl) showing correct
  sequencing and command mapping over real HTTP, captured in this
  session's terminal output.
- jsdom functional test of `simulator/index.html`, 6/6 scenarios passing.

Status updates:

- Roadmap tasks 41, 42, 43, 44, 45, 46, 47 marked `done`.
- Roadmap task 48 marked `active`: the bridge's own correctness under 200
  sequential updates is proven; the physical ESP's endurance under the
  same load is not, and needs the real board.
- Branches 2, 3 -> `implemented`; branch 12 -> `implemented` (corrected
  back from `drafted`, this time with real test evidence backing it).

Blockers / open questions (tracked in `data/agent-coordination.json` under
`agent-05-backend` and `agent-06-frontend-sim`):

1. The real ESP's IP address/hostname, for `AGRICONTROL_ESP_BASE_URL`.
2. Whether `simulator/index.html`'s virtual window actually looks right in
   a real browser -- jsdom only checks the computed CSS transform value,
   not visual rendering.
3. Whether `allow_origins=["*"]` in the bridge's CORS middleware needs
   tightening once this isn't purely local development.

Next task: once the ESP is reachable, point `AGRICONTROL_ESP_BASE_URL` at
it and re-run the live smoke test (or `backend/tests/`) against real
hardware -- that closes roadmap task 48 fully and gives Gate A's "Website
receives the response" criterion its first real evidence.


The previous session's handoff flagged a real problem and left it as an
open question rather than fixing it: `vertical_slice.cpp` applied the
decision engine's output straight to the servo, with no safety override
layer. The owner confirmed this should be fixed, so it was fixed this
session, not just re-flagged.

Changed:

- Added `firmware/include/safety.h`: a firmware port of `logic/safety.py`
  (Stage 2 roadmap task 12), restricted to the fan/window outputs the
  temperature-only slice actually has (no pump exists yet -- that's Stage
  7). Same priority order (Emergency > Safety > Equipment protection >
  Automatic) and safe-state matrix as the Python version, including the
  same "safe angle defaults to closed" and "configured safe fan state
  defaults to off" documented assumptions.
- Rewired `firmware/src/vertical_slice.cpp`: every `POST /sensor` message
  now computes the decision, runs it through `evaluateSafety()`, and only
  ever applies the **safety supervisor's** commanded value to the servo --
  never the raw decision. The OLED display and JSON response
  (`commands`, `mode`, `alarm_level`) were updated to reflect the same
  post-safety values, so what's displayed always matches what's actually
  commanded.
- `isStartup` is computed for real (true until the first message is ever
  accepted) and `dataStale` is computed for real (from
  `SharedState::tick()`'s existing staleness detection) -- both feed
  `evaluateSafety()`.
- `emergencyStopActive` and `controllerFaultActive` remain hardcoded
  `false`. This is now honestly narrower than before: the safety
  supervisor itself is real and wired in; what's still missing is two of
  its *input signals*, because no physical emergency-stop switch has been
  assigned and no controller-health-check exists yet. Named as constants
  (`kEmergencyStopActive`, `kControllerFaultActive`) specifically so wiring
  them for real later is a one-line change, not a rewrite.

Evidence:

- `firmware/include/safety.h` and the updated `vertical_slice.cpp`
  reviewed for syntax/structure (brace/paren balance checked
  programmatically) and cross-checked line-by-line against
  `logic/safety.py`'s priority order and safe-state matrix. **Still no
  `pio run` build** -- no PlatformIO toolchain, WiFi network, or physical
  board access in this environment. This is a reviewed draft, not verified
  working code, same caveat as every other firmware file so far.

Status updates: none -- this improves code quality within roadmap tasks
34/35 (already `active`), it doesn't complete a new numbered task. No
branch status changes either, per the recheck session's standard for
unverified/never-compiled C++.

Next task: same as before, now with one more thing to decide -- build
`env:vertical_slice`, add WiFi credentials, test with `curl`, AND decide
whether a spare tact switch (SW1/SW2/SW3) should become the real
emergency-stop input.

Date: 2026-08-04 JST (Stage 5 first vertical slice drafted)

Agent: agent-04-firmware-runtime (Claude Sonnet 5).

Continuing in roadmap order: Stage 4 (tasks 24-30) is drafted, and Stage 5's
first vertical slice (tasks 31/33-37) is temperature-only code that, like
Stage 4, does not require hardware access to write -- only to verify.

Changed:

- Added `firmware/include/decision.h` (roadmap task 34): temperature-only
  decision rules in C++, matching `logic/decision.py`'s thresholds exactly
  (`<=28C` fan off/window closed, `28-35C` fan on/window half, `>35C` fan
  on/window fully open).
- Added `firmware/src/vertical_slice.cpp` (`env:vertical_slice`, roadmap
  tasks 31/33/34/35/36/37): validates a temperature-only `POST /sensor`
  message (rejects anything outside a placeholder -40C to 85C range, and
  rejects any `values` key other than `temperature` -- soil/tank/rain are
  Stage 7), computes the decision, writes the servo (`ESP32Servo` on CN3),
  displays the temperature/fan/window/rule on the OLED (`U8g2`), and
  returns a full JSON response with `commands`, `triggered_rules`, and
  `reasons`.
- **Explicitly flagged, not fixed:** `vertical_slice.cpp` applies the
  decision engine's output directly with no safety supervisor. Stated in
  the file's header comment and in `firmware/README.md`'s open questions --
  `logic/safety.py` has not been ported to firmware, so nothing here
  enforces low-tank pump protection, emergency stop, or a fault/stale-data
  safe servo position. Not safe to run unattended.
- Added `[env:vertical_slice]` to `firmware/platformio.ini`.

Evidence:

- `firmware/include/decision.h` and `firmware/src/vertical_slice.cpp`
  reviewed for syntax/structure and Arduino/ArduinoJson/U8g2/ESP32Servo API
  usage from memory. **No `pio run` build was performed** -- same caveat as
  Stage 4: no PlatformIO toolchain, WiFi network, or physical board access
  in this environment. Treat as a reviewed draft.

Status updates:

- Roadmap tasks 31, 33, 34, 35, 36, 37 marked `active` (drafted,
  unverified).
- Roadmap task 32 ("Send temperature with curl") and tasks 38-40 (repeated
  messages, invalid values, timeout/recovery) remain `todo` -- they are
  test-execution tasks that need the real board and network, not something
  that can be drafted in advance.
- No branch status changes: per the system-recheck session's standard,
  unverified/never-compiled C++ stays below the "implemented" bar already
  earned by the host-tested Python in `logic/`.

Next task: build/upload `env:vertical_slice`, add real WiFi credentials,
and send a test `POST /sensor` with `curl` (roadmap task 32) -- confirm the
response JSON, the OLED contents, and that the servo actually moves to the
expected angle. Then decide whether to port `logic/safety.py` to firmware
before continuing further into Stage 5/7.

Date: 2026-08-04 JST (dashboard staleness bug fixed)

Agent: agent-01-coordinator (Claude Sonnet 5).

Root-caused and fixed the exact bug behind an owner-reported discrepancy:
the live dashboard showed materially different numbers (22% overall,
12/82 tasks, "1 implemented, 9 drafted" branches) than the deployed
`data/progress-baseline.json` (29% overall, 18/82, "5 implemented, 5
drafted"). Diffing the deployed file against the repo and against the
dashboard's own live-computed math showed both matched each other and the
repo exactly -- the discrepancy could only be explained by the dashboard's
`localStorage` overlay (`agricontrol-taskmanagement-v1`) silently taking
priority over the baseline, per `loadState()`'s existing
`{...baseline.tasks, ...stored.tasks}` merge. Nothing in the numbers the
owner saw corresponded to any baseline snapshot this repo ever had, which
means it was local browser state (likely from manual UI edits at some
earlier point), not a stale deploy.

Changed:

- Added `BASELINE_VERSION` (a timestamp, kept identical to
  `data/progress-baseline.json`'s `updated_at`) to `web-build/index.html`,
  stamped into `baseline.version` and into everything `saveState()` writes.
- Rewrote `loadState()`: local edits are only merged in when
  `stored.version === BASELINE_VERSION`. On a mismatch (including saves
  from before this fix existed, which have no `version` field at all), the
  stale blob is moved to a separate `:stale` localStorage key -- not lost,
  not silently applied -- and the page falls back to the current baseline.
- Added a visible banner (`#staleEditsBanner`) that appears whenever stale
  edits were found, explaining what happened, with two buttons:
  "Restore my saved view anyway" (applies the stashed edits on purpose,
  now an explicit choice instead of a silent default) and "Discard saved
  view".
- Fixed a second, smaller bug found while touching this code: the
  "Updated \<badge\>" in the header showed `new Date()` (page render time,
  which is always "now" and therefore meaningless as a freshness signal),
  not when the underlying data was actually last updated. It now shows
  `BASELINE_VERSION` formatted, with a tooltip noting when stale edits are
  stashed.
- Updated `docs/AI_CONTINUITY_SYSTEM.md`'s Public Reporting Checklist and
  `AGENTS.md`'s Validation Baseline: `BASELINE_VERSION` must be bumped to
  match `data/progress-baseline.json`'s `updated_at` every time tasks,
  branches, or gates change, and `data/progress-baseline.json`'s
  `updated_at` (which had silently stayed at the initial commit's
  timestamp through every prior session's edits) must be bumped too.

Evidence:

- Wrote a jsdom-based functional test (not just `node --check` syntax
  validation) covering 5 scenarios: fresh load with no saved state; a
  version-mismatched saved state (confirms the banner shows, the stale
  values are NOT applied, and the stale blob is preserved separately);
  clicking "Restore" (confirms the stashed edits then do get applied,
  intentionally); clicking "Discard" (confirms the stash is cleared); and a
  version-matched saved state (confirms same-version local edits still
  merge normally -- the existing editing feature isn't broken by this fix).
  All 5 passed after one round of fixes.
- The first draft of this fix had a real bug the functional test caught
  that `node --check` did not: `STALE_STORAGE_KEY` was declared with
  `const` textually after the point where `loadState()` first runs at
  script top-level, producing a temporal-dead-zone `ReferenceError` on
  every page load. Fixed by moving the declaration next to `STORAGE_KEY`,
  before `let state = loadState();` executes.

Status updates: none (this is a client-side dashboard bug fix, not a
roadmap task).

Next task: none required, but a good habit check -- before trusting
dashboard numbers again after a browser has had the page open across
multiple deploys, do a hard reload and check the "Data as of" badge in the
header against `data/progress-baseline.json`'s `updated_at`.

Date: 2026-08-04 JST (system recheck)

Agent: agent-01-coordinator (Claude Sonnet 5).

A full audit of every `done` status, every mirrored file, and the live
deployment, in response to an explicit "recheck" request. Findings:

Verified still correct (no changes needed):

- `python3 -m unittest discover -s tests -v` still passes 35/35 -- Stage 2
  logic is unaffected by later firmware work.
- `docs/`, `data/`, and `README.md` all match their `web-build/` mirrors
  byte-for-byte (`diff` clean on every file).
- The live deployment (`data/progress-baseline.json` fetched from
  `https://phyowaisoe.com/agricontrol/taskmanagement/`) matches the repo
  exactly -- no stale deploy.
- Roadmap task 4 ("Verify OLED, NeoPixel, buzzer, and servo wiring")
  re-read: its evidence is explicitly sourced from the manufacturer's
  manual, not an on-device test, and is kept distinct from Stage 3 tasks
  17-20 (the actual hands-on tests). Wording was already accurate; no
  change needed.

Corrected:

- Branch 12 (Observability) was marked `implemented`, resting entirely on
  `firmware/include/events.h`'s `EventLog` -- C++ that has never been
  compiled. That's a materially weaker evidence bar than branches 6-10,
  which are also `implemented` but backed by 35 passing host-run tests.
  Downgraded branch 12 back to `drafted` to keep the "implemented" label
  meaning the same thing everywhere on the dashboard.
- Documented a real limitation found while re-reading
  `firmware/src/runtime.cpp`: the `kMaxRequestBodyBytes` check runs *after*
  `WebServer.h` has already buffered the full request body into RAM, not
  before. It stops oversized bodies from being processed, but doesn't by
  itself prevent the memory allocation. Added a comment explaining this and
  what true pre-buffer protection would require (a streaming/upload
  handler, or ESPAsyncWebServer). No status changed because of this --
  roadmap task 30 was already `active`, not `done`.

Status updates:

- Branch 12: `implemented` -> `drafted`.
- `overall_percent` unchanged (29%); `branch_percent` 41% -> 39%;
  `control_loop_percent` 48% -> 47%; `roadmap_percent` unchanged (28%).

Nothing that was marked `done` turned out to be wrong. The one correction
(branch 12) was a status that was too generous, not a broken claim -- the
`EventLog` code itself wasn't touched.

Date: 2026-08-04 JST (Stage 4 ESP runtime drafted)

Agent: agent-04-firmware-runtime (Claude Sonnet 5).

This session drafts the Stage 4 ESP runtime entirely without hardware
access -- it's infrastructure code (async loop, shared state, events,
stale-data detection, recovery, HTTP server, request-size/validation
limits), not something that requires the physical board to write. It does
require the board (and real WiFi credentials) to verify.

Changed:

- Added `firmware/include/canonical.h`: `SensorId`, `SensorReading`,
  `SensorState`, mirroring `logic/canonical.py`'s model in C++ (roadmap
  task 25, Branch 6/7).
- Added `firmware/include/system_state.h`: `Mode`/`CommunicationState`
  enums with the exact same transition graph as `logic/system_state.py`
  (roadmap task 24), plus `RecoveryTracker` implementing the blueprint's
  recovery chain -- Failure -> Safe state -> consecutive valid messages ->
  stable communication -> clear fault -> resume automatic (roadmap task 28).
  `kDataStaleTimeoutMs` (10s) and `kRecoveryConsecutiveValidRequired` (5)
  are explicit tunable constants, not guessed hardware facts -- flagged for
  owner confirmation.
- Added `firmware/include/events.h`: fixed-capacity (32-entry) ring-buffer
  event log, no dynamic growth (roadmap task 26, Branch 12).
- Added `firmware/include/shared_state.h`: bundles sensors/system/
  recovery/events into one `SharedState` with a non-blocking `tick()` that
  detects staleness and drives WARNING -> RECOVERY -> AUTOMATIC transitions
  (roadmap task 27).
- Added `firmware/src/runtime.cpp` (`env:runtime`): connects WiFi, runs a
  `WebServer` on port 80 with `POST /sensor`, enforces a request-size cap
  (`kMaxRequestBodyBytes = 2048`, roadmap task 30), rejects malformed JSON,
  rejects duplicate/out-of-order `sequence` values, and rejects messages
  naming an unrecognized sensor field. Explicitly does **not** call a
  decision engine or drive any actuator, and does not do per-sensor
  range/type validation -- both are Stage 5 (roadmap task 33), out of
  scope here.
- Added `firmware/include/secrets.h.example` (WiFi credential template) and
  gitignored `firmware/include/secrets.h` so real credentials are never
  committed.
- Added `[env:runtime]` to `firmware/platformio.ini` and declared the
  `ArduinoJson` dependency.
- Advanced branch 5 (ESP communication) `planned` -> `drafted` and branch
  12 (Observability) `drafted` -> `implemented`.

Evidence:

- `firmware/include/*.h` and `firmware/src/runtime.cpp` reviewed for
  syntax/structure and API usage against the Arduino-ESP32 core, `WebServer`,
  and ArduinoJson v7 APIs from memory. **No `pio run` build was performed**
  -- there is no PlatformIO toolchain, WiFi network, or physical board
  access in this environment. Treat this as a reviewed draft, not verified
  working code; normal to need small fixes once actually compiled.

Status updates:

- Roadmap tasks 24-30 marked `active` (drafted, unverified).
- Branch 5 -> `drafted`; branch 12 -> `implemented`.

Blockers (owner input needed, tracked in `data/agent-coordination.json`
under `agent-04-firmware-runtime`):

1. Real WiFi SSID/password for `firmware/include/secrets.h`.
2. Build/upload `env:runtime` and send a test `POST /sensor` (e.g. via
   `curl`); report the response and serial log as evidence.
3. Confirm or adjust the placeholder tuning constants: 10s stale-data
   timeout, 5-message recovery threshold, 2048-byte max request body.

Next task: get `env:runtime` actually building (fix whatever compile errors
turn up -- expected, since this was never compiled), then flash and test
against the real board and WiFi network.

Date: 2026-08-04 JST (firmware toolchain decision + servo power confirmed)

Agent: agent-02-hardware (Claude Sonnet 5).

Owner-provided evidence and decisions this session:

- The board on serial port `/dev/cu.usbmodem1101` is the same physical
  ESP32-C3M-TRY used for AgriControl, currently running an Arduino/PlatformIO
  test sketch rather than MicroPython.
- Decision: AgriControl's firmware layer (Stage 3+) is built with
  **PlatformIO, Arduino framework, C++**, not MicroPython. This supersedes
  the blueprint's roadmap task 2 wording ("Record the MicroPython version"),
  which is now interpreted as "record the firmware toolchain and version."
  `data/progress-baseline.json` task 2's title was updated to match, and
  `tools/generate-prompt-test-library.mjs` / `docs/USER_GUIDE.md` /
  `docs/AI_CONTINUITY_SYSTEM.md` were updated so no durable doc still implies
  MicroPython is the plan.
- Servo power stability (roadmap task 23): confirmed by direct observation
  on the live board while a servo was cycled repeatedly through motion (a
  sweep into a rapid back-and-forth pattern between roughly 0 deg and 58
  deg) -- the ESP did not reset. This test used the board's existing
  Arduino/PlatformIO sketch, not the newly-added `firmware/src/test_servo.cpp`
  below, which has not itself been flashed yet.

Changed:

- Deleted the prior session's MicroPython scripts (`firmware/boot.py`,
  `test_oled.py`, `test_neopixel.py`, `test_buzzer.py`, `test_servo.py`) --
  superseded by the toolchain decision above, and left in place they would
  have misled a future agent into thinking MicroPython was still the plan.
- Added a PlatformIO project in `firmware/`: `platformio.ini` (one
  environment per test file via `build_src_filter`, board
  `esp32-c3-devkitm-1` as the closest chip-accurate match for the
  ESP32-C3-MINI-1 module), `include/pins.h` (shared pin constants from the
  manual's Table 5.2), `src/main.cpp` (LED-blink bring-up placeholder), and
  `src/test_oled.cpp` / `test_neopixel.cpp` / `test_buzzer.cpp` /
  `test_servo.cpp` for roadmap tasks 17-20. None of this has been built with
  `pio run` in this environment -- there is no PlatformIO toolchain or board
  access here, so it is unverified beyond visual review.
- Updated `data/progress-baseline.json`, `data/agent-coordination.json`,
  `docs/USER_GUIDE.md`, `docs/AI_CONTINUITY_SYSTEM.md`,
  `tools/generate-prompt-test-library.mjs`, and README/AGENTS files to
  remove MicroPython-specific wording and reflect the PlatformIO decision;
  regenerated `docs/PROMPT_TEST_LIBRARY.md` and
  `data/prompt-test-library.json`.
- Added `firmware/src/test_all_outputs.cpp` (`env:test_all_outputs`) for
  roadmap task 21: combines OLED, NeoPixel, and buzzer on one build to check
  for shared-bus/power interference. Deliberately excludes the servo, since
  the hardware-verified servo power test did not include the other outputs
  running at the same time. Meant to run only after tasks 17-19 have their
  own individual hardware evidence.

Evidence (this session):

- Direct observation of the physical board while the servo cycled
  repeatedly (owner-reported, not reproducible from this environment).
- `firmware/*.cpp` and `platformio.ini` reviewed for syntax/structure only;
  no `pio run` build was performed here.

Status updates (this session):

- Roadmap task 2 marked `done` (title changed to "Record the firmware
  toolchain and version"; toolchain is confirmed as PlatformIO/Arduino C++).
- Roadmap tasks 20 and 23 marked `done` (servo motion observed; ESP did not
  reset).
- Roadmap tasks 17-19 remain `active` (still unverified on hardware).
- Roadmap task 21 marked `active`: combined-output test source drafted,
  unverified on hardware, and gated behind 17-19 individually passing first.
- `known_unknowns` updated: MicroPython version and generic servo-power
  unknowns removed; exact RC servo model, pump/fan pin assignment, and
  exact PlatformIO/Arduino-ESP32 core versions remain open.

Blockers (owner input still needed, tracked in `data/agent-coordination.json`
under `agent-02-hardware`):

1. Which RC servo model is attached to CN3? (Power stability is resolved;
   the model itself is not.)
2. Which spare GPIO/relay will drive the greenhouse pump and fan? This eval
   board has no built-in pump or fan output.
3. Exact `platform-espressif32` / Arduino-ESP32 core versions in use, to pin
   in `firmware/platformio.ini` for reproducible builds.

Next task: build/upload `firmware/` test environments
(`pio run -e test_oled|test_neopixel|test_buzzer -t upload`) on the physical
board and report the results, then `env:test_all_outputs` (task 21); answer
the three blockers above before advancing Stage 3 further (task 22).

Older changes (previous session: Stage 1 hardware facts + Stage 3 firmware
drafts, superseded above where noted -- the firmware was MicroPython at the
time and has since been rewritten in PlatformIO/Arduino C++):

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

Source of hardware facts (previous session):

- `ESP32-C3M-TRY-R1-20230701.pdf` ("ESP32-C3M-TRY 取扱説明書"), MicroFan,
  2023-07-01, provided directly by the project owner.

Evidence (previous session):

- Manual sections 1.1, 2.1-2.8, and 5.1-5.3 (board overview, peripheral
  descriptions, schematic, and pin table) cited directly for the board
  identity and pin map above.
- The MicroPython scripts referenced here were syntax-checked and later
  deleted; see "Changed" above for the PlatformIO/C++ replacements.

Status updates (previous session, superseded above):

- Roadmap tasks 1, 3, 4 marked `done` (still current).
- Branch 10 corrected to `implemented`; branch 11 advanced to `drafted`
  (still current).

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

- Exact RC servo model at CN3 (power source stability is confirmed; the
  model itself is not recorded).
- Pump and fan GPIO/relay pin assignment (not built into the ESP32-C3M-TRY
  eval board; this is new wiring specific to the AgriControl greenhouse
  build, not something the board's manual answers).
- Exact `platform-espressif32` and Arduino-ESP32 core versions in use, to
  pin in `firmware/platformio.ini` for reproducible builds.
- Real WiFi credentials for `firmware/include/secrets.h`.
- Whether the placeholder runtime tuning constants (10s stale-data timeout,
  5-message recovery threshold, 2048-byte max request body, -40C to 85C
  temperature validation range) are acceptable.
- Whether a spare tact switch (SW1/SW2/SW3) should be wired as a physical
  emergency-stop input for `kEmergencyStopActive` in
  `firmware/src/vertical_slice.cpp` -- currently hardcoded `false`.
- The real ESP's IP address/hostname once reachable, for
  `AGRICONTROL_ESP_BASE_URL` (`backend/app.py`).
- Whether `simulator/index.html`'s virtual window actually looks right in a
  real browser (only jsdom-verified so far).
- Whether `backend/app.py`'s CORS `allow_origins=["*"]` needs tightening.
- Whether `firmware/src/irrigation_slice.cpp`'s NeoPixel color mapping and
  single-tone buzzer pattern (both explicit interpretations of the
  manual's ambiguous spec) are acceptable.

Resolved: exact board, complete pin map, OLED/NeoPixel/buzzer wiring
(sourced from the owner-provided `ESP32-C3M-TRY-R1-20230701.pdf`); firmware
toolchain (PlatformIO, Arduino framework, C++ -- not MicroPython); servo
power stability (roadmap task 23); the safety supervisor is now ported to
firmware and wired into `vertical_slice.cpp`/`irrigation_slice.cpp` (its
emergency-stop and controller-fault *inputs* remain open, tracked
separately above). The FastAPI bridge and website simulator (Stage 6/7)
are built and genuinely tested (17 passing pytest tests, a live end-to-end
smoke test, and 11 passing jsdom scenarios) -- the only gap is the real
ESP. See Completed Work above.

## Next Work

Stage 2 (Pure logic, tasks 9-16) is done: `logic/` implements canonical
sensor state, system/actuator state, the stateful decision engine, and the
safety supervisor, verified by 35 passing host-runnable tests in `tests/`.

Stage 1 (tasks 1-4) is fully done. Stage 3 (Local physical outputs): servo
tasks (20, 23) are done from direct hardware observation; OLED/NeoPixel/
buzzer/combined-output test environments are drafted in `firmware/`
(PlatformIO) but unverified by a build or hardware run. Stage 4 (ESP
runtime, tasks 24-30), Stage 5's first vertical slice (tasks 31/33-37), and
most of Stage 7 (tasks 49-55) are drafted in `firmware/src/runtime.cpp`,
`vertical_slice.cpp`, `irrigation_slice.cpp`, and `include/`, unverified by
a build -- except that tasks 49-55 also have real backend/simulator
evidence, unlike 24-40. Stage 6 (tasks 41-47) is done and genuinely tested
(`backend/`, `simulator/`) -- software-only, doesn't need the physical
board to build or run, only to reach the real ESP for the last mile.

Follow the blueprint order. The next open tasks are:

1. Build and upload `firmware/`'s `test_oled`, `test_neopixel`, and
   `test_buzzer` PlatformIO environments on the physical board and record
   the results as evidence (roadmap tasks 17-19, `active`).
2. Build and upload `env:test_all_outputs` (roadmap task 21, `active`,
   drafted) once 17-19 have hardware evidence.
3. Connect hardcoded decisions to outputs (roadmap task 22) - needs the
   owner to first answer the pump/fan pin question in
   `data/agent-coordination.json` (`agent-02-hardware`), since this board has
   no built-in pump/fan output.
4. Get `env:runtime` and `env:vertical_slice` actually building (roadmap
   tasks 24-30 and 31/33-37, `active`, drafted): fix whatever compile
   errors turn up, add real WiFi credentials to
   `firmware/include/secrets.h`, and test `POST /sensor` against
   `vertical_slice` with `curl` (roadmap task 32) -- confirm the response
   JSON, OLED contents, and servo motion match the safety-supervised
   values, not just the raw decision.
5. Decide whether a spare tact switch (SW1/SW2/SW3) should become the real
   `kEmergencyStopActive` input in `firmware/src/vertical_slice.cpp` (the
   safety supervisor itself is now wired in; this is its one remaining
   unconnected input worth deciding on soon).
6. Once the ESP is reachable, set `AGRICONTROL_ESP_BASE_URL` and re-run
   `backend/tests/`'s live smoke test against the real board -- closes
   roadmap task 48 fully and opens `simulator/index.html` in a real browser
   (roadmap tasks 43-46 are jsdom-verified only so far).
7. Get `env:irrigation_slice` building alongside `env:vertical_slice`
   (roadmap tasks 49-57) once the toolchain/WiFi/pin questions are
   answered; confirm the NeoPixel color mapping and buzzer pattern.
8. Consider Stage 8 (scenario testing) or Stage 9 (closed-loop simulation)
   as the next software-only work -- both can build on the now-tested
   `backend/`/`simulator/` the same way Stage 7 did, without waiting on
   hardware.

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
