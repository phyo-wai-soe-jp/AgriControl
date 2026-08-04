#pragma once

#include <Arduino.h>

#include "decision.h"
#include "safety.h"

// Stage 7 roadmap tasks 49-54: irrigation slice (soil moisture, tank
// level, rain, pump hysteresis, low-tank protection, rain protection).
// Extends decision.h/safety.h's temperature-only logic without modifying
// them -- vertical_slice.cpp (Stage 5) stays exactly as it was. Mirrors
// logic/decision.py and logic/safety.py exactly, including the same
// design decision documented in logic/decision.py: tank-level gating is
// enforced in the safety layer (evaluateFullSafety), not the decision
// layer (evaluateFullDecision), because the blueprint's own worked
// conflict example ("Decision engine: dry soil -> pump ON. Safety
// supervisor: tank below 15% -> pump OFF.") only makes sense that way.

constexpr float kMoisturePumpOnBelow = 30.0f;
constexpr float kMoisturePumpOffAbove = 40.0f;
constexpr float kLowTankThresholdPercent = 15.0f;

struct FullDecision {
  // Temperature outputs (same rules as decision.h).
  bool requestedFan;
  int requestedWindowDeg;
  const char* temperatureRule;
  String temperatureReason;

  // Irrigation outputs (Stage 7).
  bool requestedPump;
  const char* irrigationRule;
  String irrigationReason;
};

// Roadmap task 52: pump hysteresis needs the previous requested pump
// state -- the caller (irrigation_slice.cpp) is responsible for
// persisting `previousPumpRequested` across messages, the same way
// logic/decision.py's caller does on the host.
inline FullDecision evaluateFullDecision(
    float temperatureC, bool hasMoisture, float moisturePercent, bool hasRain, float rainValue,
    bool previousPumpRequested) {
  FullDecision d;

  if (temperatureC <= kTempFanOnAboveC) {
    d.requestedFan = false;
    d.requestedWindowDeg = kWindowClosedDeg;
    d.temperatureRule = "TEMPERATURE-001";
    d.temperatureReason =
        String("Temperature ") + String(temperatureC, 1) + " C is at or below " + String(kTempFanOnAboveC, 1) + " C";
  } else if (temperatureC <= kTempWindowFullAboveC) {
    d.requestedFan = true;
    d.requestedWindowDeg = kWindowHalfDeg;
    d.temperatureRule = "TEMPERATURE-002";
    d.temperatureReason =
        String("Temperature ") + String(temperatureC, 1) + " C is above " + String(kTempFanOnAboveC, 1) + " C";
  } else {
    d.requestedFan = true;
    d.requestedWindowDeg = kWindowOpenDeg;
    d.temperatureRule = "TEMPERATURE-003";
    d.temperatureReason = String("Temperature ") + String(temperatureC, 1) + " C is above " +
                           String(kTempWindowFullAboveC, 1) + " C";
  }

  // Roadmap tasks 49/51/52: soil moisture + rain -> pump, with hysteresis.
  // Tank level is deliberately NOT checked here -- see file header.
  if (!hasMoisture || !hasRain) {
    d.requestedPump = previousPumpRequested;
    d.irrigationRule = "IRRIGATION-HOLD";
    d.irrigationReason = "Soil moisture or rain reading unavailable; holding previous pump state";
  } else if (moisturePercent < kMoisturePumpOnBelow && rainValue == 0.0f) {
    d.requestedPump = true;
    d.irrigationRule = "IRRIGATION-001";
    d.irrigationReason =
        String("Soil moisture ") + String(moisturePercent, 1) + "% is below " + String(kMoisturePumpOnBelow, 1) +
        "% and no rain is detected";
  } else if (moisturePercent > kMoisturePumpOffAbove) {
    d.requestedPump = false;
    d.irrigationRule = "IRRIGATION-002";
    d.irrigationReason =
        String("Soil moisture ") + String(moisturePercent, 1) + "% is above " + String(kMoisturePumpOffAbove, 1) + "%";
  } else {
    d.requestedPump = previousPumpRequested;
    d.irrigationRule = "IRRIGATION-003";
    d.irrigationReason = String("Soil moisture ") + String(moisturePercent, 1) + "% is between " +
                          String(kMoisturePumpOnBelow, 1) + "% and " + String(kMoisturePumpOffAbove, 1) +
                          "%; holding previous pump state";
  }

  return d;
}

struct FullSafetyResult {
  bool commandedFan;
  int commandedWindowDeg;
  bool commandedPump;
  const char* alarmLevel;
  SafetyPriority appliedPriority;
  const char* overrideCode;  // nullptr if no override applied
};

// Roadmap tasks 53/54: low-tank and rain protection. Rain protection is
// already covered inside evaluateFullDecision (no-rain is part of the
// pump-on condition itself, matching logic/decision.py); low-tank
// protection is enforced here, at Equipment protection priority, exactly
// like logic/safety.py's evaluate_safety.
inline FullSafetyResult evaluateFullSafety(
    const FullDecision& decision, bool hasTankLevel, float tankLevelPercent, bool emergencyStop,
    bool controllerFault, bool dataStale, bool isStartup, bool configuredSafeFanState) {
  if (emergencyStop) {
    return FullSafetyResult{
        false, kSafeWindowDeg, false, "critical", SafetyPriority::EMERGENCY, "EMERGENCY-STOP"};
  }
  if (controllerFault) {
    return FullSafetyResult{
        configuredSafeFanState, kSafeWindowDeg, false, "critical", SafetyPriority::SAFETY, "CONTROLLER-FAULT"};
  }
  if (dataStale) {
    return FullSafetyResult{
        configuredSafeFanState, kSafeWindowDeg, false, "warning", SafetyPriority::SAFETY, "DATA-STALE"};
  }
  if (isStartup) {
    return FullSafetyResult{
        false, kWindowClosedDeg, false, "startup_indication", SafetyPriority::SAFETY, "STARTUP"};
  }
  if (hasTankLevel && tankLevelPercent < kLowTankThresholdPercent) {
    return FullSafetyResult{
        decision.requestedFan,
        decision.requestedWindowDeg,
        false,
        "warning",
        SafetyPriority::EQUIPMENT_PROTECTION,
        decision.requestedPump ? "LOW-TANK" : nullptr};
  }
  return FullSafetyResult{
      decision.requestedFan,
      decision.requestedWindowDeg,
      decision.requestedPump,
      "normal",
      SafetyPriority::AUTOMATIC_OPERATION,
      nullptr};
}
