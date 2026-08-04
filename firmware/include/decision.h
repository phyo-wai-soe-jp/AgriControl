#pragma once

#include <Arduino.h>

// Roadmap task 34: calculate the window command. Stage 5 first vertical
// slice -- temperature only (soil moisture, tank level, and rain arrive in
// Stage 7, not here). Mirrors logic/decision.py's temperature rules
// exactly: <=28C -> fan off, window closed; 28-35C -> fan on, window half;
// >35C -> fan on, window fully open. Does not include the safety
// supervisor -- see firmware/src/vertical_slice.cpp's file header for why
// that matters.

constexpr float kTempFanOnAboveC = 28.0f;
constexpr float kTempWindowFullAboveC = 35.0f;

constexpr int kWindowClosedDeg = 10;
constexpr int kWindowHalfDeg = 90;
constexpr int kWindowOpenDeg = 170;

struct TemperatureDecision {
  bool requestedFan;
  int requestedWindowDeg;
  const char* triggeredRule;
  String reason;
};

inline TemperatureDecision evaluateTemperatureDecision(float temperatureC) {
  TemperatureDecision d;
  if (temperatureC <= kTempFanOnAboveC) {
    d.requestedFan = false;
    d.requestedWindowDeg = kWindowClosedDeg;
    d.triggeredRule = "TEMPERATURE-001";
    d.reason = String("Temperature ") + String(temperatureC, 1) + " C is at or below " + String(kTempFanOnAboveC, 1) + " C";
  } else if (temperatureC <= kTempWindowFullAboveC) {
    d.requestedFan = true;
    d.requestedWindowDeg = kWindowHalfDeg;
    d.triggeredRule = "TEMPERATURE-002";
    d.reason = String("Temperature ") + String(temperatureC, 1) + " C is above " + String(kTempFanOnAboveC, 1) + " C";
  } else {
    d.requestedFan = true;
    d.requestedWindowDeg = kWindowOpenDeg;
    d.triggeredRule = "TEMPERATURE-003";
    d.reason = String("Temperature ") + String(temperatureC, 1) + " C is above " + String(kTempWindowFullAboveC, 1) + " C";
  }
  return d;
}
