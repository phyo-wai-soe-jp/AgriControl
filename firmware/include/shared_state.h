#pragma once

#include "canonical.h"
#include "events.h"
#include "system_state.h"

// Bundles the runtime's authoritative state (blueprint Stage 4, roadmap
// task 25: shared state management). One instance lives for the lifetime
// of the firmware; the HTTP handler and the periodic tick() both operate
// on it. No decision engine or actuator wiring here -- that is Stage 5.
struct SharedState {
  SensorState sensors;
  SystemState system;
  RecoveryTracker recovery;
  EventLog events;

  unsigned long lastSequence = 0;
  bool haveSequence = false;

  // Call once per loop() iteration. Detects staleness across all sensors
  // and advances recovery/mode transitions. Never blocks.
  void tick(unsigned long nowMs) {
    bool anyStale = false;
    for (uint8_t i = 0; i < static_cast<uint8_t>(SensorId::COUNT); i++) {
      SensorId id = static_cast<SensorId>(i);
      if (sensors.hasReading(id) && sensors.isStale(id, nowMs, kDataStaleTimeoutMs)) {
        anyStale = true;
      }
    }

    if (anyStale) {
      if (system.communicationState() != CommunicationState::DATA_STALE) {
        system.setCommunicationState(CommunicationState::DATA_STALE);
        events.push(nowMs, "DATA_STALE", "One or more sensor readings exceeded the staleness timeout");
        recovery.recordFailure();
        if (system.mode() == Mode::AUTOMATIC) {
          system.transitionTo(Mode::WARNING);
        }
      }
    } else if (system.communicationState() == CommunicationState::DATA_STALE) {
      system.setCommunicationState(CommunicationState::DATA_ACTIVE);
      if (system.mode() == Mode::WARNING) {
        system.transitionTo(Mode::RECOVERY);
        events.push(nowMs, "RECOVERY_START", "Data fresh again, entering recovery");
      }
    }

    if (system.mode() == Mode::RECOVERY && recovery.stableCommunicationConfirmed()) {
      events.push(nowMs, "RECOVERED", "Stable communication confirmed, resuming automatic operation");
      system.transitionTo(Mode::AUTOMATIC);
    }
  }
};
