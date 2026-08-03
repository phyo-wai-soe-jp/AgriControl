"""Stage 3 roadmap task 18: test the NeoPixel (WS2812) color LEDs independently.

Run on-device and record the observed colors as evidence in
docs/PROJECT_STATE.md before marking this task done.
"""
from machine import Pin
from neopixel import NeoPixel
import time

rgb = NeoPixel(Pin(10, Pin.OUT), 3)

for color in ((50, 0, 0), (0, 50, 0), (0, 0, 50)):  # red, green, blue
    for i in range(3):
        rgb[i] = color
    rgb.write()
    time.sleep_ms(1000)

rgb.fill((0, 0, 0))
rgb.write()
