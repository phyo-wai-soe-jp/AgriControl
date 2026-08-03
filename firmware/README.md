# Firmware (Stage 3 - Local physical outputs)

MicroPython source for the confirmed board: **ESP32-C3M-TRY** (MicroFan),
using the **ESP32-C3-MINI-1** module (RISC-V, 4MB flash). Board facts and the
pin map below come from the owner-provided manual
`ESP32-C3M-TRY-R1-20230701.pdf` (MicroFan, 2023-07-01).

This code is written for the physical board and cannot be verified from this
environment. Run each script on the device with Thonny, capture the observed
output (serial log, photo, or description), and record it as evidence in
`docs/PROJECT_STATE.md` before marking the corresponding roadmap task done.

## Pin map (manual Table 5.2)

| Signal | Pin | Notes |
|---|---|---|
| LED1 (onboard) | D0 | active-high |
| SW1 / SW2 / SW3 | D2 / D3 / D6 | active-low |
| SW4 | D9 (shared with I2C SCL) | BOOT-mode select, not usable as a general input at runtime |
| SW5 | RST | reset |
| NeoPixel x3 | D10 | WS2812, `neopixel` module |
| I2C (OLED, AHT21, KXTJ3-1057) | SCL=D9, SDA=D8 | |
| Piezo buzzer | D21 | drive with PWM |
| Light sensor (phototransistor) | D1 | analog (ADC) |
| CN2 (PIR motion sensor, optional) | D20 | |
| CN3 (RC servo, optional) | D7 | |
| CN5 (HC-SR04 ultrasonic, optional) | TRIG=D4, ECHO=D5 | |

## Files

- `boot.py` - board pin initialization, mirrors the manual's example.
- `test_oled.py` - Stage 3 task 17. Requires the `ssd1306` library (Thonny ->
  Tools -> Manage packages -> `micropython-ssd1306`).
- `test_neopixel.py` - Stage 3 task 18. Uses the built-in `neopixel` module.
- `test_buzzer.py` - Stage 3 task 19. Uses `machine.PWM`.
- `test_servo.py` - Stage 3 task 20. Drives the CN3 RC servo to the three
  greenhouse window angles used by `logic/decision.py`
  (`WINDOW_CLOSED_DEG=10`, `WINDOW_HALF_DEG=90`, `WINDOW_OPEN_DEG=170`).

## Open owner questions before Stage 3 can be marked done

These are not answered by the manual, because the manual only documents the
generic eval board, not the AgriControl greenhouse build:

1. Which RC servo model is attached to CN3, and is it powered separately from
   the USB 5V rail? (Blueprint task 23 - servo power must not reset the ESP.)
2. Which spare pins will drive the pump and fan? This board has no built-in
   pump/fan output - they are not part of the AgriControl blueprint's core
   3 sensors + fan + window + pump list matched to this eval board, so a
   relay/driver and a free GPIO need to be chosen.
3. Confirm the MicroPython version actually flashed on the physical unit
   (`import sys; print(sys.implementation)` in the Thonny REPL) - the
   manual's `v1.20.0` is only the version available when the manual was
   written (2023-07), not necessarily what is on this board today.
