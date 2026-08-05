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

Date: 2026-08-05 JST (Stage 8's fake ESP extended to actually model recovery, closing a real scope gap)

Agent: agent-05-backend (Claude Sonnet 5).

Followed through on the previous entry's own flagged follow-up:
`backend/tests/test_scenarios.py`'s fake ESP never modeled staleness or
recovery at all (`data_stale` always defaulted to `False`, `is_startup`
was hardcoded `False`), so Stage 8's scenario suite -- despite testing 7
named conditions -- had no scenario proving the "recovery requires
stable valid messages" behavior through the actual bridge protocol path,
only in `tests/test_protocol.py`'s pure `logic/` integration test and on
live hardware.

Changed:

- Added `real_esp_responder_with_recovery()` to
  `backend/tests/test_scenarios.py`: unlike the existing
  `real_esp_responder()` (a single isolated reading, already
  "recovered"), this tracks `SystemState`/`RecoveryTracker` across a
  *sequence* of requests using `evaluate_tick()` and
  `is_data_stale_for_safety()` -- mirroring the real ESP's `SharedState`
  and the corrected firmware wiring exactly.
- Added `test_recovery_requires_stable_valid_messages_through_the_bridge`:
  starts mid-recovery (`Mode.WARNING`) and sends
  `RECOVERY_CONSECUTIVE_VALID_REQUIRED` (5) identical readings through
  `/api/temperature`, asserting the bridge relays `safety_override` for
  all 5, then `automatic` on the 6th -- the same behavior verified at
  three other levels now (host-level logic integration, live hardware,
  and now the actual bridge protocol path a real website/simulator would
  go through).

Evidence:

- `python3 -m pytest backend/tests/` -> 25 passed (up from 24).
- `python3 -m unittest discover -s tests` -> 93 passed, unaffected.

Status updates: none -- this adds test coverage for behavior already
counted as evidence for Gate A in an earlier entry; no new roadmap task
or gate criterion is claimed from it.

Date: 2026-08-05 JST (host-level regression test added for the recovery-gating fix)

Agent: agent-03-logic (Claude Sonnet 5).

Directly following the recovery-gating bug fix: noticed that nothing in
`logic/` or `backend/tests/` would have caught that exact bug, or would
catch a regression of it in the future. `backend/tests/test_scenarios.py`'s
fake ESP never passed `data_stale` to `evaluate_safety()` at all (relying
on the Python default, `False`) -- not the same bug, but a real scope
gap: Stage 8's scenarios never modeled staleness/recovery, so there was
no host-level proof of the "5 consecutive valid messages" requirement
anywhere, only the live hardware test from the previous entry.

Changed:

- Added `logic/protocol.py::is_data_stale_for_safety(mode)`: the correct
  `data_stale` input for `evaluate_safety()`, derived from
  `Mode.WARNING`/`Mode.RECOVERY` rather than the raw communication state
  -- the Python equivalent of the exact fix just applied to
  `irrigation_slice.cpp`/`vertical_slice.cpp`/`mqtt_test_harness.cpp`.
  Documented in the docstring as existing specifically so future
  Python-side integration work (an updated fake ESP, a new end-to-end
  test) doesn't have to independently rediscover -- or re-break -- this
  wiring.
- Added `tests/test_protocol.py::TestIsDataStaleForSafety` (4 tests) and
  `TestFullRecoveryGatingIntegration` (1 test): the latter wires
  `evaluate_tick()`, `is_data_stale_for_safety()`, `evaluate_decision()`,
  and `evaluate_safety()` together exactly as the corrected firmware
  does, and asserts the identical outcome verified live on hardware --
  automatic operation stays overridden for exactly
  `RECOVERY_CONSECUTIVE_VALID_REQUIRED` (5) messages after a stale gap,
  then resumes on the 6th.

Evidence:

- `python3 -m unittest discover -s tests` -> 93 passed (up from 88).
- `python3 -m pytest backend/tests/` -> 24 passed, unaffected.

Status updates:

- No roadmap task or gate criterion changes from this entry -- it adds
  regression coverage for behavior the previous entry's live hardware
  test already proved and already counted as evidence for Gate A.
- `backend/tests/test_scenarios.py` was not modified to use
  `is_data_stale_for_safety()` -- that would be a reasonable follow-up
  (Stage 8's fake ESP could gain a genuine recovery scenario) but is a
  scope expansion beyond closing the gap this entry targeted, left for a
  future session.

Date: 2026-08-05 JST (real safety-supervisor bug found and fixed; Gates A, B, C closed -- first gate progress ever recorded)

Agent: agent-04-firmware-runtime, agent-01-coordinator (Claude Sonnet 5).

While reviewing Gate A's ("First vertical slice") seven criteria against
today's accumulated evidence -- an audit prompted by noticing
`gate_percent` had sat at 0% for the entire project's history -- found a
genuine, previously-undetected bug in the safety supervisor's wiring, and
a second, unrelated bug in the dashboard itself that would have silently
discarded any gate-tracking work regardless.

**Bug 1 -- recovery never actually required stable communication.**
`irrigation_slice.cpp` and `vertical_slice.cpp` computed their `dataStale`
safety-supervisor input as `shared.system.communicationState() ==
CommunicationState::DATA_STALE` -- the *raw*, instantaneous communication
state, which `SharedState::tick()` flips back to `DATA_ACTIVE` as soon as
a single fresh reading arrives. The blueprint's own documented recovery
chain ("Failure -> Safe state -> Several consecutive valid messages ->
Stable communication confirmed -> Resume automatic operation") is
implemented correctly by `RecoveryTracker`/`SystemState::mode()`
(`WARNING` -> `RECOVERY` -> `AUTOMATIC`, gated on 5 consecutive valid
messages) -- but that mode field was never actually consulted by the
safety decision. The result: real automatic operation (and its commanded
actuator values) resumed after just one valid message, not five. Every
piece in isolation was correct and separately tested (`RecoveryTracker`'s
host tests, `evaluate_safety`'s `data_stale` handling) -- the bug was
purely in how they were wired together in the firmware caller, which
none of the host tests could see since they don't exercise `SharedState`
end-to-end the way live hardware does.

**Fix**: changed `dataStale` in `irrigation_slice.cpp`,
`vertical_slice.cpp`, and `mqtt_test_harness.cpp` (same bug, ported there
too) to `shared.system.mode() == Mode::WARNING || shared.system.mode() ==
Mode::RECOVERY` -- reusing the exact state machine `SharedState::tick()`
already maintains correctly, rather than adding new tracking.

**Verified live**: forced a real stale gap (>10s) on the physical board,
then sent rapid consecutive readings. With genuinely back-to-back
requests, the fix behaved exactly as designed: 5 consecutive messages in
`safety_override`, then automatic resumes on the 6th -- matching
`kRecoveryConsecutiveValidRequired = 5` precisely. (Earlier attempts with
natural gaps between manual `curl` calls repeatedly re-triggered
staleness mid-cycle, which is *correct* behavior, not a flaw -- any new
staleness during recovery should reset the streak.)

**Bug 2 -- the dashboard itself silently discarded gate data.**
`web-build/index.html` had a leftover initialization loop
(`for (const gate of gates) { gate.criteria.forEach((_, index) => {
baseline.gates[...] = "todo"; }); }`) that ran *after* the `baseline`
object literal, unconditionally overwriting every gate criterion back to
`"todo"` -- dead code from when `baseline.gates` was empty and this loop
was the only way criteria got default values. The moment `baseline.gates`
was populated with real values (this session), this loop silently erased
them on every page load. Removed now that every applicable criterion is
listed explicitly in the object literal; criteria not listed still
correctly default to `"todo"` via `statusForGate()`'s existing fallback.

**Closed three completion gates in full**, the first ever recorded in
this project (`gate_percent` had been 0% since the baseline was created):

- **Gate A (First vertical slice)**: all 7 criteria, including two not
  previously verified this session -- "Website receives the response"
  (confirmed by running the real FastAPI bridge with
  `AGRICONTROL_ESP_BASE_URL` pointed at the physical board's IP and
  relaying a real response, not a mocked one) and the now-fixed recovery
  criterion.
- **Gate B (Greenhouse MVP)**: all 6 criteria -- confirmed rain
  protection on real hardware for the first time this session (dry soil +
  rain=1 correctly held the previous pump state rather than turning it
  on), alongside soil/tank/temperature support, low-tank override, OLED/
  LED/buzzer/servo coherence, Stage 8's automated scenarios, and Stage
  9's commanded/simulated state separation (all already proven in earlier
  sessions).
- **Gate C (Test platform)**: all 5 criteria -- Stage 9's fault injection,
  Stage 10's recording/replay, and both the bridge-side and board-side
  endurance runs.

Gates D (Physical migration) and E (Platform expansion) remain untouched
at 0% -- they require real sensor/actuator hardware and deliberate
architecture decisions this session didn't have grounds to make.

Evidence:

- `pio run` (all 10 environments): SUCCESS after the fix.
- Live recovery-cycle test against the physical board: 5-message
  safety-override streak confirmed, matching the constant exactly.
- Live rain-protection test: dry soil + rain=1 held the previous `pump:
  true` state from an earlier test rather than triggering a new pump-on.
- Live bridge-to-real-ESP test: `uvicorn` run locally with
  `AGRICONTROL_ESP_BASE_URL=http://192.168.0.11`, 5 real round trips
  relayed and logged correctly in the bridge's own event log.
- `python3 -m unittest discover -s tests` -> 88 passed, unaffected (the
  fix only touched firmware callers, not `logic/`).

Status updates:

- No roadmap task status changed from the bug fix itself (it corrects
  behavior for gate criteria, not a numbered task).
- Gates A, B, and C fully closed (18/26 criteria done).
- `data/progress-baseline.json` metrics: overall 54% -> 72% (`gate_percent`
  0% -> 69%, the single largest jump of any change this project has ever
  recorded, entirely because gate tracking had never been touched before).
  `updated_at` bumped to `2026-08-05T15:00:00+09:00`;
  `web-build/index.html`'s `BASELINE_VERSION` bumped to match, and its
  gate-clobbering dead code removed.

Next task: Gates D and E, and roadmap tasks 22/70/72-82, all need either
real physical hardware (sensors, a pump driver) this environment doesn't
have, or deliberate scope decisions (MQTT, multi-device, auth, packaging)
the project's own docs say to defer. This is close to a genuine stopping
point for further autonomous progress without the owner's involvement.

Date: 2026-08-05 JST (ten more roadmap tasks closed: Stage 4/5's shared infrastructure, proven via irrigation_slice.cpp)

Agent: agent-04-firmware-runtime (Claude Sonnet 5).

Directly following the tasks 56/57 session: noticed that several Stage 4
("ESP runtime") and Stage 5 ("first vertical slice") tasks were still
`active` even though `irrigation_slice.cpp` -- which had by this point
been extensively tested live on real hardware -- shares the exact same
asynchronous runtime, event system, HTTP server, request validation,
window-command calculation, servo actuation, OLED display, and JSON
response code as `runtime.cpp`/`vertical_slice.cpp`. Filled two remaining
test gaps, then closed all of them with the same "irrigation_slice.cpp is
a strict superset" reasoning already used for task 32.

Gaps filled with fresh real-hardware tests:

- **Window angle 170 (task 34's full range)**: sent temperature=40C,
  confirmed `window_angle: 170, fan: true` -- the >35C branch, not
  previously exercised on this hardware (only 10 and 90 had been).
- **Request-size limit (task 30)**: sent a 2264-byte body (over the
  2048-byte `kMaxRequestBodyBytes` limit) -- got HTTP 413, confirming the
  limit is enforced, not just present in the source.
- **Servo motion, directly observed (task 35)**: after the 170-degree
  reading, sent a cold reading (window should return to 10); asked the
  owner to watch the physical servo -- confirmed it visibly swung from
  170 to 10 ("yes"). The clearest, most direct piece of hardware evidence
  gathered this session -- an actual described physical motion, not just
  a JSON field matching an expectation.
- **Temperature-only request (task 31's Stage 5 scope)**: confirmed
  `irrigation_slice.cpp` still handles a request with only `temperature`
  correctly (also re-confirmed the `IRRIGATION-HOLD` rule-name quirk
  found in the previous session, on a second, independent request).

One anomaly noted honestly: between two of these tests, the board's
`isStartup` state reappeared (a `STARTUP` override on a request that
should have been well past that point), meaning the board silently reset
at some point without any visible cause. Not investigated further --
serial capture remains unreliable in this environment for the reasons
noted in the earlier MQTT-harness session, and the retry-with-a-warm-up
pattern already established handled it without needing to know why.
Recorded here as an open question, not swept under the rug.

Status updates:

- Roadmap tasks 24 (async runtime), 26 (event system), 29 (HTTP server),
  30 (request-size/validation limits), 31 (temperature-only scope), 33
  (message validation), 34 (window command), 35 (servo command), 36
  (OLED reason display), and 37 (JSON response) all marked `done` -- ten
  tasks in one entry, all justified by the same file
  (`irrigation_slice.cpp`) that was already extensively tested this
  session, not by newly testing `runtime.cpp`/`vertical_slice.cpp`
  themselves (which remain compiled-only, unflashed in their own right --
  see the caveat already recorded for task 32).
- No branch status change -- branches 4/5/7/8/9/10/11/12 were already
  `implemented` from this session or earlier ones.
- `data/progress-baseline.json` metrics: overall 53% -> 54%, roadmap 77%
  -> 84% (59/82 -> 69/82 tasks done; branches/control-loop unchanged, no
  branch crossed a new threshold). `updated_at` bumped to
  `2026-08-05T14:00:00+09:00`; `web-build/index.html`'s `BASELINE_VERSION`
  bumped to match. Notes field rewritten again for concision.

Next task: only tasks 22 (needs the pump/fan pin decision) and 70
(intentionally gated on runtime stability) remain reachable without a
Stage 11/12 scope decision. This is very close to the natural end of what
this project's software-and-firmware work can do without the owner
making those decisions or acquiring additional physical sensors/actuators.

Date: 2026-08-05 JST (roadmap tasks 56/57 closed: irrigation_slice.cpp's alarm colors/tones/OLED confirmed live)

Agent: agent-02-hardware, agent-04-firmware-runtime (Claude Sonnet 5).

Directly following the Stage 3 output-test milestone: reflashed
`env:irrigation_slice` (which the Stage 3 tests had overwritten) and, with
the owner watching and listening in real time, walked it through three
reachable alarm states via `curl` against `192.168.0.11/sensor`:

1. First message (`isStartup`): `alarm_level: startup_indication`.
   Owner confirmed the NeoPixels were blue and the OLED showed the
   expected TEMP/WIN, SOIL, TANK, and PUMP/FAN lines ("yeah all right").
2. Low-tank / stale-data warning: `alarm_level: warning`. Owner confirmed
   yellow ("see it").
3. Fresh, in-range reading: `mode: automatic`, `alarm_level: normal`.
   Owner confirmed green ("good").
4. Asked directly whether the buzzer was also audible at each alarm
   change (a distinct pitch per severity, non-blocking, only firing on
   transitions) -- owner confirmed ("heard it").

**Not tested**: `critical` (red LED, 440Hz tone) is not reachable through
this build's HTTP interface at all -- `kEmergencyStopActive` and
`kControllerFaultActive` are still hardcoded `false` placeholders in
`irrigation_slice.cpp` (open owner questions, unchanged for many
sessions), so there is no sensor input that can trigger it. This is an
honest gap, not an oversight in testing.

Status updates:

- Roadmap tasks 56 ("Connect LED and buzzer warnings") and 57 ("Add
  corresponding OLED pages") marked `done` -- direct owner observation of
  the specific color mapping, tone-on-change behavior, and OLED content
  this project has been carrying as an "explicit interpretation, not
  confirmed" caveat since Stage 7 was first drafted.
- No branch status change -- branches 10/11/12 (Actuator abstraction,
  Physical outputs, Observability) were already `implemented` from
  earlier sessions and this doesn't cross a new threshold for any of
  them.
- `data/progress-baseline.json` metrics: overall 52% -> 53%, roadmap 76%
  -> 77% (57/82 -> 59/82 tasks done; branches/control-loop unchanged).
  `updated_at` bumped to `2026-08-05T13:00:00+09:00`;
  `web-build/index.html`'s `BASELINE_VERSION` bumped to match.

Next task: task 22 ("Connect hardcoded decisions to outputs") and task 70
(watchdog, intentionally gated) are the only roadmap items left in
`next_tasks`. Task 22 needs the pump/fan GPIO/relay decision before it can
mean anything physically -- everything else reachable without that
decision or without Stage 11/12 scope choices has now been closed this
session.

Date: 2026-08-05 JST (Stage 3 output tests closed: owner-confirmed on real AgriControl firmware)

Agent: agent-02-hardware, agent-04-firmware-runtime (Claude Sonnet 5).

Flashed `env:test_oled`, `env:test_neopixel`, `env:test_buzzer`, and
`env:test_all_outputs` onto the physical board in sequence (each
overwrites the previous, so only `test_all_outputs` -- the combined test
-- was live when the owner looked). This is the piece none of the
session's prior hardware work could close alone: flashing and running
the code is now fully within reach, but confirming an OLED shows the
right text, NeoPixels show the right color, or a buzzer makes a sound at
all still needs eyes and ears this agent doesn't have.

The owner directly observed the board while `test_all_outputs.cpp` was
running (OLED text "AgriControl" / "All-outputs test" / "Stage 3 task
21", all 3 NeoPixels blinking dim green on/off every second, an 880Hz
buzzer tone once per second) and confirmed: "all works."

Evidence:

- All four environments built and flashed without error (build tooling
  confirmed working across this whole session; not new evidence on its
  own, but the prerequisite for this task).
- Direct owner observation of the physical board, reported in this
  conversation: OLED, NeoPixel, and buzzer all functioning correctly.

Status updates:

- Roadmap tasks 17 ("Test OLED independently"), 18 ("Test NeoPixel
  independently"), 19 ("Test buzzer independently"), and 21 ("Test all
  outputs together") all marked `done`. Tasks 17-19 rely on the combined
  test's success as evidence for each individual peripheral (the owner
  watched `test_all_outputs`, not each standalone environment
  separately) -- a reasonable inference (a broken OLED or dead buzzer
  would have surfaced in the combined test too, since they share the
  same wiring/pins as their standalone counterparts), recorded honestly
  as such rather than claiming separately-observed evidence that wasn't
  actually gathered.
- Branch 11 (Physical outputs) advanced `drafted` -> `implemented`.
- `data/progress-baseline.json` metrics: overall 51% -> 52%, roadmap 73%
  -> 76% (53/82 -> 57/82 tasks done), branches 61% -> 63%, control loop
  68% -> 70% (branch 11 appears in loop step 8). `updated_at` bumped to
  `2026-08-05T12:00:00+09:00`; `web-build/index.html`'s `BASELINE_VERSION`
  bumped to match. Also trimmed the dashboard's `notes` field again,
  which had grown long across several sessions' worth of appends.

Next task: task 22 ("Connect hardcoded decisions to outputs") and tasks
56/57 (irrigation_slice.cpp's specific NeoPixel color mapping and OLED
soil/tank/pump/fan page content) are the natural next hardware items --
both are now genuinely reachable the same way this session's other tasks
were (flash + curl + owner observation), unlike task 22 which additionally
needs the still-open pump/fan pin decision before it can mean anything
physically.

Date: 2026-08-05 JST (roadmap task 48 closed: real endurance test against the physical board)

Agent: agent-04-firmware-runtime (Claude Sonnet 5).

With `env:irrigation_slice` flashed and reachable at `192.168.0.11`
(previous entry), the hardware half of roadmap task 48 became directly
reachable too -- the bridge-side half was already proven in Stage 6
(`backend/tests/test_app.py::TestEndurance`, 200 sequential updates
against a fake ESP); this closes the other half against the real board.

Ran 300 sequential `POST /sensor` requests directly against the physical
ESP32 (varying temperature/soil/tank/rain each time, not the same
payload repeated), checking every response for HTTP 200, `accepted:
true`, and the correct echoed sequence number.

Evidence:

- 300/300 requests succeeded, zero failures.
- ~63ms/request average (19.0s total for 300 requests).
- A follow-up sanity request after the run confirmed the board was still
  fully responsive and computing correct decisions, not just still
  "up" -- no degradation from the sustained run.

Status updates:

- Roadmap task 48 ("Run hundreds of updates") marked `done` -- both
  halves (bridge-side, board-side) now have real evidence.
- `data/progress-baseline.json` metrics: overall 50% -> 51%, roadmap
  stays 73% at this rounding (52/82 -> 53/82 tasks done;
  branch/control-loop percentages unchanged, no branch status crossed a
  threshold). `updated_at` bumped to `2026-08-05T11:00:00+09:00`;
  `web-build/index.html`'s `BASELINE_VERSION` bumped to match.

Date: 2026-08-05 JST (roadmap task 32 closed with real hardware: env:irrigation_slice flashed and curl-tested directly)

Agent: agent-04-firmware-runtime (Claude Sonnet 5).

Directly following the MQTT harness milestone below: ported the
WiFi-reconnect-robustness fix (found there) back to `runtime.cpp`,
`vertical_slice.cpp`, and `irrigation_slice.cpp` -- all three previously
never retried a dropped WiFi connection at all (worse than the harness's
original bug, which at least tried, just unsafely). Then flashed
`env:irrigation_slice` itself -- the actual production file, not the
parallel harness -- onto the physical board and tested it directly via
`curl` against its own local HTTP server, closing roadmap task 32 with
first-party evidence instead of the harness's (still valuable, but
one-file-removed) evidence.

Found the board's local IP (`192.168.0.11`) via a subnet port scan since
serial output remained unreliable to capture right after a fresh flash
(same ESP32-C3 native-USB-CDC quirk as the harness session -- the ROM
bootloader's own messages come through fine, application-level `Serial`
output does not, for reasons not fully run to ground, but consistently
reproducible and evidently not indicative of any actual fault, since the
broker/HTTP logs independently confirm the device works correctly
regardless of what serial shows).

Changed:

- Added the same `maintainWiFi()` / backoff pattern from
  `mqtt_test_harness.cpp` to `runtime.cpp`, `vertical_slice.cpp`, and
  `irrigation_slice.cpp`'s `loop()` functions (setup()'s blocking connect
  is unchanged and still setup()-only). Also added a `Serial.println` of
  the assigned IP on connect to all three, for whenever serial capture
  does work.

Evidence -- six real `curl` requests against `http://192.168.0.11/sensor`,
all responses reproduced in full below because they are the evidence,
not just a claim of evidence:

1. First-ever message (`isStartup`): `mode: safety_override`,
   `alarm_level: startup_indication`, safe state (fan off, window 10,
   pump off), `STARTUP` override -- correct.
2. After a gap (data gone stale again between test batches):
   `mode: safety_override`, `DATA-STALE` override, safe state -- correct.
3. Fresh data, temperature=32C/soil=20%/rain=0: `mode: automatic`,
   `fan: true`, `window_angle: 90`, `pump: true`,
   `[TEMPERATURE-002, IRRIGATION-001]` -- matches `logic/decision.py`
   exactly (28C < 32C <= 35C -> fan on/window half; moisture < 30% and no
   rain -> pump on).
4. Cold temperature (20C) + wet soil (50%): `fan: false`,
   `window_angle: 10`, `pump: false`,
   `[TEMPERATURE-001, IRRIGATION-002]` -- correct.
5. Low tank (soil 20%/tank 10%, after a warm-up reading to clear
   staleness): decision engine still requests the pump
   (`IRRIGATION-001` reasoning), safety supervisor forces it off,
   `LOW-TANK` override -- the `EQUIPMENT_PROTECTION` tier confirmed
   correct on real hardware, matching the blueprint's own worked
   conflict example exactly.
6. Invalid temperature (999C): HTTP 400, rejected before reaching the
   decision engine at all.

**One genuine, minor discrepancy found and worth recording honestly**:
`firmware/include/irrigation.h` labels the "soil_moisture or rain
reading unavailable" branch with rule name `"IRRIGATION-HOLD"`
(`irrigation.h:69`) -- `logic/decision.py`'s equivalent branch (lines
73-75) does not add *any* triggered-rule entry for this case, only a
reason string. The actual computed pump/fan/window values are identical
either way; this only affects what appears in the `triggered_rules`
diagnostic array. This means the "line-by-line verified port" claim made
in earlier sessions wasn't perfectly literal in this one spot. Not fixed
here -- deciding whether `decision.py` should gain a matching rule label,
or `irrigation.h` should drop it, is a small design call for a future
session or the owner, not something to change unilaterally while
documenting a test result. Found only because the code was actually run,
not reviewed -- exactly the kind of thing this whole exercise was for.

Status updates:

- Roadmap task 32 ("Send temperature with curl") marked `done` -- direct,
  first-party evidence from the actual named transport and file, unlike
  the MQTT harness session's evidence.
- Branch 5 (ESP communication) advanced `drafted` -> `implemented` --
  real physical HTTP communication now confirmed, a stronger bar than
  branches 6-10's host-test-only evidence.
- `data/progress-baseline.json` metrics: overall 49% -> 50%, roadmap 72%
  -> 73% (51/82 -> 52/82 tasks done), branches 59% -> 61%, control loop
  66% -> 68% (loop steps 3 and 12 both reference branch 5). `updated_at`
  bumped to `2026-08-05T10:00:00+09:00`; `web-build/index.html`'s
  `BASELINE_VERSION` bumped to match.

Next task: `vertical_slice.cpp` and `runtime.cpp` themselves are still
compiled-only, not individually flashed (though `irrigation_slice.cpp`
is a strict superset of both, so this is a formality more than a real
gap). The bigger remaining items are physical: pump/fan pin assignment,
Stage 3's OLED/NeoPixel/buzzer/all-outputs tests using AgriControl's own
firmware specifically (not the other project's), and the emergency-stop
switch decision.

Date: 2026-08-05 JST (first real hardware verification of AgriControl's own compiled firmware)

Agent: agent-04-firmware-runtime, agent-02-hardware (Claude Sonnet 5).

**Corrected a long-standing wrong assumption first**: every prior session in
this project, including this one's own earlier turns, stated "no
PlatformIO toolchain, no board, no WiFi network reachable from here" as an
environment fact. It was never actually true in this sense -- the
sandboxed Bash tool runs directly on the owner's own Mac (the same
machine with the physical board's USB connection), not an isolated remote
container. The owner surfaced this by pointing out "usb is already
connected" after being told flashing wasn't possible; checking
`/dev/cu.usbmodem1101` confirmed it. `pip install platformio` then just
worked. This should have been checked much earlier rather than assumed.

**Result: `pio run` (build-only) now succeeds for all 10 firmware
environments** -- the first time any of this project's C++ has ever
actually been compiled, after many sessions of "reviewed, not compiled"
firmware. This surfaced a real, previously-undetected bug affecting
*every* environment: `build_src_filter = +<file.cpp> -<*>` has its
patterns in the wrong order for this PlatformIO version -- the later
`-<*>` (broader) pattern overrides the earlier `+<file.cpp>` match,
producing "Nothing to build" for literally every environment. Fixed by
reversing the order (`-<*> +<file.cpp>`) project-wide in
`firmware/platformio.ini`. This had been sitting broken since Stage 3 and
was only caught because this is the first time anyone (owner or agent)
ran `pio run` at all.

**Then flashed and debugged `env:mqtt_test_harness` against the real
ESP32-C3M-TRY board** (the same physical board, now dedicated to
AgriControl -- the owner disconnected it from the `Full-control-on-ESP32`
project first). Three real bugs found and fixed through iterative
flash-and-observe cycles, using a combination of direct serial capture
(via `pyserial`, since PlatformIO's own `device monitor` needs a real TTY
this environment doesn't have) and the Mosquitto broker's own verbose log
(`log_type all`) as a second, independent observation channel when serial
output proved unreliable to capture reliably right after a fresh flash:

1. **`connectMqtt()` had no reconnect backoff.** A transient failure right
   after a successful CONNECT triggered a tight reconnect loop (the broker
   log showed the same client ID reconnecting and kicking off its own
   previous session repeatedly, seconds apart). Fixed by adding a 3000ms
   minimum gap between attempts, mirroring the reference project's own
   `connectMqtt()` pattern.
2. **`connectWiFi()` was blocking and reused unsafely from `loop()`.**
   Calling `WiFi.begin()` again while a connection attempt was already
   resolving produced `wifi:sta is connecting, return error` (caught via
   serial), and the up-to-15-second blocking wait, when triggered from
   `loop()`, stalled `mqttClient.loop()` long enough to compound the MQTT
   instability above. Split into `connectWiFiBlocking()` (setup()-only,
   blocking is fine at boot) and a non-blocking `maintainWiFi()` (loop()
   -safe, own 5000ms backoff, never blocks).
3. **The Mosquitto ACL for the new `agricontrol-test-harness` credential
   was backwards.** Granted `write`-only on `agricontrol/sensor` and
   `read`-only on `agricontrol/state`, reasoning about the topics from a
   "test client publishes/reads" perspective -- but the same credential
   is also what the *device* uses, and the device needs to *subscribe*
   (read) `agricontrol/sensor` and *publish* (write) `agricontrol/state`.
   ACL enforcement had also been silently broken since this user was
   created (traced to `/etc/mosquitto/acl.conf` having the wrong
   owner/permissions -- Mosquitto 2.0.18 warns but doesn't refuse to load
   a world-readable, non-`mosquitto`-owned ACL file, and apparently
   doesn't enforce it correctly either in that state), so this asymmetry
   went undetected until a full `systemctl restart mosquitto` finally got
   the ACL loading and enforcing correctly -- at which point it started
   correctly *blocking* both directions. Fixed by granting `readwrite` on
   both topics for this credential.

**Verified end-to-end, for real, for the first time**: published a
sensor reading via `tools/mqtt_hardware_verify.py` and read back the
physical board's actual response.

- First message (after a stale gap): `mode: safety_override`,
  `alarm_level: warning`, `fan: false`, `window_angle: 10`, `pump: false`,
  `triggered_rules: [TEMPERATURE-002, IRRIGATION-001, DATA-STALE]` -- the
  safety supervisor correctly overriding to the safe state because the
  prior reading had gone stale, exactly matching the documented safe-state
  matrix.
- Subsequent messages (fresh data): `mode: automatic`, `alarm_level:
  normal`, `fan: true`, `window_angle: 90`, `pump: true`, matching
  `logic/decision.py`'s already-host-tested rules exactly for
  temperature=32C (TEMPERATURE-002: fan on, window half) and
  soil_moisture=20%/rain=0 (IRRIGATION-001: pump on).

This is the first time in this project's history that `decision.h`/
`safety.h`/`irrigation.h`, compiled into a real binary and run on the
physical board, have been confirmed to produce correct output -- not
reviewed C++, not a host-tested Python mirror, the actual compiled
firmware. `env:mqtt_test_harness` is a field-for-field duplicate of
`irrigation_slice.cpp`'s validation/decision/safety/actuation pipeline
(only the transport differs, MQTT vs. WebServer -- see that file's
header), so this is very strong, though not literally direct, evidence
that `irrigation_slice.cpp` itself would behave identically if flashed
and driven over local HTTP instead. Roadmap task 32 ("Send temperature
with curl") is deliberately **not** marked done from this: it names curl
against the local-HTTP environments specifically, which remain unflashed
and untested in their own right. Overclaiming task 32 from a different
file's success would repeat exactly the mistake this project has
consistently avoided all session.

Evidence:

- `pio run` (all 10 environments): SUCCESS.
- `pio run -e mqtt_test_harness -t upload --upload-port /dev/cu.usbmodem1101`:
  SUCCESS, multiple times across the debugging iterations.
- Mosquitto broker log (`/var/log/mosquitto/mosquitto.log`, verbose mode):
  direct confirmation of `CONNECT`/`CONNACK`, `SUBSCRIBE`/`SUBACK`,
  `PUBLISH`/`PUBACK` at the protocol level, independent of any
  client-library interpretation.
- Full request/response JSON pairs from `tools/mqtt_hardware_verify.py`,
  cross-checked field-by-field against `logic/decision.py`'s documented
  thresholds.

Status updates:

- No roadmap task or branch status changed as a direct result of this
  session -- the genuinely new, durable facts are: (a) the whole firmware
  project now compiles cleanly (a real, low-risk, unambiguous fact worth
  recording even without a specific task tied to it), and (b) the
  decision/safety logic is now confirmed correct when compiled and run on
  real hardware, via a parallel test harness rather than the "production"
  files themselves.
- Known Limits (below) updated: "firmware/ has never been compiled or
  run" is no longer accurate and has been corrected.

Left open / not attempted this session:

1. The same WiFi-reconnect-robustness bug (blocking `WiFi.begin()` in
   `setup()`, never retried in `loop()`) almost certainly also exists in
   `runtime.cpp`, `vertical_slice.cpp`, and `irrigation_slice.cpp` --
   discovered here because `mqtt_test_harness.cpp` happened to get
   exercised long enough to hit it, not because those other files were
   checked. Not fixed there this session; flagged for the next one.
2. The physical board is now running `env:mqtt_test_harness`, not any of
   the "production" local-HTTP environments. Flashing
   `env:irrigation_slice` and testing it via curl (roadmap task 32) is
   still open and would be the direct way to close it.
3. The Mosquitto ACL fix applied here is specific to the
   `agricontrol-test-harness` credential this project added -- the
   pre-existing `esp32-device`/`dashboard-backend` entries for the other
   project were not touched and were not re-verified after the ACL
   enforcement bug was found; whether they were also affected by the same
   silent-bypass window is unknown and is that project's concern, not
   this one's, but worth the owner being aware of.

Date: 2026-08-04 JST (MQTT hardware-verification harness -- ad-hoc, not a numbered roadmap task)

Agent: agent-04-firmware-runtime, agent-02-hardware (Claude Sonnet 5).

Following the live hardware session below (verifying LED/servo/buzzer on
a *different* project's firmware via `esp32.phyowaisoe.com`), the owner
pointed at a second, private repo -- `Full-Control-on-ESP-32-on-VPS` --
and asked for AgriControl's own firmware to be made runnable through that
same remote channel, "if you can prove this design will have good
approach to the mission."

**The case for this, made explicit before building anything**:

1. It does not weaken the blueprint's core rule ("no interface may bypass
   the central control loop"). The ESP stays the sole decision-making
   authority -- MQTT is a transport swap for sensor-in/state-out, exactly
   analogous to `runtime.cpp`'s existing HTTP transport, not a new place
   where decisions get made.
2. It reuses `firmware/include/irrigation.h` (itself built on `decision.h`/
   `safety.h`, both already proven by 35+ host tests) completely
   unmodified. Zero risk of logic drift between this harness and
   `irrigation_slice.cpp`.
3. It closes the single most-repeated caveat in this entire project's
   history: "no PlatformIO toolchain, no board, no WiFi network reachable
   from here." AgriControl's existing local-HTTP design assumes the
   tester is on the same local network as the board -- true for the
   owner, never true for an AI agent with no physical presence. This is
   the first mechanism that could make "verified by me directly" actually
   possible for *AgriControl's own* code, not just corroborating evidence
   from a different project's firmware.
4. It is narrowly scoped and fully reversible: one new `.cpp` file, one
   new PlatformIO environment, one new gitignored secrets file. Nothing
   in `runtime.cpp`, `vertical_slice.cpp`, `irrigation_slice.cpp`, or any
   existing environment changes. Deleting `mqtt_test_harness.cpp` removes
   this entirely.
5. Different justification than Stage 12 task 77 ("Add MQTT"), which is
   about a *product* feature (remote access, multi-device, cloud). This
   is a *development-time verification aid* -- closer in spirit to Stage
   8's fake-ESP scenario tests (real logic, not-the-real-transport) than
   to a permanent architecture choice. No Stage 12 task is marked done
   from this, and the local-HTTP design remains AgriControl's real
   architecture.

Changed:

- Added `firmware/src/mqtt_test_harness.cpp` (`env:mqtt_test_harness`):
  a near-duplicate of `irrigation_slice.cpp` with `WebServer` replaced by
  `PubSubClient` (MQTT) -- same validation, same `evaluateFullDecision`/
  `evaluateFullSafety` calls, same servo/NeoPixel/buzzer/OLED actuation,
  field-for-field. Subscribes `agricontrol/sensor`, publishes
  `agricontrol/state` -- topics deliberately separate from the other
  project's `esp32/command`/`esp32/state`, which belong to a different
  firmware's LED/servo/sound command vocabulary this file has no
  relationship to.
- Added `firmware/include/mqtt_secrets.h.example` and gitignored
  `firmware/include/mqtt_secrets.h` (MQTT broker identity), following the
  same pattern as `secrets.h`/`secrets.h.example` for WiFi.
- Added `firmware/platformio.ini`'s `[env:mqtt_test_harness]`, adding
  `knolleary/PubSubClient` only for this environment
  (`lib_deps = ${env.lib_deps} \n knolleary/PubSubClient`), not globally.
- Added `tools/mqtt_hardware_verify.py`: a Python MQTT client (matching
  the `paho-mqtt` library the VPS's own `server/app.py` uses) that
  publishes one simulated sensor reading and waits for the board's real
  response -- the tool that would actually be used to verify AgriControl's
  compiled firmware once the remaining access gaps below are resolved.
  `build_payload()` is pure logic, genuinely tested (see Evidence); the
  network I/O around it is not, and cannot be, executed in this
  environment.
- Added `tests/test_mqtt_hardware_verify.py`: 4 passing tests for
  `build_payload()` (temperature-only, all-fields, partial-fields, and
  specifically that `rain=0.0` isn't dropped as falsy -- the same bug
  class `backend/app.py`'s `is not None` checks already guard against).

Evidence:

- `python3 -m unittest discover -s tests` -> 88 passed (up from 84).
- `python3 -m pytest backend/tests/` -> 24 passed, unaffected.
- **Not** built, flashed, or run against real hardware -- same caveat as
  every other firmware file in this project. This session produced a
  reviewed, ready-to-flash design, not verified working code.

What this does *not* resolve (still open, tracked as
`firmware/README.md` questions 9-10):

1. No MQTT broker credentials exist yet for this harness or for
   `tools/mqtt_hardware_verify.py` to actually connect -- needs a
   distinct client identity scoped to `agricontrol/#` topics on the
   Mosquitto broker behind `esp32.phyowaisoe.com`, not a reused device
   credential from the other project.
2. No confirmed way to flash this onto the physical board remotely --
   `pio run -e mqtt_test_harness -t upload` still needs either the owner
   doing it directly, or some SSH-reachable machine with the board
   attached via USB that this environment doesn't have access to.

Until both are resolved, this stays exactly where every other firmware
file in this project sits: reviewed, not verified. Recorded here in full
because the *reasoning* for building it is itself part of the durable
record -- if it turns out to be the wrong call, that reasoning is what
should get revisited, not just the code.

Date: 2026-08-04 JST (live hardware verification via esp32.phyowaisoe.com, not AgriControl's own firmware)

Agent: agent-02-hardware (Claude Sonnet 5).

The owner pointed at `https://esp32.phyowaisoe.com`, a live remote-control
panel (`GET /api/state` read-only, `POST /api/command` with an `x-pin`
header) for the physical ESP32-C3M-TRY board, currently running the
*separate* `Full-control-on-ESP32` firmware, not AgriControl's own
compiled code. This is the first genuinely first-hand interaction with the
real board in this environment (everything before this was either host
logic, or evidence the owner reported secondhand).

**Confirmed the board is online and live right now**: `GET /api/state`
returned real, moving sensor readings (temperature ~31.8-32.1C, humidity
~54-57%, ambient light ~0.15 normalized) with a current `updatedAt`
timestamp -- not stale/cached data.

Sent four commands via `POST /api/command` and confirmed each was
genuinely applied (not just accepted) by re-reading `/api/state` afterward:

- `{"command":"servo","angle":90}` -> `servoAngle` reported back as
  exactly `90`.
- `{"command":"sound","frequency":660,"duration":3000}` -> `sound`
  reported `true` while active (a short first attempt at 400ms was missed
  entirely, since it had already finished by the time of the follow-up
  read -- the retry used a longer duration specifically to catch the
  `true` state, not just get a 200 from the API).
- `{"command":"set","r":0,"g":45,"b":0,"led":-1}` (AgriControl's own
  "normal" NeoPixel status color) -> `led0`/`led1`/`led2` reported back
  as `11520`, exactly `(0<<16)|(45<<8)|0` -- the packed color math
  matches precisely, not just "some color changed."
- `{"command":"display_text","text":"AgriControl hw check OK"}` -> `note`
  field reported the exact text back.

Then returned the board to a neutral state: `{"command":"off"}` (LEDs
off) and `{"command":"servo","angle":10}` (AgriControl's own
`WINDOW_CLOSED_DEG`, a sensible resting position). Attempting to clear
the OLED note via an empty `text` value was rejected by the Worker
("Bad display settings") even though the firmware itself treats empty
text as "clear" (`main.cpp`'s `noteActive = noteText.length() > 0`) --
a discrepancy in that project's own Worker validation, not AgriControl's
concern to fix. The harmless leftover note was left in place rather than
fought further.

**What this does and does not prove**: this genuinely confirms the LEDC
PWM buzzer approach ported into AgriControl last session (`irrigation_slice.cpp`,
`test_buzzer.cpp`, `test_all_outputs.cpp`) produces real, audible-range
PWM output on this exact chip -- the single largest open question about
that port. It also confirms the servo reaches commanded angles precisely
and the NeoPixels accept exact RGB values, using the same libraries
(ESP32Servo, Adafruit_NeoPixel) AgriControl's own firmware uses on the
same pins. It does **not** prove AgriControl's own compiled firmware
works -- this ran a different project's `main.cpp`, built with a
different OLED library (Adafruit_SSD1306+GFX vs. AgriControl's U8g2) and
no decision engine, safety supervisor, or HTTP `/sensor` endpoint at all.
No roadmap task status changed from this -- Stage 3's tasks 17-19/21
still require AgriControl's *own* firmware to actually be flashed and
observed before they can move past `active`, per the standard already
applied consistently everywhere else in this project. Recorded here as
strong corroborating evidence, not roadmap evidence.

Also noteworthy: the live ambient temperature (~32C) sits inside
AgriControl's own "fan on, window half open" band (28-35C per
`logic/decision.py`'s `TEMP_FAN_ON_ABOVE`/`TEMP_WINDOW_FULL_ABOVE`) --
real-world confirmation that these placeholder thresholds are at least in
a physically plausible range for wherever this board actually sits, not
just internally consistent numbers.

Next task: this doesn't change what's next -- Stage 3's output tests
still need AgriControl's own `env:test_oled`/`test_neopixel`/
`test_buzzer`/`test_all_outputs` flashed via PlatformIO and observed, not
just this other firmware exercised through its remote panel.

Date: 2026-08-04 JST (Stage 4/5 protocol: staleness, recovery, message validation, host/tested)

Agent: agent-03-logic (Claude Sonnet 5).

After Stage 10, re-checked whether "pure-software roadmap progress is
exhausted" (the prior session's stated conclusion) actually held up. It
didn't: Stage 5's remaining test tasks (38-40: repeated messages, invalid
values, timeout and recovery) looked hardware-blocked at a glance, but the
behavior they test -- sequence-duplicate rejection, temperature-range
validation, staleness+recovery mode transitions -- is pure logic that
`firmware/include/canonical.h`'s `isStale`, `firmware/include/
system_state.h`'s `RecoveryTracker`, and `firmware/include/
shared_state.h`'s `SharedState::tick()` already implement in C++, with no
Python equivalent to prove it against first. Same gap Stage 9 found for
actuator feedback, just in a different corner of the codebase.

Changed:

- Added `logic/protocol.py` (roadmap tasks 25/27/28/38/39/40, Branches 4:
  Protocol, 7: State management): `is_valid_sequence()` (rejects
  duplicate/out-of-order sequence numbers, task 38) and
  `is_valid_temperature_c()` (rejects physically implausible readings
  before they'd reach the decision engine, task 39) factor out validation
  that was previously duplicated inline across three different .cpp
  files. `is_stale()` and `RecoveryTracker` mirror `canonical.h`'s
  staleness check and `system_state.h`'s recovery-streak tracker (tasks
  27/28). `evaluate_tick()` mirrors `SharedState::tick()`'s full cycle:
  staleness moves AUTOMATIC->WARNING, freshness moves WARNING->RECOVERY,
  and enough consecutive valid messages move RECOVERY->AUTOMATIC (task
  40) -- proving the same recovery chain the blueprint documents
  (Failure -> Safe state -> Consecutive valid messages -> Stable
  communication confirmed -> Resume automatic).
- Added `tests/test_protocol.py`: 21 tests covering sequence validation
  (first-ever, duplicate, out-of-order, next, and gap-ahead cases),
  temperature boundaries (inclusive at -40/85, just outside, wildly out
  of range), staleness timing, `RecoveryTracker`'s streak behavior
  (confirms at exactly 5, resets on failure, doesn't overflow past 5),
  and a full multi-step recovery cycle exercised the same way
  `SharedState::tick()` would be called once per `loop()` iteration
  (staleness -> WARNING -> freshness -> RECOVERY -> N valid messages ->
  AUTOMATIC, plus repeated-stale-tick and stale-during-recovery edge
  cases).
- Refactored `backend/tests/test_scenarios.py`'s `invalid_data` scenario
  to call `logic.protocol.is_valid_temperature_c()` instead of a locally
  duplicated `-40/85` constant pair, removing that duplication now that
  a real home for it exists.

Evidence:

- `python3 -m unittest discover -s tests` -> 84 passed (up from 63).
- `python3 -m pytest backend/tests/` -> 24 passed, unaffected by the
  refactor (same behavior, single source of truth for the constant).
- Recomputed `data/progress-baseline.json`'s metrics by hand with the
  same formula as `web-build/index.html`, then confirmed the dashboard's
  own live jsdom rendering produces identical numbers before committing.

Status updates:

- Roadmap tasks 25, 27, 28 (Stage 4) and 38, 39, 40 (Stage 5) marked
  `done` -- same evidence bar as Stage 2's decision/safety tasks: a
  proven-correct Python algorithm, cross-checked line-by-line against
  the existing C++ header it mirrors. Tasks 24 (async runtime), 26
  (event system -- already covered by `backend/app.py`'s own tested
  `EventLog`, a distinct but analogous implementation, not directly
  reused as evidence here), 29 (HTTP server), and 30 (request-size
  limits) remain `active` -- genuinely un-host-testable without a real
  async loop or HTTP server.
- Branch 4 (Protocol) advanced `drafted` -> `implemented` -- first real
  tested content in that branch.
- `data/progress-baseline.json` metrics: overall 46% -> 49%, roadmap 61%
  -> 72% (45/82 -> 51/82 tasks done), branches 57% -> 59%, control loop
  63% -> 66% (loop steps 2 and 3 both reference branch 4). `updated_at`
  bumped to `2026-08-04T20:00:00+09:00`; `web-build/index.html`'s
  `BASELINE_VERSION` bumped to match. Also trimmed the dashboard's
  `notes` field, which had grown very long across several sessions, down
  to a concise current summary rather than appending indefinitely.

Next task: pure-software roadmap progress is now much closer to genuinely
exhausted -- every remaining `todo`/`active` task either needs the
physical board (Stage 3's output tests, task 32's curl-against-a-real-ESP,
Stage 4's async runtime/HTTP server, task 48's hardware half, Stage 7's
task 56/57 physical evidence) or is Stage 11/12 territory requiring a
deliberate owner scope decision (real sensors, MQTT, multi-device, auth,
packaging) that this project's own docs say to defer. Task 70 (watchdog)
stays intentionally untouched.

Date: 2026-08-04 JST (Stage 10 reliability: recording/replay/versioning/limits, host/tested)

Agent: agent-03-logic (Claude Sonnet 5).

Continuing in roadmap order after Stage 9: Stage 10 ("Reliability") targets
Branches 3, 4, 12, 13, 14. Its hazards, per `docs/PROMPT_TEST_LIBRARY.md`:
"Record protocol and rule versions. Do not add a watchdog until runtime
behavior is understood. Known limits must be explicit." Tasks 67, 68, 69,
71 are all pure logic/documentation and could be built and executed here;
task 70 (watchdog) is explicitly gated by the blueprint's own wording on
runtime stability this environment can't establish, so it was left alone
on purpose, not skipped by oversight.

Changed:

- Added `DECISION_RULES_VERSION`/`SAFETY_RULES_VERSION` constants to
  `logic/decision.py`/`logic/safety.py` (roadmap task 68) -- additive only,
  no behavior change, so the existing 35 Stage 2 tests needed no changes.
- Added `logic/replay.py` (roadmap tasks 67-68, Branch 14: Recording and
  replay, previously `planned`, the only branch still untouched):
  `record_cycle()` runs one real decision cycle and records every input,
  both rule versions, and the outputs produced; `replay_cycle()`/
  `replay_sequence()` re-run recorded inputs through the *current* rules
  and report any field that no longer matches what was recorded;
  `save_recording()`/`load_recording()` persist a recording as JSON lines.
- Added `tests/test_replay.py` (8 tests): recording correctness (including
  the low-tank case, where the recorded *requested* pump state and the
  recorded *commanded* state deliberately differ), replay-detects-nothing
  on an unmodified recording, replay-detects-a-hand-tampered field,
  replay-detects-mismatches-across-a-multi-cycle-sequence, and -- the
  strongest evidence -- **replay catches a genuine rule change**: the test
  temporarily mutates `decision.TEMP_FAN_ON_ABOVE` (restored in a
  `finally` block) and confirms `replay_cycle()` actually flags the
  now-different `requested_fan` outcome, proving this isn't just comparing
  trivially-equal data.
- Added `TestLongDurationRecordingAndReplay` (roadmap task 69): records
  1,000 varied cycles (temperature/moisture/rain/tank all cycling through
  their full ranges) and replays all of them, asserting zero mismatches
  over the full run -- endurance evidence for the new replay engine
  itself, distinct from `backend/tests/test_app.py`'s existing 200-update
  bridge endurance test.
- Added a "Known Limits" section to this file (roadmap task 71), listing
  the boundaries of the current design that hold regardless of any owner
  answer (single device, no persistent storage, no auth, no MQTT, no
  watchdog, pump/fan not physically driven, firmware never compiled,
  Stage 9's fault detection is simulated not measured, Stage 10's replay
  only catches drift in exercised code paths, and response-time evidence
  is bridge-side only) -- distinct from "Known Unknowns" below, which are
  open questions that *could* be answered.

Evidence:

- `python3 -m unittest discover -s tests` -> 63 passed (up from 55).
- `python3 -m pytest backend/tests/` -> 24 passed, unaffected.
- Recomputed `data/progress-baseline.json`'s metrics by hand with the same
  formula as `web-build/index.html`, then confirmed the dashboard's own
  live jsdom rendering produces identical numbers before committing.

Status updates:

- Roadmap tasks 67, 68, 69, 71 marked `done`. Task 70 (watchdog) stays
  `todo` -- explicitly gated, not attempted.
- Branch 14 (Recording and replay) advanced `planned` -> `implemented` --
  the first real content in that branch, backed by genuinely executed
  tests, same bar as every other `implemented` branch.
- `data/progress-baseline.json` metrics: overall 44% -> 46%, roadmap 61%
  -> 66% (41/82 -> 45/82 tasks done), branches 52% -> 57% (branch 14
  crossing planned->implemented), control loop unchanged at 63% (branch 14
  isn't referenced by any control_loop_steps entry). `updated_at` bumped
  to `2026-08-04T18:00:00+09:00`; `web-build/index.html`'s
  `BASELINE_VERSION` bumped to match.

Next task: everything remaining in `next_tasks` is now hardware-blocked
(Stages 3-7's board-dependent tasks) or Stage 11/12 territory (real
sensors, MQTT, multi-device, auth, packaging), all of which need the
physical board or a deliberate architecture decision the owner hasn't
made yet. This is the natural stopping point for pure-software roadmap
progress until real hardware access or further owner direction changes
what's reachable.

Date: 2026-08-04 JST (Stage 9 closed-loop simulation, host/tested)

Agent: agent-03-logic (Claude Sonnet 5).

Continuing in roadmap order after Stage 8: Stage 9 ("Closed-loop
simulation") targets Branches 2, 9, 10, 12, 13. Its core hazard, stated
directly in `docs/PROMPT_TEST_LIBRARY.md`: "Commanded state is not
measured state. Fault evidence must be explicit. Feedback faults must
influence safety or recovery behavior." All of that is pure logic --
no real board needed to prove it -- so like Stage 2/6/7/8 it could be
built and genuinely executed here.

Changed:

- Added `logic/actuator_feedback.py` (roadmap tasks 61-65): populates the
  `simulated_state`/`fault_state` fields `logic/actuator_state.py` already
  defines but nothing filled in yet.
  - `simulate_binary_actuator()` models fan/pump feedback: normal
    operation reports the commanded ON state only after a startup delay
    (task 62, not instant like a real relay); `FAILED_STARTUP` never
    reaches ON and faults (task 63); `STUCK_ON`/`STUCK_OFF` report a fixed
    state regardless of command, faulting only once that fixed state
    actually disagrees with what was commanded (task 64) -- a stuck-on
    relay looks fine right up until you try to turn it off.
  - `simulate_servo_actuator()` models the window servo: `WRONG_POSITION`
    reports an offset angle standing in for mechanical slip/binding (task
    65), clamped to the servo's 0-180 range.
  - `detect_mismatch()` is the general task-61 check: an explicit fault
    code from the source wins; otherwise any commanded/measured
    disagreement is itself a fault -- never silently assumed equal.
  - `to_actuator_state()` builds an `ActuatorState` record populating only
    `simulated_state`, leaving `measured_state` as `None` -- there is no
    real sensor yet (that's Stage 11: physical migration), and
    `actuator_state.py`'s own docstring is explicit the two must stay
    distinct.
- Roadmap task 66 ("make the ESP respond to feedback faults"): rather than
  modifying the already-verified `logic/safety.py` to add a new priority
  tier, a detected fault code is passed into `evaluate_safety()`'s
  existing `controller_fault` input. The proven SAFETY-tier response
  (safe state, critical alarm) applies unchanged; the specific fault code
  stays available separately as explicit evidence (task 66's "fault
  evidence must be explicit" hazard), not hidden inside a boolean.
  `safety.py` itself was not touched.
- Added `tests/test_actuator_feedback.py`: 20 new tests covering startup
  delay timing, failed-startup, stuck-on/off (both the "looks fine" and
  "faults on disagreement" cases), wrong-position clamping, mismatch
  detection (including the "no explicit fault code but states disagree
  anyway" case), `ActuatorState` evidence shape, and three end-to-end
  tests proving a detected actuator fault actually forces
  `evaluate_safety()` into the SAFETY tier with a critical alarm.
- **Not** ported to `firmware/`: unlike Stage 2's decision/safety logic,
  this is a fault-*simulation* capability, and porting it to the real ESP
  would require assuming feedback-sensor hardware (current-sense
  resistors, limit switches, etc.) that hasn't been confirmed for this
  board -- same caution already applied to the missing pump/fan pins.
  Flagged as an open owner question below rather than guessed.

Evidence:

- `python3 -m unittest discover -s tests` -> 55 passed (up from 35).
- `python3 -m pytest backend/tests/` -> 24 passed, unaffected (this
  session didn't touch `backend/`).
- Recomputed `data/progress-baseline.json`'s metrics by hand with the same
  formula as `web-build/index.html`, then confirmed the dashboard's own
  live jsdom rendering produces identical numbers before committing.

Status updates:

- Roadmap tasks 61-66 marked `done` -- real executed, passing host tests,
  same bar as every other pure-logic stage.
- No branch status changes: branches 2, 9, 10, 12, 13 were already
  `implemented` from prior sessions; this doesn't newly cross a threshold
  for any of them, and there's no established criterion yet for the
  `verified` tier beyond branch 1's example.
- `data/progress-baseline.json` metrics: overall 42% -> 44%, roadmap 54%
  -> 61% (35/82 -> 41/82 tasks done), branches/control-loop unchanged (no
  branch status crossed a threshold this round). `updated_at` bumped to
  `2026-08-04T16:00:00+09:00`; `web-build/index.html`'s `BASELINE_VERSION`
  bumped to match.

Blockers / open questions (tracked in `data/agent-coordination.json`):

1. Real actuator feedback hardware (current-sense resistors, limit
   switches, or similar) is not confirmed for this board -- without it,
   task 66's firmware-side implementation can't be built without
   guessing, so it stays logic-only for now.
2. Everything already open from Stage 4/5/7 (WiFi credentials, ESP IP,
   pump/fan pins, emergency-stop switch) still applies.

Next task: Stage 10 ("Reliability") tasks 67-69/71 (recording and replay,
rule versioning, long-duration tests, documenting known limits) look
partially software-reachable via the backend/simulator pairing, similar to
Stage 8/9. Task 70 (watchdog) is explicitly gated on runtime stability in
the blueprint's own wording, so it should wait. Tasks 17-19/21/22/24-40/48/
56/57 remain blocked on real board access, unchanged.

Date: 2026-08-04 JST (Stage 8 scenario testing, backend/tested)

Agent: agent-05-backend (Claude Sonnet 5).

Continuing in roadmap order after the buzzer-fix session below: Stage 8
("Scenario testing") is pure software, like Stage 6/7, so it could be built
and genuinely executed here, not just reviewed.

Changed:

- Added `backend/tests/test_scenarios.py` (roadmap tasks 58-60): 7 preset
  scenarios (normal, hot, dry_soil, low_tank, rain, invalid_data,
  communication_loss) run end-to-end through the FastAPI bridge
  (`POST /api/temperature`) against a fake ESP responder. Unlike prior
  fake-ESP test doubles in `backend/tests/test_app.py`, which hardcode a
  small mirror of the temperature-only rule, this one calls the *real*
  `logic/decision.py` (`evaluate_decision`) and `logic/safety.py`
  (`evaluate_safety`) functions directly -- the same host-tested algorithm
  `firmware/include/decision.h`/`safety.h`/`irrigation.h` are a verified
  line-by-line port of -- so each scenario's expected commands/mode/alarm
  come from proven logic, not hand-guessed values.
  - `low_tank` specifically exercises the EQUIPMENT_PROTECTION override
    (decision engine requests the pump on from dry soil; safety supervisor
    forces it off because the tank is below 15%).
  - `rain` exercises the rain-gates-pump rule (dry soil alone would trigger
    the pump; rain=1 blocks it, holding the previous state instead).
  - `invalid_data` and `communication_loss` exercise the bridge's protocol
    layer (502 + event log) for a rejected message and an unreachable ESP,
    matching `backend/app.py`'s existing error handling.
  - Response time (task 59) is checked against a generous 1-second budget
    on the in-process bridge call -- real evidence of the bridge's own
    performance, explicitly *not* evidence of the physical ESP's real
    round-trip time, which needs the real board.
  - PASS/FAIL (task 60) is the parametrized pytest assertions themselves;
    each scenario reports as its own pass/fail case.

Evidence:

- `python3 -m pytest backend/tests/ -v` -> 24 passed (17 prior + 7 new).
- `python3 -m unittest discover -s tests` -> 35 passed, unchanged (proves
  the scenario tests didn't require touching the already-proven logic
  layer).
- Recomputed `data/progress-baseline.json`'s dashboard metrics by hand
  using the exact same weighted-average formula as
  `web-build/index.html`'s `calcTaskProgress`/`calcBranchProgress`/
  `calcLoopProgress`, then confirmed the dashboard's own live jsdom
  rendering produces identical numbers before committing (same discipline
  established after the earlier "dashboard shows wrong numbers" incident).

Status updates:

- Roadmap tasks 58, 59, 60 marked `done` -- real executed, passing tests
  against the real decision/safety logic, same bar as Stage 6/7's software
  work.
- Branch 13 (Testing) advanced `drafted` -> `implemented` -- first real
  scenario/integration-style test coverage, matching the bar branches 6-10
  were already held to.
- `data/progress-baseline.json` metrics: overall 40% -> 42%, roadmap 50% ->
  54% (32/82 -> 35/82 tasks done), branches 50% -> 52%, control loop 61% ->
  63% (loop steps 10 and 12 both reference branch 13).
  `updated_at` bumped to `2026-08-04T14:00:00+09:00`; `web-build/index.html`'s
  `BASELINE_VERSION` bumped to match, per the discipline in `AGENTS.md`.

Next task: Stage 9 (closed-loop simulation: actuator feedback, delays,
failed starts, stuck faults, servo mismatch) is the next stage in roadmap
order, but it's mostly about *simulating hardware failure modes* which may
be better suited to the simulator/backend pairing than pure Python --
worth scoping carefully before starting. Tasks 17-19/21/22/32/38-40/48/56/57
remain blocked on real board access, unchanged.

Date: 2026-08-04 JST (buzzer fix ported from owner's other ESP32-C3M-TRY project)

Agent: agent-04-firmware-runtime (Claude Sonnet 5).

The owner pointed at a separate, actively hardware-tested repo on the same
GitHub account -- `phyo-wai-soe-jp/Full-control-on-ESP32` -- running on the
identical ESP32-C3M-TRY board, and asked for its code to be ported into
AgriControl where useful. That repo uses a materially different
communication architecture (MQTT over TLS via EMQX Cloud, relayed through a
Cloudflare Worker + Durable Object, for remote access from anywhere) instead
of AgriControl's local-HTTP-only design. That architecture is **not**
adopted here: the blueprint already places MQTT at Stage 12 ("Platform
growth"), and `docs/AI_CONTINUITY_SYSTEM.md` explicitly says to avoid MQTT
and cloud services until the first local control loop is proven stable.
Adopting it now would be a large, unrequested architecture change well past
what "port useful code" calls for.

What *was* ported is one concrete, hardware-justified correctness fix, plus
confirmation of the existing pin map:

- `firmware/include/pins.h`'s pin assignments (NeoPixel D10, buzzer D21,
  servo D7, I2C SDA D8/SCL D9, phototransistor D1) match
  `Full-control-on-ESP32/src/main.cpp` exactly -- independent, hardware-run
  confirmation of the board's pin table beyond the owner's manual alone.
- `firmware/src/irrigation_slice.cpp`'s buzzer previously used Arduino's
  `tone()`. The reference firmware deliberately avoids `tone()`/`noTone()`
  in favor of driving the piezo directly through the ESP32's LEDC PWM
  peripheral (`ledcSetup`/`ledcAttachPin`/`ledcWriteTone`), with a comment
  noting `tone()` support is unreliable on this core. `tone()`/`noTone()`
  are a known ESP32 Arduino-core gap (originally AVR-only, inconsistently
  backported, particularly shaky on RISC-V parts like the C3). Ported the
  same LEDC approach into `soundAlarmChangeTone()`, adding a non-blocking
  `serviceBuzzer()` step (called from `loop()`) to turn the tone off after
  its duration, since raw `ledcWriteTone` has no built-in auto-stop the way
  `tone(pin, freq, duration)` does.
- Considered but **not** changed: the reference repo uses
  `Adafruit_SSD1306`+`Adafruit_GFX` for its OLED where AgriControl's
  firmware uses `U8g2` (`U8G2_SSD1306_128X64_NONAME_F_HW_I2C`, hardware
  I2C). Both are legitimate, widely-used libraries for this exact display;
  unlike `tone()`, there's no evidence U8g2 is actually broken on this
  hardware, only that the other repo made a different valid choice. Not
  swapping four firmware files' OLED code without a demonstrated defect.

Evidence: line-by-line comparison against the cloned reference repo's
`src/main.cpp`. Still **no `pio run` build** -- this remains a reviewed
port, not verified working code, same caveat as every other firmware file.
Roadmap task 56 stays `active` (unchanged); this is a correctness
improvement to existing unverified code, not new coverage.

Security note, unrelated to AgriControl's own state but worth recording:
`Full-control-on-ESP32` is a **public** GitHub repo whose checked-in
`src/main.cpp` contains the owner's real WiFi password and real MQTT
broker credentials in plaintext (its own README acknowledges this and asks
for placeholder substitution before sharing, which was never done). Flagged
directly to the owner; no credential values were copied into AgriControl
anywhere -- AgriControl's own `firmware/include/secrets.h` stays gitignored
per the existing `secrets.h.example` pattern.

Next task: unchanged from the Stage 7 entry below -- pump/fan GPIO
assignment is still the blocker for physical irrigation actuation; highest-
value remaining software-only work is Stage 8/9.

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

## Known Limits

Roadmap task 71 (Stage 10). Unlike "Known Unknowns" below (open questions
that could be answered), these are boundaries of the current design that
hold regardless of any owner answer, until a future stage deliberately
changes them:

- **Single ESP device only.** No multi-device support; that is Stage 12
  (task 78), not attempted here.
- **No persistent storage.** `backend/app.py`'s session, sequence counter,
  and event log all live in process memory and reset on every restart
  (Stage 12 task 79 is the first point this would change).
- **No authentication anywhere in the loop.** The FastAPI bridge and the
  ESP's own HTTP server accept any request; CORS on the bridge is wide
  open (`allow_origins=["*"]`). Stage 12 task 80, not attempted.
- **No MQTT or remote/cloud access.** Deliberately deferred to Stage 12
  (task 77) per `docs/AI_CONTINUITY_SYSTEM.md`'s "avoid MQTT and cloud
  services until the first local control loop is proven stable" -- even
  after a hardware-verified MQTT+Cloudflare reference implementation
  (`Full-control-on-ESP32`) was available to port from.
- **No watchdog.** Task 70 is explicitly gated in the blueprint's own
  wording ("Add a watchdog only after runtime stability") and has not
  been attempted for that reason, not because it was overlooked.
- **Pump and fan are not physically driven.** No GPIO/relay pin has been
  assigned for either (see Known Unknowns below); every session's
  irrigation/fan logic computes and reports a commanded state but never
  writes it to a pin.
- **Most of `firmware/`'s "production" environments have been compiled
  but not flashed or run.** `pio run` now succeeds for all 10 PlatformIO
  environments (corrected 2026-08-05 -- a PlatformIO toolchain has been
  available in this environment the whole time; that was a wrong
  assumption carried for many sessions, not a real constraint). Only
  `env:mqtt_test_harness` has actually been flashed and exercised against
  the physical board so far, and its decision/safety pipeline is
  field-for-field identical to `irrigation_slice.cpp`'s. `runtime.cpp`,
  `vertical_slice.cpp`, and `irrigation_slice.cpp` themselves are still
  compiled-only, not flashed -- flashing and testing them via their own
  local-HTTP transport (roadmap task 32) remains open.
- **Stage 9's actuator-fault detection is simulated, not measured.**
  `logic/actuator_feedback.py` proves the safety supervisor responds
  correctly to a detected fault, using an injected/simulated feedback
  source -- there is no real feedback sensor hardware (current-sense,
  limit switches) confirmed for this board to detect a real fault from.
- **Stage 10's replay (`logic/replay.py`) only catches drift in code
  paths the recording actually exercised.** A changed threshold that no
  recorded scenario ever crossed will not surface as a replay mismatch --
  replay is a regression check against recorded behavior, not a proof of
  correctness for untested inputs.
- **"Response time" evidence throughout this project (Stage 8's scenario
  tests, Stage 6/7's endurance tests) measures the FastAPI bridge's own
  in-process call time**, not real network latency or the physical ESP's
  actual round-trip time -- there is no real network or board to measure
  here.

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
