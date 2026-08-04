import os
import tempfile
import unittest

from logic import decision as decision_module
from logic.replay import (
    load_recording,
    record_cycle,
    replay_cycle,
    replay_sequence,
    save_recording,
)
from tests.helpers import make_sensors


class TestRecordCycle(unittest.TestCase):
    """Roadmap task 67: recording."""

    def test_records_inputs_rule_versions_and_outputs(self):
        sensors = make_sensors(temperature=40.0, soil_moisture=20.0, rain=0, water_level_percent=80.0)
        cycle = record_cycle(1, sensors, previous_pump_requested=False, tank_level_percent=80.0)

        self.assertEqual(cycle.sequence, 1)
        self.assertEqual(cycle.decision_rules_version, "1.0.0")
        self.assertEqual(cycle.safety_rules_version, "1.0.0")
        self.assertEqual(cycle.temperature, 40.0)
        self.assertTrue(cycle.recorded_requested_fan)  # hot -> fan requested
        self.assertTrue(cycle.recorded_requested_pump)  # dry, no rain -> pump requested
        self.assertTrue(cycle.recorded_commanded_pump)  # tank fine -> not overridden
        self.assertEqual(cycle.recorded_alarm_level, "normal")

    def test_low_tank_records_the_safety_override_not_the_raw_request(self):
        sensors = make_sensors(temperature=20.0, soil_moisture=20.0, rain=0, water_level_percent=10.0)
        cycle = record_cycle(1, sensors, previous_pump_requested=False, tank_level_percent=10.0)
        self.assertTrue(cycle.recorded_requested_pump)  # decision engine still requests it
        self.assertFalse(cycle.recorded_commanded_pump)  # safety supervisor overrides it off
        self.assertEqual(cycle.recorded_alarm_level, "warning")


class TestReplayCycle(unittest.TestCase):
    """Roadmap task 67-68: replay against the current rules."""

    def test_unmodified_recording_replays_with_no_mismatches(self):
        sensors = make_sensors(temperature=40.0, soil_moisture=20.0, rain=0, water_level_percent=80.0)
        cycle = record_cycle(1, sensors, previous_pump_requested=False, tank_level_percent=80.0)
        self.assertEqual(replay_cycle(cycle), [])

    def test_tampered_recording_is_detected_as_a_mismatch(self):
        # Simulates "the rules changed since this was recorded" by
        # corrupting one recorded field, proving replay actually compares
        # values rather than trivially passing.
        sensors = make_sensors(temperature=40.0, soil_moisture=20.0, rain=0, water_level_percent=80.0)
        cycle = record_cycle(1, sensors, previous_pump_requested=False, tank_level_percent=80.0)
        tampered = cycle.__class__(**{**cycle.__dict__, "recorded_commanded_fan": not cycle.recorded_commanded_fan})

        mismatches = replay_cycle(tampered)
        self.assertEqual(len(mismatches), 1)
        self.assertEqual(mismatches[0].field, "commanded_fan")
        self.assertEqual(mismatches[0].sequence, 1)

    def test_replay_sequence_reports_mismatches_from_every_cycle(self):
        sensors = make_sensors(temperature=40.0, soil_moisture=20.0, rain=0, water_level_percent=80.0)
        good = record_cycle(1, sensors, previous_pump_requested=False, tank_level_percent=80.0)
        bad = record_cycle(2, sensors, previous_pump_requested=False, tank_level_percent=80.0)
        bad = bad.__class__(**{**bad.__dict__, "recorded_alarm_level": "critical"})

        mismatches = replay_sequence([good, bad])
        self.assertEqual(len(mismatches), 1)
        self.assertEqual(mismatches[0].sequence, 2)
        self.assertEqual(mismatches[0].field, "alarm_level")

    def test_actual_rule_change_is_caught_by_replay(self):
        # Genuinely change decision.py's threshold, not just a recorded
        # field, to prove replay would catch a real regression/rule change,
        # not only hand-tampered test data. Restored in the finally block
        # so this doesn't leak into other tests.
        sensors = make_sensors(temperature=30.0, soil_moisture=50.0, rain=0, water_level_percent=80.0)
        cycle = record_cycle(1, sensors, previous_pump_requested=False, tank_level_percent=80.0)
        self.assertTrue(cycle.recorded_requested_fan)  # 30C is above the 28C threshold

        original_threshold = decision_module.TEMP_FAN_ON_ABOVE
        try:
            decision_module.TEMP_FAN_ON_ABOVE = 35.0  # 30C would no longer trigger the fan
            mismatches = replay_cycle(cycle)
        finally:
            decision_module.TEMP_FAN_ON_ABOVE = original_threshold

        fields = {m.field for m in mismatches}
        self.assertIn("requested_fan", fields)


class TestRecordingPersistence(unittest.TestCase):
    """Roadmap task 67: durable recording/replay round-trip."""

    def test_save_and_load_round_trips_every_field(self):
        sensors = make_sensors(temperature=40.0, soil_moisture=20.0, rain=1, water_level_percent=5.0)
        cycles = [
            record_cycle(1, sensors, previous_pump_requested=False, tank_level_percent=5.0),
            record_cycle(2, sensors, previous_pump_requested=True, tank_level_percent=5.0),
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "recording.jsonl")
            save_recording(cycles, path)
            loaded = load_recording(path)

        self.assertEqual(loaded, cycles)
        self.assertEqual(replay_sequence(loaded), [])


class TestLongDurationRecordingAndReplay(unittest.TestCase):
    """Roadmap task 69: long-duration/endurance evidence for the replay
    engine itself, not just the FastAPI bridge (already covered in
    backend/tests/test_app.py::TestEndurance)."""

    def test_thousand_cycle_recording_replays_cleanly(self):
        cycles = []
        previous_pump = False
        for i in range(1000):
            temperature = -10.0 + (i % 100)
            moisture = float(i % 100)
            rain = float(i % 7 == 0)
            tank = float((i * 3) % 100)
            sensors = make_sensors(temperature=temperature, soil_moisture=moisture, rain=rain, water_level_percent=tank)
            cycle = record_cycle(i, sensors, previous_pump_requested=previous_pump, tank_level_percent=tank)
            previous_pump = cycle.recorded_requested_pump
            cycles.append(cycle)

        self.assertEqual(len(cycles), 1000)
        self.assertEqual(replay_sequence(cycles), [])  # nothing changed -> zero mismatches over 1000 cycles


if __name__ == "__main__":
    unittest.main()
