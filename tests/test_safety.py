import unittest

from logic.decision import WINDOW_CLOSED_DEG, evaluate_decision
from logic.safety import SafetyPriority, evaluate_safety
from tests.helpers import make_sensors


class TestSafetyConflictResolution(unittest.TestCase):
    """Roadmap task 15: Test conflicting rules."""

    def test_blueprint_conflict_example_dry_soil_vs_low_tank(self):
        # Decision engine: dry soil -> pump ON.
        sensors = make_sensors(temperature=20.0, soil_moisture=20.0, rain=0)
        decision = evaluate_decision(sensors, previous_pump_requested=False, decision_id="c1")
        self.assertTrue(decision.requested_pump)

        # Safety supervisor: tank below 15% -> pump OFF. Final command: pump OFF.
        result = evaluate_safety(decision, tank_level_percent=10.0)
        self.assertFalse(result.commanded_pump)
        self.assertEqual(result.applied_priority, SafetyPriority.EQUIPMENT_PROTECTION)
        self.assertIn("LOW-TANK", result.overrides)

    def test_tank_at_exactly_15_percent_does_not_block_pump(self):
        sensors = make_sensors(temperature=20.0, soil_moisture=20.0, rain=0)
        decision = evaluate_decision(sensors, previous_pump_requested=False, decision_id="c2")
        result = evaluate_safety(decision, tank_level_percent=15.0)
        self.assertTrue(result.commanded_pump)
        self.assertEqual(result.applied_priority, SafetyPriority.AUTOMATIC_OPERATION)

    def test_emergency_stop_beats_low_tank(self):
        sensors = make_sensors(temperature=20.0, soil_moisture=20.0, rain=0)
        decision = evaluate_decision(sensors, previous_pump_requested=False, decision_id="c3")
        result = evaluate_safety(decision, tank_level_percent=5.0, emergency_stop=True)
        self.assertEqual(result.applied_priority, SafetyPriority.EMERGENCY)
        self.assertFalse(result.commanded_pump)
        self.assertFalse(result.commanded_fan)
        self.assertEqual(result.commanded_window_deg, WINDOW_CLOSED_DEG)
        self.assertEqual(result.alarm_level, "critical")

    def test_controller_fault_beats_low_tank(self):
        sensors = make_sensors(temperature=40.0, soil_moisture=20.0, rain=0)
        decision = evaluate_decision(sensors, previous_pump_requested=False, decision_id="c4")
        result = evaluate_safety(decision, tank_level_percent=5.0, controller_fault=True)
        self.assertEqual(result.applied_priority, SafetyPriority.SAFETY)
        self.assertFalse(result.commanded_pump)


class TestSafetyStateMatrix(unittest.TestCase):
    def setUp(self):
        sensors = make_sensors(temperature=40.0, soil_moisture=20.0, rain=0)
        self.decision = evaluate_decision(sensors, previous_pump_requested=False, decision_id="s0")

    def test_startup_forces_safe_state(self):
        result = evaluate_safety(self.decision, tank_level_percent=70.0, is_startup=True)
        self.assertFalse(result.commanded_pump)
        self.assertFalse(result.commanded_fan)
        self.assertEqual(result.commanded_window_deg, WINDOW_CLOSED_DEG)
        self.assertEqual(result.alarm_level, "startup_indication")

    def test_valid_operation_passes_decision_through(self):
        result = evaluate_safety(self.decision, tank_level_percent=70.0)
        self.assertEqual(result.commanded_pump, self.decision.requested_pump)
        self.assertEqual(result.commanded_fan, self.decision.requested_fan)
        self.assertEqual(result.commanded_window_deg, self.decision.requested_window_deg)
        self.assertEqual(result.alarm_level, "normal")

    def test_low_tank_still_allows_fan_and_window_through(self):
        result = evaluate_safety(self.decision, tank_level_percent=10.0)
        self.assertFalse(result.commanded_pump)
        self.assertEqual(result.commanded_fan, self.decision.requested_fan)
        self.assertEqual(result.commanded_window_deg, self.decision.requested_window_deg)
        self.assertEqual(result.alarm_level, "warning")

    def test_stale_data_forces_safe_state(self):
        result = evaluate_safety(self.decision, tank_level_percent=70.0, data_stale=True, configured_safe_fan_state=True)
        self.assertFalse(result.commanded_pump)
        self.assertTrue(result.commanded_fan)
        self.assertEqual(result.commanded_window_deg, WINDOW_CLOSED_DEG)
        self.assertEqual(result.alarm_level, "warning")

    def test_controller_fault_forces_safe_state_critical_alarm(self):
        result = evaluate_safety(self.decision, tank_level_percent=70.0, controller_fault=True)
        self.assertFalse(result.commanded_pump)
        self.assertEqual(result.commanded_window_deg, WINDOW_CLOSED_DEG)
        self.assertEqual(result.alarm_level, "critical")

    def test_emergency_stop_forces_everything_off(self):
        result = evaluate_safety(self.decision, tank_level_percent=70.0, emergency_stop=True)
        self.assertFalse(result.commanded_pump)
        self.assertFalse(result.commanded_fan)
        self.assertEqual(result.commanded_window_deg, WINDOW_CLOSED_DEG)
        self.assertEqual(result.alarm_level, "critical")


if __name__ == "__main__":
    unittest.main()
