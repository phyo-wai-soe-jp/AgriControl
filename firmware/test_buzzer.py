"""Stage 3 roadmap task 19: test the piezo buzzer independently.

Run on-device and record the observed/heard behavior as evidence in
docs/PROJECT_STATE.md before marking this task done.
"""
from machine import Pin, PWM
import time

buzzer = PWM(Pin(21), duty=512)
buzzer.deinit()

for hz in (440, 880, 1320):
    buzzer.init(hz)
    time.sleep_ms(300)
    buzzer.deinit()
    time.sleep_ms(100)
