import unittest

from logic.actuator_feedback import (
    FaultMode,
    detect_mismatch,
    simulate_binary_actuator,
    simulate_servo_actuator,
    to_actuator_state,
)
from logic.decision import evaluate_decision
from logic.safety import SafetyPriority, evaluate_safety
from tests.helpers import make_sensors


class TestBinaryActuatorStartupDelay(unittest.TestCase):
    """Roadmap task 62: startup delays."""

    def test_on_command_reports_off_before_startup_delay_elapses(self):
        feedback = simulate_binary_actuator(True, elapsed_since_command_ms=100)
        self.assertFalse(feedback.measured_state)
        self.assertIsNone(feedback.fault_code)  # still starting up, not yet a fault

    def test_on_command_reports_on_after_startup_delay_elapses(self):
        feedback = simulate_binary_actuator(True, elapsed_since_command_ms=600)
        self.assertTrue(feedback.measured_state)
        self.assertIsNone(feedback.fault_code)

    def test_off_command_reports_immediately_no_delay(self):
        feedback = simulate_binary_actuator(False, elapsed_since_command_ms=0)
        self.assertFalse(feedback.measured_state)
        self.assertIsNone(feedback.fault_code)

    def test_custom_startup_delay_is_respected(self):
        feedback = simulate_binary_actuator(True, elapsed_since_command_ms=50, startup_delay_ms=1000)
        self.assertFalse(feedback.measured_state)
        feedback = simulate_binary_actuator(True, elapsed_since_command_ms=1001, startup_delay_ms=1000)
        self.assertTrue(feedback.measured_state)


class TestBinaryActuatorFailedStartup(unittest.TestCase):
    """Roadmap task 63: failed startup."""

    def test_on_command_never_succeeds_and_faults(self):
        feedback = simulate_binary_actuator(True, elapsed_since_command_ms=99999, fault_mode=FaultMode.FAILED_STARTUP)
        self.assertFalse(feedback.measured_state)
        self.assertEqual(feedback.fault_code, "ACTUATOR-FAILED-STARTUP")

    def test_off_command_still_succeeds_without_fault(self):
        feedback = simulate_binary_actuator(False, elapsed_since_command_ms=0, fault_mode=FaultMode.FAILED_STARTUP)
        self.assertFalse(feedback.measured_state)
        self.assertIsNone(feedback.fault_code)


class TestBinaryActuatorStuckFaults(unittest.TestCase):
    """Roadmap task 64: stuck-on and stuck-off faults."""

    def test_stuck_on_matches_an_on_command_without_fault(self):
        feedback = simulate_binary_actuator(True, elapsed_since_command_ms=99999, fault_mode=FaultMode.STUCK_ON)
        self.assertTrue(feedback.measured_state)
        self.assertIsNone(feedback.fault_code)

    def test_stuck_on_faults_when_commanded_off(self):
        feedback = simulate_binary_actuator(False, elapsed_since_command_ms=0, fault_mode=FaultMode.STUCK_ON)
        self.assertTrue(feedback.measured_state)
        self.assertEqual(feedback.fault_code, "ACTUATOR-STUCK-ON")

    def test_stuck_off_matches_an_off_command_without_fault(self):
        feedback = simulate_binary_actuator(False, elapsed_since_command_ms=0, fault_mode=FaultMode.STUCK_OFF)
        self.assertFalse(feedback.measured_state)
        self.assertIsNone(feedback.fault_code)

    def test_stuck_off_faults_when_commanded_on(self):
        feedback = simulate_binary_actuator(True, elapsed_since_command_ms=99999, fault_mode=FaultMode.STUCK_OFF)
        self.assertFalse(feedback.measured_state)
        self.assertEqual(feedback.fault_code, "ACTUATOR-STUCK-OFF")


class TestServoWrongPosition(unittest.TestCase):
    """Roadmap task 65: incorrect virtual servo position."""

    def test_normal_servo_reports_commanded_angle(self):
        feedback = simulate_servo_actuator(90)
        self.assertEqual(feedback.measured_deg, 90)
        self.assertIsNone(feedback.fault_code)

    def test_wrong_position_offsets_and_faults(self):
        feedback = simulate_servo_actuator(90, fault_mode=FaultMode.WRONG_POSITION)
        self.assertNotEqual(feedback.measured_deg, 90)
        self.assertEqual(feedback.fault_code, "ACTUATOR-WRONG-POSITION")

    def test_wrong_position_clamps_to_servo_range(self):
        feedback = simulate_servo_actuator(170, fault_mode=FaultMode.WRONG_POSITION)
        self.assertLessEqual(feedback.measured_deg, 180)
        feedback = simulate_servo_actuator(0, fault_mode=FaultMode.WRONG_POSITION)
        self.assertGreaterEqual(feedback.measured_deg, 0)


class TestDetectMismatch(unittest.TestCase):
    """Roadmap task 61: simulated actuator feedback / mismatch detection."""

    def test_matching_states_produce_no_fault(self):
        self.assertIsNone(detect_mismatch(True, True))
        self.assertIsNone(detect_mismatch(90, 90))

    def test_disagreement_without_explicit_fault_code_is_still_a_fault(self):
        # Never silently assume commanded == measured (Stage 9's core hazard).
        self.assertEqual(detect_mismatch(True, False), "ACTUATOR-MISMATCH")
        self.assertEqual(detect_mismatch(10, 25), "ACTUATOR-MISMATCH")

    def test_explicit_fault_code_from_source_wins(self):
        self.assertEqual(detect_mismatch(True, True, fault_code="ACTUATOR-STUCK-ON"), "ACTUATOR-STUCK-ON")


class TestActuatorStateEvidence(unittest.TestCase):
    def test_to_actuator_state_populates_simulated_not_measured(self):
        state = to_actuator_state("fan", requested_state=True, commanded_state=True, measured_state=False,
                                   fault_code="ACTUATOR-FAILED-STARTUP")
        self.assertEqual(state.name, "fan")
        self.assertTrue(state.requested_state)
        self.assertTrue(state.commanded_state)
        self.assertFalse(state.simulated_state)
        self.assertIsNone(state.measured_state)  # no real sensor yet -- Stage 11
        self.assertEqual(state.fault_state, "ACTUATOR-FAILED-STARTUP")


class TestFeedbackFaultDrivesSafetyResponse(unittest.TestCase):
    """Roadmap task 66: make the ESP respond to feedback faults.

    A detected actuator fault is fed into evaluate_safety's existing
    controller_fault input -- the already-verified SAFETY-tier response
    (safe state, critical alarm) applies unchanged; the specific fault
    code stays available separately as explicit evidence, not folded into
    or hidden by that boolean.
    """

    def test_stuck_on_fan_forces_safe_state_via_controller_fault(self):
        sensors = make_sensors(temperature=40.0, soil_moisture=50.0, rain=0)
        decision = evaluate_decision(sensors, previous_pump_requested=False, decision_id="d1")
        self.assertTrue(decision.requested_fan)  # hot -> fan requested on

        fan_feedback = simulate_binary_actuator(False, elapsed_since_command_ms=0, fault_mode=FaultMode.STUCK_ON)
        fault_code = detect_mismatch(False, fan_feedback.measured_state, fan_feedback.fault_code)
        self.assertEqual(fault_code, "ACTUATOR-STUCK-ON")

        result = evaluate_safety(decision, tank_level_percent=80.0, controller_fault=fault_code is not None)
        self.assertEqual(result.applied_priority, SafetyPriority.SAFETY)
        self.assertEqual(result.alarm_level, "critical")
        self.assertFalse(result.commanded_fan)
        self.assertIn("CONTROLLER-FAULT", result.overrides)

    def test_wrong_servo_position_forces_safe_state_via_controller_fault(self):
        sensors = make_sensors(temperature=40.0, soil_moisture=50.0, rain=0)
        decision = evaluate_decision(sensors, previous_pump_requested=False, decision_id="d2")

        servo_feedback = simulate_servo_actuator(decision.requested_window_deg, fault_mode=FaultMode.WRONG_POSITION)
        fault_code = detect_mismatch(decision.requested_window_deg, servo_feedback.measured_deg, servo_feedback.fault_code)
        self.assertEqual(fault_code, "ACTUATOR-WRONG-POSITION")

        result = evaluate_safety(decision, tank_level_percent=80.0, controller_fault=fault_code is not None)
        self.assertEqual(result.applied_priority, SafetyPriority.SAFETY)
        self.assertEqual(result.alarm_level, "critical")

    def test_no_fault_leaves_automatic_operation_unaffected(self):
        sensors = make_sensors(temperature=40.0, soil_moisture=50.0, rain=0)
        decision = evaluate_decision(sensors, previous_pump_requested=False, decision_id="d3")

        fan_feedback = simulate_binary_actuator(True, elapsed_since_command_ms=99999)
        fault_code = detect_mismatch(True, fan_feedback.measured_state, fan_feedback.fault_code)
        self.assertIsNone(fault_code)

        result = evaluate_safety(decision, tank_level_percent=80.0, controller_fault=fault_code is not None)
        self.assertEqual(result.applied_priority, SafetyPriority.AUTOMATIC_OPERATION)
        self.assertTrue(result.commanded_fan)


if __name__ == "__main__":
    unittest.main()
