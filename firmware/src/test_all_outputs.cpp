// Stage 3 roadmap task 21: test all outputs together (env:test_all_outputs).
//
// Build/upload with: pio run -e test_all_outputs -t upload
// Run only after tasks 17-19 (OLED, NeoPixel, buzzer) have individual
// hardware evidence recorded in docs/PROJECT_STATE.md -- this combines them
// to check they don't interfere with each other (shared I2C bus, shared
// power rail), not to substitute for the individual tests.
//
// The servo (CN3) is deliberately left out of this combined loop: it is
// already confirmed independently (roadmap tasks 20/23), and combining it
// with the other three at once was not part of what was hardware-verified
// for power stability.
#include <Arduino.h>
#include <U8g2lib.h>
#include <Wire.h>
#include <Adafruit_NeoPixel.h>

#include "pins.h"

U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);
Adafruit_NeoPixel rgb(pins::NEOPIXEL_COUNT, pins::NEOPIXEL, NEO_GRB + NEO_KHZ800);

// LEDC-backed buzzer drive, not tone()/noTone() -- see test_buzzer.cpp for
// why.
namespace {
constexpr int kBuzzerChannel = 5;
constexpr int kBuzzerPwmResolutionBits = 10;
}  // namespace

void setup() {
  Wire.begin(pins::I2C_SDA, pins::I2C_SCL);
  u8g2.begin();
  rgb.begin();
  ledcSetup(kBuzzerChannel, 1000, kBuzzerPwmResolutionBits);
  ledcAttachPin(pins::BUZZER, kBuzzerChannel);

  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_6x10_tf);
  u8g2.drawStr(0, 12, "AgriControl");
  u8g2.drawStr(0, 26, "All-outputs test");
  u8g2.drawStr(0, 40, "Stage 3 task 21");
  u8g2.sendBuffer();
}

void loop() {
  for (int i = 0; i < pins::NEOPIXEL_COUNT; i++) {
    rgb.setPixelColor(i, rgb.Color(0, 30, 0));
  }
  rgb.show();
  ledcWriteTone(kBuzzerChannel, 880);
  delay(150);
  ledcWriteTone(kBuzzerChannel, 0);
  delay(850);

  for (int i = 0; i < pins::NEOPIXEL_COUNT; i++) {
    rgb.setPixelColor(i, 0);
  }
  rgb.show();
  delay(1000);
}
