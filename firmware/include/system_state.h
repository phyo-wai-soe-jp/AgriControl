#pragma once

#include <Arduino.h>

// System state machine (blueprint Stage 4, roadmap tasks 24/28, Branch 7).
// Mirrors logic/system_state.py's Mode transition graph exactly, plus a
// RecoveryTracker implementing the blueprint's recovery chain:
// Failure -> Safe state -> Several consecutive valid messages ->
// Stable communication confirmed -> Clear fault -> Resume automatic
// operation.

enum class Mode : uint8_t {
  BOOT = 0,
  CONNECTING,
  READY,
  AUTOMATIC,
  WARNING,
  SAFE,
  FAULT,
  RECOVERY
};

enum class CommunicationState : uint8_t {
  OFFLINE = 0,
  CONNECTING,
  ONLINE,
  DATA_ACTIVE,
  DATA_STALE,
  RECONNECTING
};

// Consecutive valid messages required before recovery completes and the
// system returns to AUTOMATIC. Tunable runtime parameter, not a hardware
// fact -- confirm/adjust with the owner before relying on it.
constexpr int kRecoveryConsecutiveValidRequired = 5;

// Data-staleness timeout. Also a tunable runtime parameter, not a hardware
// fact -- confirm/adjust with the owner. 10s is a conservative placeholder.
constexpr unsigned long kDataStaleTimeoutMs = 10000;

class SystemState {
 public:
  Mode mode() const { return mode_; }
  CommunicationState communicationState() const { return commState_; }

  // Returns false (and leaves mode unchanged) if the transition is not part
  // of the defined graph -- exactly the chain documented in the blueprint:
  // BOOT -> CONNECTING -> READY -> AUTOMATIC -> WARNING/SAFE/FAULT ->
  // RECOVERY -> AUTOMATIC. FAULT/SAFE are not yet driven by this Stage 4
  // runtime (no safety supervisor is wired in here); that lands in Stage 5.
  bool transitionTo(Mode next) {
    if (next == mode_) return true;
    if (!isAllowed(mode_, next)) return false;
    mode_ = next;
    return true;
  }

  void setCommunicationState(CommunicationState state) { commState_ = state; }

 private:
  static bool isAllowed(Mode from, Mode to) {
    switch (from) {
      case Mode::BOOT:
        return to == Mode::CONNECTING;
      case Mode::CONNECTING:
        return to == Mode::READY;
      case Mode::READY:
        return to == Mode::AUTOMATIC;
      case Mode::AUTOMATIC:
        return to == Mode::WARNING || to == Mode::SAFE || to == Mode::FAULT;
      case Mode::WARNING:
        return to == Mode::RECOVERY;
      case Mode::SAFE:
        return to == Mode::RECOVERY;
      case Mode::FAULT:
        return to == Mode::RECOVERY;
      case Mode::RECOVERY:
        return to == Mode::AUTOMATIC;
    }
    return false;
  }

  Mode mode_ = Mode::BOOT;
  CommunicationState commState_ = CommunicationState::OFFLINE;
};

// Roadmap task 28: recovery logic. Call recordValid()/recordFailure() as
// messages are validated; stableCommunicationConfirmed() reports whether
// enough consecutive valid messages have arrived to leave RECOVERY.
class RecoveryTracker {
 public:
  void recordFailure() { consecutiveValid_ = 0; }

  void recordValid() {
    if (consecutiveValid_ < kRecoveryConsecutiveValidRequired) {
      consecutiveValid_++;
    }
  }

  bool stableCommunicationConfirmed() const {
    return consecutiveValid_ >= kRecoveryConsecutiveValidRequired;
  }

  int consecutiveValid() const { return consecutiveValid_; }

 private:
  int consecutiveValid_ = 0;
};
