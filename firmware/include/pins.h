#pragma once

// ESP32-C3M-TRY pin map, from the owner-provided manual
// ESP32-C3M-TRY-R1-20230701.pdf (MicroFan, 2023-07-01), Table 5.2.
namespace pins {

constexpr int LED1 = 0;             // onboard blue LED, active-high
constexpr int SW1 = 2;              // tact switch 1, active-low
constexpr int SW2 = 3;              // tact switch 2, active-low
constexpr int SW3 = 6;              // tact switch 3, active-low
constexpr int SW4_BOOT_SCL = 9;     // BOOT-mode select, shared with I2C SCL;
                                     // not usable as a runtime input

constexpr int I2C_SCL = 9;          // OLED, AHT21, KXTJ3-1057
constexpr int I2C_SDA = 8;

constexpr int NEOPIXEL = 10;        // WS2812 x3, onboard
constexpr int NEOPIXEL_COUNT = 3;

constexpr int BUZZER = 21;          // piezo buzzer, drive with PWM/tone()
constexpr int LIGHT_SENSOR = 1;     // phototransistor, analog (ADC)

constexpr int CN2_PIR = 20;         // optional PIR motion sensor header
constexpr int CN3_SERVO = 7;        // optional RC servo header
constexpr int CN5_TRIG = 4;         // optional HC-SR04 ultrasonic header
constexpr int CN5_ECHO = 5;

}  // namespace pins
