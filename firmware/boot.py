"""ESP32-C3M-TRY board pin initialization.

Pin assignments per the owner-provided manual ESP32-C3M-TRY-R1-20230701.pdf
(MicroFan, 2023-07-01), Table 5.2. Runs once on device boot.
"""
from machine import Pin, I2C

i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)  # OLED, AHT21, KXTJ3-1057

led1 = Pin(0, Pin.OUT)  # onboard blue LED
sw1 = Pin(2, Pin.IN)  # tact switch 1, active-low
sw2 = Pin(3, Pin.IN)  # tact switch 2, active-low
sw3 = Pin(6, Pin.IN)  # tact switch 3, active-low
