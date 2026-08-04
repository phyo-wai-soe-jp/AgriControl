#pragma once

#include <Arduino.h>

#include "decision.h"

// Firmware port of logic/safety.py (Stage 2 roadmap task 12) for the
// Stage 5 temperature-only vertical slice. Mirrors the Python priority
// order (Emergency > Safety > Equipment protection > Automatic operation)
// and safe-state matrix exactly, restricted to the fan/window outputs
// this slice actually has. Pump/irrigation safety (low-tank protection)
// is real in logic/safety.py but has no equivalent here yet -- there is no
// pump and no tank-level sensor until Stage 7. EQUIPMENT_PROTECTION is
// kept in the enum for parity with the Python source; nothing in this
// file currently returns it.
//
// Only narrows/overrides the decision engine's output -- never
// recomputes requested values, same rule as the Python version.

enum class SafetyPriority : uint8_t {
  EMERGENCY,
  SAFETY,
  EQUIPMENT_PROTECTION,
  AUTOMATIC_OPERATION
};

// The blueprint documents a "safe angle" for stale/fault/emergency states
// without giving a numeric value; closed matches the documented startup
// default -- the same choice logic/safety.py makes.
constexpr int kSafeWindowDeg = kWindowClosedDeg;

struct SafetyResult {
  bool commandedFan;
  int commandedWindowDeg;
  const char* alarmLevel;
  SafetyPriority appliedPriority;
  const char* overrideCode;  // nullptr if no override applied
};

inline SafetyResult evaluateSafety(
    const TemperatureDecision& decision,
    bool emergencyStop,
    bool controllerFault,
    bool dataStale,
    bool isStartup,
    bool configuredSafeFanState) {
  if (emergencyStop) {
    return SafetyResult{false, kSafeWindowDeg, "critical", SafetyPriority::EMERGENCY, "EMERGENCY-STOP"};
  }
  if (controllerFault) {
    return SafetyResult{configuredSafeFanState, kSafeWindowDeg, "critical", SafetyPriority::SAFETY, "CONTROLLER-FAULT"};
  }
  if (dataStale) {
    return SafetyResult{configuredSafeFanState, kSafeWindowDeg, "warning", SafetyPriority::SAFETY, "DATA-STALE"};
  }
  if (isStartup) {
    return SafetyResult{false, kWindowClosedDeg, "startup_indication", SafetyPriority::SAFETY, "STARTUP"};
  }
  return SafetyResult{
      decision.requestedFan, decision.requestedWindowDeg, "normal", SafetyPriority::AUTOMATIC_OPERATION, nullptr};
}
