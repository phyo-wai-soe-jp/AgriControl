import unittest

from logic.decision import (
    WINDOW_CLOSED_DEG,
    WINDOW_HALF_DEG,
    WINDOW_OPEN_DEG,
    evaluate_decision,
)
from tests.helpers import make_sensors


class TestDecisionNormalConditions(unittest.TestCase):
    """Roadmap task 13: Test normal conditions."""

    def test_low_temperature_closes_window_and_turns_fan_off(self):
        sensors = make_sensors(temperature=20.0)
        decision = evaluate_decision(sensors, previous_pump_requested=False, decision_id="d1")
        self.assertFalse(decision.requested_fan)
        self.assertEqual(decision.requested_window_deg, WINDOW_CLOSED_DEG)
        self.assertIn("TEMPERATURE-001", decision.triggered_rules)

    def test_mid_temperature_opens_window_half(self):
        sensors = make_sensors(temperature=30.0)
        decision = evaluate_decision(sensors, previous_pump_requested=False, decision_id="d2")
        self.assertTrue(decision.requested_fan)
        self.assertEqual(decision.requested_window_deg, WINDOW_HALF_DEG)
        self.assertIn("TEMPERATURE-002", decision.triggered_rules)

    def test_high_temperature_opens_window_fully(self):
        sensors = make_sensors(temperature=40.0)
        decision = evaluate_decision(sensors, previous_pump_requested=False, decision_id="d3")
        self.assertTrue(decision.requested_fan)
        self.assertEqual(decision.requested_window_deg, WINDOW_OPEN_DEG)
        self.assertIn("TEMPERATURE-003", decision.triggered_rules)

    def test_dry_soil_no_rain_requests_pump_on(self):
        sensors = make_sensors(temperature=20.0, soil_moisture=20.0, rain=0)
        decision = evaluate_decision(sensors, previous_pump_requested=False, decision_id="d4")
        self.assertTrue(decision.requested_pump)
        self.assertIn("IRRIGATION-001", decision.triggered_rules)

    def test_dry_soil_with_rain_does_not_request_pump_on(self):
        sensors = make_sensors(temperature=20.0, soil_moisture=20.0, rain=1)
        decision = evaluate_decision(sensors, previous_pump_requested=False, decision_id="d5")
        self.assertFalse(decision.requested_pump)
        self.assertIn("IRRIGATION-003", decision.triggered_rules)

    def test_wet_soil_requests_pump_off(self):
        sensors = make_sensors(temperature=20.0, soil_moisture=50.0, rain=0)
        decision = evaluate_decision(sensors, previous_pump_requested=True, decision_id="d6")
        self.assertFalse(decision.requested_pump)
        self.assertIn("IRRIGATION-002", decision.triggered_rules)


class TestDecisionBoundaries(unittest.TestCase):
    """Roadmap task 14: Test exact boundaries."""

    def test_temperature_exactly_28_is_fan_off(self):
        sensors = make_sensors(temperature=28.0)
        decision = evaluate_decision(sensors, previous_pump_requested=False, decision_id="b1")
        self.assertFalse(decision.requested_fan)
        self.assertEqual(decision.requested_window_deg, WINDOW_CLOSED_DEG)

    def test_temperature_just_above_28_is_fan_on(self):
        sensors = make_sensors(temperature=28.1)
        decision = evaluate_decision(sensors, previous_pump_requested=False, decision_id="b2")
        self.assertTrue(decision.requested_fan)
        self.assertEqual(decision.requested_window_deg, WINDOW_HALF_DEG)

    def test_temperature_exactly_35_is_half_open_not_full(self):
        sensors = make_sensors(temperature=35.0)
        decision = evaluate_decision(sensors, previous_pump_requested=False, decision_id="b3")
        self.assertEqual(decision.requested_window_deg, WINDOW_HALF_DEG)

    def test_temperature_just_above_35_is_fully_open(self):
        sensors = make_sensors(temperature=35.1)
        decision = evaluate_decision(sensors, previous_pump_requested=False, decision_id="b4")
        self.assertEqual(decision.requested_window_deg, WINDOW_OPEN_DEG)

    def test_moisture_exactly_30_holds_previous_pump_state(self):
        sensors = make_sensors(temperature=20.0, soil_moisture=30.0, rain=0)
        decision = evaluate_decision(sensors, previous_pump_requested=True, decision_id="b5")
        self.assertTrue(decision.requested_pump)
        self.assertIn("IRRIGATION-003", decision.triggered_rules)

    def test_moisture_exactly_40_holds_previous_pump_state(self):
        sensors = make_sensors(temperature=20.0, soil_moisture=40.0, rain=0)
        decision = evaluate_decision(sensors, previous_pump_requested=False, decision_id="b6")
        self.assertFalse(decision.requested_pump)
        self.assertIn("IRRIGATION-003", decision.triggered_rules)

    def test_moisture_just_below_30_requests_pump_on(self):
        sensors = make_sensors(temperature=20.0, soil_moisture=29.9, rain=0)
        decision = evaluate_decision(sensors, previous_pump_requested=False, decision_id="b7")
        self.assertTrue(decision.requested_pump)

    def test_moisture_just_above_40_requests_pump_off(self):
        sensors = make_sensors(temperature=20.0, soil_moisture=40.1, rain=0)
        decision = evaluate_decision(sensors, previous_pump_requested=True, decision_id="b8")
        self.assertFalse(decision.requested_pump)


class TestDecisionMissingData(unittest.TestCase):
    def test_missing_temperature_holds_closed_and_off(self):
        sensors = make_sensors()
        decision = evaluate_decision(sensors, previous_pump_requested=False, decision_id="m1")
        self.assertFalse(decision.requested_fan)
        self.assertEqual(decision.requested_window_deg, WINDOW_CLOSED_DEG)

    def test_missing_moisture_holds_previous_pump_state(self):
        sensors = make_sensors(temperature=20.0)
        decision = evaluate_decision(sensors, previous_pump_requested=True, decision_id="m2")
        self.assertTrue(decision.requested_pump)


class TestDecisionStateSequences(unittest.TestCase):
    """Roadmap task 16: Test state sequences (stateful hysteresis)."""

    def test_blueprint_moisture_sequence_50_20_35_45(self):
        pump_state = False
        expected_after_each_step = [False, True, True, False]

        for moisture, expected_pump in zip([50.0, 20.0, 35.0, 45.0], expected_after_each_step):
            sensors = make_sensors(temperature=20.0, soil_moisture=moisture, rain=0)
            decision = evaluate_decision(sensors, previous_pump_requested=pump_state, decision_id="seq")
            self.assertEqual(
                decision.requested_pump,
                expected_pump,
                f"moisture={moisture} expected pump={expected_pump} got={decision.requested_pump}",
            )
            pump_state = decision.requested_pump


if __name__ == "__main__":
    unittest.main()
