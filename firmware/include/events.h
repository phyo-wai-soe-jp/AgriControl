#pragma once

#include <Arduino.h>

// Structured event log (blueprint Stage 4, roadmap task 26, Branch 12).
// Fixed-capacity ring buffer -- no dynamic growth, bounded memory use.

constexpr size_t kEventLogCapacity = 32;

struct Event {
  unsigned long timestampMs = 0;
  const char* code = "";  // short machine-readable code, e.g. "DATA_STALE"
  String detail;
};

class EventLog {
 public:
  void push(unsigned long nowMs, const char* code, const String& detail) {
    Event& slot = events_[writeIndex_];
    slot.timestampMs = nowMs;
    slot.code = code;
    slot.detail = detail;
    writeIndex_ = (writeIndex_ + 1) % kEventLogCapacity;
    if (count_ < kEventLogCapacity) count_++;
  }

  size_t count() const { return count_; }

  // Returns the i-th most recent event (0 = newest). `i` must be < count().
  const Event& recent(size_t i) const {
    size_t idx = (writeIndex_ + kEventLogCapacity - 1 - i) % kEventLogCapacity;
    return events_[idx];
  }

 private:
  Event events_[kEventLogCapacity];
  size_t writeIndex_ = 0;
  size_t count_ = 0;
};
