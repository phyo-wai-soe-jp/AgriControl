"""Stage 3 roadmap task 20: test the RC servo independently (CN3, pin D7).

Angles match the greenhouse window positions from logic/decision.py:
WINDOW_CLOSED_DEG=10, WINDOW_HALF_DEG=90, WINDOW_OPEN_DEG=170.

No RC servo model or external power source has been confirmed for CN3 yet
(see firmware/README.md, open owner questions). Do not run this unattended
until servo power stability has been verified (blueprint roadmap task 23).
"""
from machine import Pin, PWM
import time

servo = PWM(Pin(7), freq=50)


def angle_to_duty_u16(deg):
    # Typical hobby servo: 0.5ms-2.5ms pulse over a 20ms period.
    min_us, max_us = 500, 2500
    us = min_us + (max_us - min_us) * deg / 180
    return int(us / 20000 * 65535)


for deg in (10, 90, 170):
    servo.duty_u16(angle_to_duty_u16(deg))
    time.sleep_ms(1000)

servo.deinit()
