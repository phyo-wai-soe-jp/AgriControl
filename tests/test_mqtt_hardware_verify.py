"""Tests for tools/mqtt_hardware_verify.py's payload-building logic --
the only part of that script that's pure logic rather than network I/O
(which needs a real MQTT broker this environment doesn't have)."""
import importlib.util
import pathlib
import unittest

_MODULE_PATH = pathlib.Path(__file__).resolve().parent.parent / "tools" / "mqtt_hardware_verify.py"
_spec = importlib.util.spec_from_file_location("mqtt_hardware_verify", _MODULE_PATH)
mqtt_hardware_verify = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mqtt_hardware_verify)
build_payload = mqtt_hardware_verify.build_payload
build_feedback_payload = mqtt_hardware_verify.build_feedback_payload


class TestBuildPayload(unittest.TestCase):
    def test_temperature_only_omits_optional_fields(self):
        payload = build_payload("session-a", 1, 25.0)
        self.assertEqual(payload, {"session_id": "session-a", "sequence": 1, "values": {"temperature": 25.0}})

    def test_all_fields_included_when_provided(self):
        payload = build_payload("session-a", 2, 20.0, soil_moisture=22.5, tank=60.0, rain=0.0)
        self.assertEqual(
            payload,
            {
                "session_id": "session-a",
                "sequence": 2,
                "values": {
                    "temperature": 20.0,
                    "soil_moisture": 22.5,
                    "water_level_percent": 60.0,
                    "rain": 0.0,
                },
            },
        )

    def test_partial_fields_only_include_what_was_given(self):
        payload = build_payload("session-a", 3, 20.0, soil_moisture=15.0)
        self.assertEqual(
            payload, {"session_id": "session-a", "sequence": 3, "values": {"temperature": 20.0, "soil_moisture": 15.0}}
        )
        self.assertNotIn("water_level_percent", payload["values"])
        self.assertNotIn("rain", payload["values"])

    def test_rain_zero_is_not_treated_as_missing(self):
        # rain=0.0 is falsy in Python -- must use "is not None", not
        # truthiness, or a genuine 0 reading would be silently dropped.
        payload = build_payload("session-a", 4, 20.0, rain=0.0)
        self.assertIn("rain", payload["values"])
        self.assertEqual(payload["values"]["rain"], 0.0)


class TestBuildFeedbackPayload(unittest.TestCase):
    def test_fault_code_included_when_present(self):
        payload = build_feedback_payload(1, "pump", "ACTUATOR-STUCK-OFF")
        self.assertEqual(payload, {"request_id": 1, "actuator": "pump", "fault_code": "ACTUATOR-STUCK-OFF"})

    def test_fault_code_none_clears_a_fault(self):
        payload = build_feedback_payload(2, "fan", None)
        self.assertEqual(payload, {"request_id": 2, "actuator": "fan", "fault_code": None})


if __name__ == "__main__":
    unittest.main()
