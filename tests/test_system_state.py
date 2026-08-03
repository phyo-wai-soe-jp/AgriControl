import unittest

from logic.system_state import CommunicationState, InvalidModeTransition, Mode, SystemState


class TestSystemStateTransitions(unittest.TestCase):
    def make_state(self, mode):
        return SystemState(
            mode=mode,
            communication_state=CommunicationState.ONLINE,
            alarm_level="normal",
            boot_id="boot-1",
        )

    def test_valid_transition_chain(self):
        state = self.make_state(Mode.BOOT)
        state = state.transition_to(Mode.CONNECTING)
        state = state.transition_to(Mode.READY)
        state = state.transition_to(Mode.AUTOMATIC)
        state = state.transition_to(Mode.WARNING)
        state = state.transition_to(Mode.RECOVERY)
        state = state.transition_to(Mode.AUTOMATIC)
        self.assertEqual(state.mode, Mode.AUTOMATIC)

    def test_invalid_transition_raises(self):
        state = self.make_state(Mode.BOOT)
        with self.assertRaises(InvalidModeTransition):
            state.transition_to(Mode.AUTOMATIC)

    def test_lateral_transition_between_warning_and_safe_is_invalid(self):
        state = self.make_state(Mode.WARNING)
        with self.assertRaises(InvalidModeTransition):
            state.transition_to(Mode.SAFE)

    def test_same_state_transition_is_noop(self):
        state = self.make_state(Mode.AUTOMATIC)
        state = state.transition_to(Mode.AUTOMATIC)
        self.assertEqual(state.mode, Mode.AUTOMATIC)


if __name__ == "__main__":
    unittest.main()
