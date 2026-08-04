// Stage 3 roadmap task 20: test the RC servo independently (CN3, pin D7,
// env:test_servo).
//
// Build/upload with: pio run -e test_servo -t upload
// Angles match the greenhouse window positions from logic/decision.py:
// WINDOW_CLOSED_DEG=10, WINDOW_HALF_DEG=90, WINDOW_OPEN_DEG=170.
//
// Servo power stability (roadmap task 23) was confirmed by direct
// observation: cycling the servo repeatedly did not reset the ESP. Record
// any further servo model/power source facts in
// data/agent-coordination.json before relying on this for continuous use.
#include <Arduino.h>
#include <ESP32Servo.h>

#include "pins.h"

Servo windowServo;

void setup() {
  windowServo.attach(pins::CN3_SERVO);
}

void loop() {
  const int angles[] = {10, 90, 170};
  for (int deg : angles) {
    windowServo.write(deg);
    delay(1000);
  }
}
