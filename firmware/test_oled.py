"""Stage 3 roadmap task 17: test the OLED display independently.

Requires the micropython-ssd1306 library installed on the device
(Thonny -> Tools -> Manage packages -> micropython-ssd1306).
Run on-device and record the observed output as evidence in
docs/PROJECT_STATE.md before marking this task done.
"""
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

oled.fill(0)
oled.text("AgriControl", 0, 0, 1)
oled.text("OLED test", 0, 16, 1)
oled.text("Stage 3 task 17", 0, 32, 1)
oled.show()
