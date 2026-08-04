# Firmware (Stage 3 - Local physical outputs; Stage 4 - ESP runtime; Stage 5 - First vertical slice; Stage 7 - Irrigation slice)

PlatformIO / Arduino C++ project for the confirmed board: **ESP32-C3M-TRY**
(MicroFan), module **ESP32-C3-MINI-1** (RISC-V, 4MB flash). Board facts and
the pin map below come from the owner-provided manual
`ESP32-C3M-TRY-R1-20230701.pdf` (MicroFan, 2023-07-01).

**Toolchain decision:** the firmware is built with **PlatformIO, Arduino
framework, C++** rather than MicroPython. This was decided by the owner
2026-08-04 after confirming the physical board already runs an
Arduino/PlatformIO test sketch (serial port `/dev/cu.usbmodem1101`). The
blueprint's roadmap task 2 originally said "Record the MicroPython version";
that task is reinterpreted as "record the firmware toolchain and version"
(see `docs/PROJECT_STATE.md`).

None of this code has been built or flashed from this environment -- there is
no PlatformIO toolchain or physical board access here. Build/upload each
environment yourself, capture the observed output (serial log, photo, or
description), and record it as evidence in `docs/PROJECT_STATE.md` before
marking the corresponding roadmap task done.

```bash
cd firmware
pio run -e main -t upload            # board bring-up (LED blink)
pio run -e test_oled -t upload        # roadmap task 17
pio run -e test_neopixel -t upload    # roadmap task 18
pio run -e test_buzzer -t upload      # roadmap task 19
pio run -e test_servo -t upload       # roadmap task 20
pio run -e test_all_outputs -t upload # roadmap task 21 (run after 17-19)
pio run -e runtime -t upload          # roadmap tasks 24-30 (needs secrets.h)
pio run -e vertical_slice -t upload   # roadmap tasks 31/33-37 (needs secrets.h)
pio run -e irrigation_slice -t upload # roadmap tasks 49-57 (needs secrets.h)
pio device monitor                    # serial output, 115200 baud
```

`env:runtime`, `env:vertical_slice`, and `env:irrigation_slice` need WiFi
credentials: copy `include/secrets.h.example` to `include/secrets.h` and
fill in real values. `secrets.h` is gitignored and must never be committed.

## Pin map (manual Table 5.2)

| Signal | Pin | Notes |
|---|---|---|
| LED1 (onboard) | D0 | active-high |
| SW1 / SW2 / SW3 | D2 / D3 / D6 | active-low |
| SW4 | D9 (shared with I2C SCL) | BOOT-mode select, not usable as a general input at runtime |
| SW5 | RST | reset |
| NeoPixel x3 | D10 | WS2812, `Adafruit_NeoPixel` |
| I2C (OLED, AHT21, KXTJ3-1057) | SCL=D9, SDA=D8 | |
| Piezo buzzer | D21 | drive via LEDC PWM (`ledcWriteTone`), not `tone()` -- see task 19 notes |
| Light sensor (phototransistor) | D1 | analog (ADC) |
| CN2 (PIR motion sensor, optional) | D20 | |
| CN3 (RC servo, optional) | D7 | |
| CN5 (HC-SR04 ultrasonic, optional) | TRIG=D4, ECHO=D5 | |

## Files

- `platformio.ini` - one environment per test file via `build_src_filter`, so
  only one `setup()`/`loop()` is linked per build. `board = esp32-c3-devkitm-1`
  is the closest chip-accurate PlatformIO board definition for the
  ESP32-C3-MINI-1 module; ESP32-C3M-TRY itself is not a registered board.
- `include/pins.h` - shared pin constants from the manual's Table 5.2.
- `src/main.cpp` - board bring-up placeholder (LED blink). The decision
  engine and safety supervisor (`logic/`, Stage 2) have not been ported to
  this firmware yet; that is later Stage 4/5 work.
- `src/test_oled.cpp` - Stage 3 task 17. Needs the `U8g2` library (declared
  in `platformio.ini`).
- `src/test_neopixel.cpp` - Stage 3 task 18. Needs `Adafruit_NeoPixel`.
- `src/test_buzzer.cpp` - Stage 3 task 19. Drives the buzzer via the LEDC
  PWM peripheral directly (`ledcWriteTone`), not the Arduino-ESP32 core's
  `tone()`/`noTone()`, which are not reliably supported on this chip --
  confirmed by github.com/phyo-wai-soe-jp/Full-control-on-ESP32, a
  separate owner-tested project on the same board.
- `src/test_servo.cpp` - Stage 3 task 20. Needs `ESP32Servo`. Drives the CN3
  RC servo header to the three greenhouse window angles used by
  `logic/decision.py` (`WINDOW_CLOSED_DEG=10`, `WINDOW_HALF_DEG=90`,
  `WINDOW_OPEN_DEG=170`).
- `src/test_all_outputs.cpp` - Stage 3 task 21. Combines OLED, NeoPixel, and
  buzzer on one build to check they don't interfere with each other over the
  shared I2C bus / power rail. Run only after 17-19 have individual
  hardware evidence. The servo is intentionally left out (see file header).
- `include/canonical.h` - `SensorId`, `SensorReading`, `SensorState` (Stage 4
  task 25, Branch 6/7). Mirrors `logic/canonical.py`'s model so host tests
  (Stage 2) and device firmware share the same shape.
- `include/system_state.h` - `Mode`/`CommunicationState` enums with an
  explicit transition graph (Stage 4 tasks 24/28), matching
  `logic/system_state.py` exactly, plus `RecoveryTracker` implementing the
  blueprint's recovery chain (Failure -> Safe state -> consecutive valid
  messages -> stable communication -> resume automatic).
- `include/events.h` - fixed-capacity ring-buffer event log (Stage 4 task
  26, Branch 12). No dynamic growth.
- `include/shared_state.h` - bundles sensors/system/recovery/events into one
  `SharedState`, with a non-blocking `tick()` that detects staleness (task
  27) and drives recovery (task 28).
- `include/secrets.h.example` - WiFi credential template; copy to
  `include/secrets.h` (gitignored) before building `env:runtime`.
- `src/runtime.cpp` - Stage 4 tasks 24/29/30: a `WebServer` on port 80
  accepting `POST /sensor`, with generic request-size and JSON/sequence
  validation (task 30). Does **not** call a decision engine or drive any
  actuator -- that wiring, plus sensor-specific range validation, is
  Stage 5 (roadmap tasks 31-40).
- `include/decision.h` - Stage 5 task 34: temperature-only decision rules,
  matching `logic/decision.py` exactly (`<=28C` fan off/window closed,
  `28-35C` fan on/window half, `>35C` fan on/window fully open).
- `include/safety.h` - firmware port of `logic/safety.py` (Stage 2 task 12),
  restricted to the fan/window outputs this slice has. Same priority order
  (Emergency > Safety > Equipment protection > Automatic) and safe-state
  matrix as the Python version. `vertical_slice.cpp` always routes the
  decision engine's output through this before touching the servo.
- `src/vertical_slice.cpp` (`env:vertical_slice`) - Stage 5 tasks
  31/33/34/35/36/37: temperature range validation, the decision engine, the
  safety supervisor, servo output, OLED display, and a full JSON response
  with commands, alarm level, and reasons. Soil moisture, tank level, and
  rain are Stage 7, not this slice, so low-tank pump protection has no pump
  to protect yet. Two safety inputs are still hardcoded placeholders, not
  real hardware signals -- read the file header before using this beyond a
  bench test:
  - `kEmergencyStopActive` -- no physical emergency-stop input assigned yet.
  - `kControllerFaultActive` -- no self-health-check exists yet to set it.
  `dataStale` and `isStartup` are real, driven by `SharedState::tick()` and
  by whether any message has ever been accepted.
- `include/irrigation.h` - Stage 7 tasks 49/51-54: extends decision.h/
  safety.h without modifying them (`vertical_slice.cpp` stays exactly as
  it was). `FullDecision`/`evaluateFullDecision` add soil-moisture +
  rain-gated pump hysteresis; `FullSafetyResult`/`evaluateFullSafety` add
  the `EQUIPMENT_PROTECTION` tier for low-tank pump protection. Same
  design decision as `logic/decision.py`: tank-level gating lives in the
  safety layer, not the decision layer.
- `src/irrigation_slice.cpp` (`env:irrigation_slice`) - Stage 7 tasks
  49-57: soil moisture / tank level / rain validation, the full decision +
  safety pipeline, a NeoPixel status color keyed to `alarm_level` (task
  56), a non-blocking buzzer tone on alarm-level changes (task 56), and an
  extended OLED page showing soil/tank/pump/fan (task 57). **Pump is
  reported, never physically driven** -- same situation as the fan in
  `vertical_slice.cpp`: no pump GPIO/relay pin has been assigned. Read the
  file header before assuming this drives real irrigation hardware.

## Resolved this session

- Servo power stability (roadmap task 23): confirmed by direct hardware
  observation that repeatedly cycling the servo does not reset the ESP.
- The safety supervisor is now wired into `vertical_slice.cpp` -- it is no
  longer true that decisions reach the servo unchecked. The remaining gap
  is narrower: two of the safety supervisor's *inputs* (emergency stop,
  controller fault) are still placeholders, not that the supervisor itself
  is missing.

## Open owner questions

These are not answered by the manual, because the manual only documents the
generic eval board, not the AgriControl greenhouse build:

1. Which RC servo model is attached to CN3? (Power source is confirmed
   stable; the model itself is still unrecorded.)
2. Which spare pins will drive the pump and fan? This board has no built-in
   pump/fan output - they are not part of the AgriControl blueprint's core
   3 sensors + fan + window + pump list matched to this eval board, so a
   relay/driver and a free GPIO need to be chosen.
3. Exact PlatformIO platform/framework/core versions in use (e.g.
   `platform-espressif32` version, Arduino-ESP32 core version) - useful to
   pin in `platformio.ini` once confirmed, for reproducible builds.
4. Real WiFi credentials for `include/secrets.h` (network name/password for
   the board to join).
5. Whether the placeholder tuning constants in `include/system_state.h`
   (`kDataStaleTimeoutMs = 10000`, `kRecoveryConsecutiveValidRequired = 5`)
   and `src/runtime.cpp`/`src/vertical_slice.cpp`
   (`kMaxRequestBodyBytes = 2048`, `-40C` to `85C` temperature range) are
   acceptable, or need different values for the real deployment.
6. Should one of the spare tact switches (SW1/SW2/SW3) be wired as a
   physical emergency-stop input for `kEmergencyStopActive` in
   `src/vertical_slice.cpp`? Currently hardcoded `false` -- no switch is
   assigned. Do not guess which switch; ask first.
7. `src/irrigation_slice.cpp`'s NeoPixel color mapping (critical=red,
   warning=yellow, startup=blue, normal=green) is an explicit
   interpretation of the manual's ambiguous "Green normal, blue automatic,
   yellow warning, red critical, purple manual" spec, not a confirmed
   rule -- does it match what's actually wanted?
8. The buzzer tone pattern on alarm changes (single tone, pitch by
   severity) is a simplification of the blueprint's "confirmation/warning
   pattern/critical pattern" description, chosen specifically to avoid
   blocking `delay()` calls in the HTTP handler -- acceptable, or is a
   real multi-beep pattern (needing an async/non-blocking beep scheduler)
   worth building?
