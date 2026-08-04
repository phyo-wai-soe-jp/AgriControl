// Stage 3 roadmap task 17: test the OLED display independently (env:test_oled).
//
// Build/upload with: pio run -e test_oled -t upload
// Record the observed output as evidence in docs/PROJECT_STATE.md before
// marking this task done.
#include <Arduino.h>
#include <U8g2lib.h>
#include <Wire.h>

#include "pins.h"

U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);

void setup() {
  Wire.begin(pins::I2C_SDA, pins::I2C_SCL);
  u8g2.begin();
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_6x10_tf);
  u8g2.drawStr(0, 12, "AgriControl");
  u8g2.drawStr(0, 26, "OLED test");
  u8g2.drawStr(0, 40, "Stage 3 task 17");
  u8g2.sendBuffer();
}

void loop() {}
