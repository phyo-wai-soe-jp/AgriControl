// Stage 3 roadmap task 18: test the onboard NeoPixel (WS2812) LEDs
// independently (env:test_neopixel).
//
// Build/upload with: pio run -e test_neopixel -t upload
// Record the observed colors as evidence in docs/PROJECT_STATE.md before
// marking this task done.
#include <Arduino.h>
#include <Adafruit_NeoPixel.h>

#include "pins.h"

Adafruit_NeoPixel rgb(pins::NEOPIXEL_COUNT, pins::NEOPIXEL, NEO_GRB + NEO_KHZ800);

void setup() {
  rgb.begin();
}

void loop() {
  const uint32_t colors[] = {
      rgb.Color(50, 0, 0),  // red
      rgb.Color(0, 50, 0),  // green
      rgb.Color(0, 0, 50),  // blue
  };
  for (uint32_t color : colors) {
    for (int i = 0; i < pins::NEOPIXEL_COUNT; i++) {
      rgb.setPixelColor(i, color);
    }
    rgb.show();
    delay(1000);
  }
}
