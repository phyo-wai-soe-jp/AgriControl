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

  // Blueprint protocol rules: "New browser start creates a new session_id"
  // and "Sequence increases inside each session" -- the duplicate/
  // out-of-order check below must be scoped to session_id, not to the
  // device's whole uptime. Found broken on real hardware (2026-08-06):
  // once any message had ever been accepted, no new browser session could
  // ever send sequence=1 again without a full ESP reboot, because
  // lastSequence/haveSequence above were being reused as a lifetime
  // counter. Kept as separate fields from lastSequence/haveSequence,
  // which remain solely responsible for isStartup (the blueprint's
  // distinct "boot_id" / genuine-device-restart concept) and must not
  // reset on a session change.
  String currentSessionId;
  bool haveSessionId = false;
  unsigned long sessionLastSequence = 0;
  bool haveSessionSequence = false;

  // Returns true and records `sequence` if it is valid for `sessionId`
  // (non-empty, strictly increasing within that session); false if it is
  // a duplicate/out-of-order sequence for the current session. A
  // sessionId that differs from the one last seen starts a fresh
  // per-session sequence baseline.
  bool acceptSequence(const String& sessionId, long sequence) {
    if (!haveSessionId || sessionId != currentSessionId) {
      currentSessionId = sessionId;
      haveSessionId = true;
      haveSessionSequence = false;
    }
    if (haveSessionSequence && sequence <= static_cast<long>(sessionLastSequence)) {
      return false;
    }
    sessionLastSequence = static_cast<unsigned long>(sequence);
    haveSessionSequence = true;
    return true;
  }

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
