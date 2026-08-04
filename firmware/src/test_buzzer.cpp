// Stage 3 roadmap task 19: test the piezo buzzer independently
// (env:test_buzzer).
//
// Build/upload with: pio run -e test_buzzer -t upload
// Uses the Arduino-ESP32 core's tone()/noTone() (LEDC-backed). Record the
// observed/heard behavior as evidence in docs/PROJECT_STATE.md before
// marking this task done.
#include <Arduino.h>

#include "pins.h"

void setup() {
  pinMode(pins::BUZZER, OUTPUT);
}

void loop() {
  const int frequencies[] = {440, 880, 1320};
  for (int hz : frequencies) {
    tone(pins::BUZZER, hz, 300);
    delay(400);
  }
  delay(1000);
}
