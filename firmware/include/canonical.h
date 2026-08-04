#pragma once

#include <Arduino.h>

// Canonical sensor state (blueprint Stage 4, roadmap task 25, Branch 6/7).
// Mirrors logic/canonical.py's SensorReading/SensorState so the same
// sensor model is used on the host (Stage 2 tests) and on the device.

enum class SensorId : uint8_t {
  TEMPERATURE = 0,
  SOIL_MOISTURE,
  RAIN,
  WATER_LEVEL_PERCENT,
  COUNT
};

struct SensorReading {
  float value = 0.0f;
  bool valid = false;
  unsigned long receivedAtMs = 0;
};

class SensorState {
 public:
  void update(SensorId id, float value, unsigned long nowMs) {
    SensorReading& reading = readings_[index(id)];
    reading.value = value;
    reading.valid = true;
    reading.receivedAtMs = nowMs;
  }

  void invalidate(SensorId id) { readings_[index(id)].valid = false; }

  bool hasReading(SensorId id) const { return readings_[index(id)].valid; }

  bool valueOf(SensorId id, float* outValue) const {
    const SensorReading& reading = readings_[index(id)];
    if (!reading.valid) return false;
    *outValue = reading.value;
    return true;
  }

  unsigned long ageMs(SensorId id, unsigned long nowMs) const {
    const SensorReading& reading = readings_[index(id)];
    if (nowMs < reading.receivedAtMs) return 0;
    return nowMs - reading.receivedAtMs;
  }

  // Roadmap task 27: stale-data detection. `timeoutMs` is a tunable
  // runtime parameter, not a hardware fact -- see kDataStaleTimeoutMs in
  // system_state.h for the current default and rationale.
  bool isStale(SensorId id, unsigned long nowMs, unsigned long timeoutMs) const {
    const SensorReading& reading = readings_[index(id)];
    if (!reading.valid) return true;
    return ageMs(id, nowMs) > timeoutMs;
  }

 private:
  static size_t index(SensorId id) { return static_cast<size_t>(id); }

  SensorReading readings_[static_cast<size_t>(SensorId::COUNT)];
};
