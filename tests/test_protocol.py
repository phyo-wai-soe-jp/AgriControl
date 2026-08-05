import unittest

from logic.decision import evaluate_decision
from logic.protocol import (
    DATA_STALE_TIMEOUT_MS,
    RECOVERY_CONSECUTIVE_VALID_REQUIRED,
    RecoveryTracker,
    SessionSequenceTracker,
    evaluate_tick,
    is_data_stale_for_safety,
    is_stale,
    is_valid_sequence,
    is_valid_temperature_c,
)
from logic.safety import SafetyPriority, evaluate_safety
from logic.system_state import CommunicationState, Mode, SystemState
from tests.helpers import make_sensors


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


class TestSessionSequenceTracker(unittest.TestCase):
    """Roadmap task 38, corrected 2026-08-06: the duplicate/out-of-order
    sequence check must be scoped per session_id, not to the device's
    entire uptime -- found broken on real hardware where a second browser
    session's sequence=1 was rejected against a prior session's history."""

    def test_first_message_of_a_session_is_always_valid(self):
        tracker = SessionSequenceTracker()
        self.assertTrue(tracker.accept("session-a", 1))

    def test_duplicate_sequence_within_a_session_is_rejected(self):
        tracker = SessionSequenceTracker()
        tracker.accept("session-a", 5)
        self.assertFalse(tracker.accept("session-a", 5))

    def test_out_of_order_lower_sequence_within_a_session_is_rejected(self):
        tracker = SessionSequenceTracker()
        tracker.accept("session-a", 5)
        self.assertFalse(tracker.accept("session-a", 3))

    def test_next_sequence_within_a_session_is_valid(self):
        tracker = SessionSequenceTracker()
        tracker.accept("session-a", 5)
        self.assertTrue(tracker.accept("session-a", 6))

    def test_new_session_id_resets_the_sequence_baseline(self):
        # The exact bug found on real hardware: a prior session reaching a
        # high sequence number must not block a new session's sequence=1.
        tracker = SessionSequenceTracker()
        tracker.accept("session-a", 100)
        self.assertTrue(tracker.accept("session-b", 1))

    def test_returning_to_an_old_session_id_does_not_replay_its_history(self):
        # Switching sessions resets the baseline; switching *back* resets
        # it again rather than restoring the old session's own history --
        # matching the firmware's single current-session baseline, not a
        # per-session-id memory bank.
        tracker = SessionSequenceTracker()
        tracker.accept("session-a", 50)
        tracker.accept("session-b", 1)
        self.assertTrue(tracker.accept("session-a", 1))


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


class TestIsDataStaleForSafety(unittest.TestCase):
    """Roadmap Gate A: 'Recovery requires stable valid messages.' Direct
    unit coverage for the exact bug found live on real hardware
    2026-08-05 -- firmware computed its safety supervisor's dataStale
    input from the raw communication state instead of this mode-based
    signal, so automatic operation resumed after 1 valid message instead
    of the required 5."""

    def test_automatic_is_not_stale(self):
        self.assertFalse(is_data_stale_for_safety(Mode.AUTOMATIC))

    def test_warning_is_stale(self):
        self.assertTrue(is_data_stale_for_safety(Mode.WARNING))

    def test_recovery_is_still_stale(self):
        # The exact case the firmware bug got wrong: RECOVERY means
        # communication is fresh again but not yet confirmed stable --
        # still not safe to resume automatic operation.
        self.assertTrue(is_data_stale_for_safety(Mode.RECOVERY))

    def test_ready_and_boot_are_not_stale(self):
        self.assertFalse(is_data_stale_for_safety(Mode.READY))
        self.assertFalse(is_data_stale_for_safety(Mode.BOOT))


class TestFullRecoveryGatingIntegration(unittest.TestCase):
    """Roadmap Gate A, full pipeline: mirrors exactly what was verified
    live on the physical board 2026-08-05 -- after a stale gap, automatic
    operation must not resume until RECOVERY_CONSECUTIVE_VALID_REQUIRED
    (5) consecutive valid messages have arrived, using is_data_stale_for_
    safety() as the corrected wiring between evaluate_tick()'s mode and
    evaluate_safety()'s data_stale input.
    """

    def _process_message(self, state, recovery, any_stale):
        """One simulated request cycle: tick() first (mirrors the ESP
        detecting staleness before a message arrives), then a decision +
        safety evaluation using the *current* mode as the safety input --
        exactly the corrected firmware wiring, not the buggy original."""
        tick_result = evaluate_tick(state, recovery, any_stale)
        state = tick_result.system_state

        sensors = make_sensors(temperature=25.0, soil_moisture=50.0, rain=0)
        decision = evaluate_decision(sensors, previous_pump_requested=False, decision_id="int")
        data_stale = is_data_stale_for_safety(state.mode)
        safety = evaluate_safety(decision, tank_level_percent=80.0, data_stale=data_stale)

        recovery.record_valid()
        return state, safety

    def test_exactly_five_messages_required_before_automatic_resumes(self):
        state = SystemState(
            mode=Mode.AUTOMATIC, communication_state=CommunicationState.DATA_ACTIVE,
            alarm_level="normal", boot_id="b1",
        )
        recovery = RecoveryTracker()

        # Message 1: staleness detected (any_stale=True) -- must NOT be automatic.
        state, safety = self._process_message(state, recovery, any_stale=True)
        self.assertEqual(safety.applied_priority, SafetyPriority.SAFETY)

        # Messages 2-5: fresh data arriving (any_stale=False from here on),
        # but still within the recovery streak -- still must NOT be automatic.
        for _ in range(RECOVERY_CONSECUTIVE_VALID_REQUIRED - 1):
            state, safety = self._process_message(state, recovery, any_stale=False)
            self.assertEqual(
                safety.applied_priority, SafetyPriority.SAFETY,
                f"resumed automatic too early, after only {recovery.consecutive_valid} valid message(s)",
            )

        # The (RECOVERY_CONSECUTIVE_VALID_REQUIRED + 1)-th message: stable
        # communication is now confirmed -- automatic operation may resume.
        state, safety = self._process_message(state, recovery, any_stale=False)
        self.assertEqual(safety.applied_priority, SafetyPriority.AUTOMATIC_OPERATION)
        self.assertEqual(state.mode, Mode.AUTOMATIC)


if __name__ == "__main__":
    unittest.main()
