// Board bring-up placeholder for the ESP32-C3M-TRY (env:main).
//
// Blinks the onboard LED so a fresh flash is visibly alive. The actual
// decision engine and safety supervisor live in logic/ (host-runnable
// Python, Stage 2) and have not yet been ported to this firmware -- that
// port is later Stage 4/5 work, not this placeholder.
#include <Arduino.h>

#include "pins.h"

void setup() {
  pinMode(pins::LED1, OUTPUT);
}

void loop() {
  digitalWrite(pins::LED1, HIGH);
  delay(1000);
  digitalWrite(pins::LED1, LOW);
  delay(1000);
}
