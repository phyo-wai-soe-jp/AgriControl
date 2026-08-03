import unittest

from logic.canonical import SensorReading, SensorState, SourceMode


class TestSensorState(unittest.TestCase):
    def test_update_and_get(self):
        state = SensorState()
        reading = SensorReading(
            name="temperature",
            value=25.0,
            unit="celsius",
            source=SourceMode.VIRTUAL,
            quality="good",
            received_at_ms=1000,
            valid=True,
        )
        state.update(reading)
        self.assertEqual(state.get("temperature"), reading)
        self.assertEqual(state.value_of("temperature"), 25.0)

    def test_value_of_none_when_missing(self):
        state = SensorState()
        self.assertIsNone(state.value_of("temperature"))

    def test_value_of_none_when_invalid(self):
        state = SensorState()
        state.update(
            SensorReading(
                name="temperature",
                value=25.0,
                unit="celsius",
                source=SourceMode.VIRTUAL,
                quality="bad",
                received_at_ms=1000,
                valid=False,
            )
        )
        self.assertIsNone(state.value_of("temperature"))

    def test_age_ms(self):
        reading = SensorReading(
            name="temperature",
            value=25.0,
            unit="celsius",
            source=SourceMode.VIRTUAL,
            quality="good",
            received_at_ms=1000,
            valid=True,
        )
        self.assertEqual(reading.age_ms(1500), 500)
        self.assertEqual(reading.age_ms(500), 0)


if __name__ == "__main__":
    unittest.main()
