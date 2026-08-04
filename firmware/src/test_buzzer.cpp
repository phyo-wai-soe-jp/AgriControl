// Stage 3 roadmap task 19: test the piezo buzzer independently
// (env:test_buzzer).
//
// Build/upload with: pio run -e test_buzzer -t upload
// Drives the buzzer through the LEDC PWM peripheral directly rather than
// the Arduino core's tone()/noTone(), which are not reliably supported on
// the ESP32 (particularly its RISC-V parts, like the C3 this board uses).
// Confirmed working on this exact board by the owner's separate
// github.com/phyo-wai-soe-jp/Full-control-on-ESP32 project. Record the
// observed/heard behavior as evidence in docs/PROJECT_STATE.md before
// marking this task done.
#include <Arduino.h>

#include "pins.h"

namespace {
constexpr int kBuzzerChannel = 5;
constexpr int kBuzzerPwmResolutionBits = 10;
}  // namespace

void setup() {
  ledcSetup(kBuzzerChannel, 1000, kBuzzerPwmResolutionBits);
  ledcAttachPin(pins::BUZZER, kBuzzerChannel);
}

void loop() {
  const int frequencies[] = {440, 880, 1320};
  for (int hz : frequencies) {
    ledcWriteTone(kBuzzerChannel, hz);
    delay(300);
    ledcWriteTone(kBuzzerChannel, 0);
    delay(100);
  }
  delay(1000);
}
