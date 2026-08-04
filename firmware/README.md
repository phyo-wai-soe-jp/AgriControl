# Firmware (Stage 3 - Local physical outputs)

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
pio device monitor                    # serial output, 115200 baud
```

## Pin map (manual Table 5.2)

| Signal | Pin | Notes |
|---|---|---|
| LED1 (onboard) | D0 | active-high |
| SW1 / SW2 / SW3 | D2 / D3 / D6 | active-low |
| SW4 | D9 (shared with I2C SCL) | BOOT-mode select, not usable as a general input at runtime |
| SW5 | RST | reset |
| NeoPixel x3 | D10 | WS2812, `Adafruit_NeoPixel` |
| I2C (OLED, AHT21, KXTJ3-1057) | SCL=D9, SDA=D8 | |
| Piezo buzzer | D21 | drive with `tone()`/PWM |
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
- `src/test_buzzer.cpp` - Stage 3 task 19. Uses the Arduino-ESP32 core's
  `tone()`/`noTone()`.
- `src/test_servo.cpp` - Stage 3 task 20. Needs `ESP32Servo`. Drives the CN3
  RC servo header to the three greenhouse window angles used by
  `logic/decision.py` (`WINDOW_CLOSED_DEG=10`, `WINDOW_HALF_DEG=90`,
  `WINDOW_OPEN_DEG=170`).
- `src/test_all_outputs.cpp` - Stage 3 task 21. Combines OLED, NeoPixel, and
  buzzer on one build to check they don't interfere with each other over the
  shared I2C bus / power rail. Run only after 17-19 have individual
  hardware evidence. The servo is intentionally left out (see file header).

## Resolved this session

- Servo power stability (roadmap task 23): confirmed by direct hardware
  observation that repeatedly cycling the servo does not reset the ESP.

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
