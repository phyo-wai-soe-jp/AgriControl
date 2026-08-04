import unittest

from logic.protocol import (
    DATA_STALE_TIMEOUT_MS,
    RECOVERY_CONSECUTIVE_VALID_REQUIRED,
    RecoveryTracker,
    evaluate_tick,
    is_stale,
    is_valid_sequence,
    is_valid_temperature_c,
)
from logic.system_state import CommunicationState, Mode, SystemState


class TestSequenceValidation(unittest.TestCase):
    """Roadmap task 38: repeated/out-of-order message rejection."""

    def test_first_message_ever_is_always_valid(self):
        self.assertTrue(is_valid_sequence(1, last_sequence=0, have_sequence=False))

    def test_duplicate_sequence_is_rejected(self):
        self.assertFalse(is_valid_sequence(5, last_sequence=5, have_sequence=True))

    def test_out_of_order_lower_sequence_is_rejected(self):
        self.assertFalse(is_valid_sequence(3, last_sequence=5, have_sequence=True))

    def test_next_sequence_is_valid(self):
        self.assertTrue(is_valid_sequence(6, last_sequence=5, have_sequence=True))

    def test_a_gap_ahead_is_still_valid(self):
        # Only non-increasing sequence numbers are rejected; skipping ahead
        # (e.g. a dropped request) is not itself an error.
        self.assertTrue(is_valid_sequence(100, last_sequence=5, have_sequence=True))


class TestTemperatureValidation(unittest.TestCase):
    """Roadmap task 39: invalid-value rejection."""

    def test_boundaries_are_inclusive(self):
        self.assertTrue(is_valid_temperature_c(-40.0))
        self.assertTrue(is_valid_temperature_c(85.0))

    def test_just_outside_boundaries_is_invalid(self):
        self.assertFalse(is_valid_temperature_c(-40.1))
        self.assertFalse(is_valid_temperature_c(85.1))

    def test_wildly_out_of_range_is_invalid(self):
        self.assertFalse(is_valid_temperature_c(999.0))

    def test_ordinary_value_is_valid(self):
        self.assertTrue(is_valid_temperature_c(25.0))


class TestStaleness(unittest.TestCase):
    """Roadmap task 27: stale-data detection."""

    def test_age_at_or_below_timeout_is_not_stale(self):
        self.assertFalse(is_stale(DATA_STALE_TIMEOUT_MS))

    def test_age_above_timeout_is_stale(self):
        self.assertTrue(is_stale(DATA_STALE_TIMEOUT_MS + 1))

    def test_custom_timeout_is_respected(self):
        self.assertFalse(is_stale(500, timeout_ms=1000))
        self.assertTrue(is_stale(1500, timeout_ms=1000))


class TestRecoveryTracker(unittest.TestCase):
    """Roadmap task 28: recovery logic."""

    def test_starts_unconfirmed(self):
        tracker = RecoveryTracker()
        self.assertFalse(tracker.stable_communication_confirmed())
        self.assertEqual(tracker.consecutive_valid, 0)

    def test_confirms_after_required_consecutive_valid_messages(self):
        tracker = RecoveryTracker()
        for _ in range(RECOVERY_CONSECUTIVE_VALID_REQUIRED - 1):
            tracker.record_valid()
            self.assertFalse(tracker.stable_communication_confirmed())
        tracker.record_valid()
        self.assertTrue(tracker.stable_communication_confirmed())

    def test_failure_resets_the_streak(self):
        tracker = RecoveryTracker()
        for _ in range(RECOVERY_CONSECUTIVE_VALID_REQUIRED - 1):
            tracker.record_valid()
        tracker.record_failure()
        self.assertEqual(tracker.consecutive_valid, 0)
        self.assertFalse(tracker.stable_communication_confirmed())

    def test_streak_does_not_exceed_the_required_count(self):
        tracker = RecoveryTracker()
        for _ in range(RECOVERY_CONSECUTIVE_VALID_REQUIRED + 10):
            tracker.record_valid()
        self.assertEqual(tracker.consecutive_valid, RECOVERY_CONSECUTIVE_VALID_REQUIRED)


class TestEvaluateTickFullRecoveryCycle(unittest.TestCase):
    """Roadmap task 40: timeout and recovery, exercised end-to-end exactly
    like firmware/include/shared_state.h's SharedState::tick() would be
    called once per loop() iteration."""

    def setUp(self):
        self.state = SystemState(
            mode=Mode.AUTOMATIC,
            communication_state=CommunicationState.DATA_ACTIVE,
            alarm_level="normal",
            boot_id="b1",
        )
        self.recovery = RecoveryTracker()

    def test_staleness_moves_automatic_to_warning_and_logs_event(self):
        result = evaluate_tick(self.state, self.recovery, any_stale=True)
        self.assertEqual(result.system_state.mode, Mode.WARNING)
        self.assertEqual(result.system_state.communication_state, CommunicationState.DATA_STALE)
        self.assertEqual(result.events, ["DATA_STALE"])
        self.assertEqual(self.recovery.consecutive_valid, 0)

    def test_repeated_stale_ticks_do_not_re_fire_the_event(self):
        first = evaluate_tick(self.state, self.recovery, any_stale=True)
        second = evaluate_tick(first.system_state, self.recovery, any_stale=True)
        self.assertEqual(second.events, [])
        self.assertEqual(second.system_state.mode, Mode.WARNING)

    def test_data_fresh_again_moves_warning_to_recovery(self):
        stale = evaluate_tick(self.state, self.recovery, any_stale=True)
        recovering = evaluate_tick(stale.system_state, self.recovery, any_stale=False)
        self.assertEqual(recovering.system_state.mode, Mode.RECOVERY)
        self.assertEqual(recovering.system_state.communication_state, CommunicationState.DATA_ACTIVE)
        self.assertEqual(recovering.events, ["RECOVERY_START"])

    def test_full_cycle_returns_to_automatic_after_enough_valid_messages(self):
        state = evaluate_tick(self.state, self.recovery, any_stale=True).system_state
        state = evaluate_tick(state, self.recovery, any_stale=False).system_state
        self.assertEqual(state.mode, Mode.RECOVERY)

        # Simulate consecutive valid messages arriving (recovery.record_valid()
        # is called by the request handler, not by tick() itself).
        for _ in range(RECOVERY_CONSECUTIVE_VALID_REQUIRED - 1):
            self.recovery.record_valid()
            still_recovering = evaluate_tick(state, self.recovery, any_stale=False)
            self.assertEqual(still_recovering.system_state.mode, Mode.RECOVERY)
            self.assertEqual(still_recovering.events, [])

        self.recovery.record_valid()
        final = evaluate_tick(state, self.recovery, any_stale=False)
        self.assertEqual(final.system_state.mode, Mode.AUTOMATIC)
        self.assertEqual(final.events, ["RECOVERED"])

    def test_stale_again_during_recovery_resets_the_streak(self):
        state = evaluate_tick(self.state, self.recovery, any_stale=True).system_state
        state = evaluate_tick(state, self.recovery, any_stale=False).system_state
        self.recovery.record_valid()
        self.recovery.record_valid()
        self.assertEqual(self.recovery.consecutive_valid, 2)

        # Data goes stale again mid-recovery -- back to WARNING, streak reset.
        state = SystemState(mode=Mode.RECOVERY, communication_state=CommunicationState.DATA_ACTIVE,
                             alarm_level="warning", boot_id="b1")
        # RECOVERY -> WARNING is not a defined transition in the mode graph
        # (only AUTOMATIC -> WARNING/SAFE/FAULT is); evaluate_tick only
        # transitions out of AUTOMATIC on staleness, matching the C++
        # original exactly, so recovery-time staleness is only visible via
        # the communication_state flip and the reset streak, not a mode
        # change back to WARNING.
        result = evaluate_tick(state, self.recovery, any_stale=True)
        self.assertEqual(result.system_state.communication_state, CommunicationState.DATA_STALE)
        self.assertEqual(self.recovery.consecutive_valid, 0)


if __name__ == "__main__":
    unittest.main()
