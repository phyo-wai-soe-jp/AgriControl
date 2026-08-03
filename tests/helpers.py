"""Shared test helpers for building canonical sensor state."""
from logic.canonical import SensorReading, SensorState, SourceMode


def make_sensors(temperature=None, soil_moisture=None, rain=None, water_level_percent=None, now_ms=1000):
    state = SensorState()
    values = {
        "temperature": temperature,
        "soil_moisture": soil_moisture,
        "rain": rain,
        "water_level_percent": water_level_percent,
    }
    units = {
        "temperature": "celsius",
        "soil_moisture": "percent",
        "rain": "boolean",
        "water_level_percent": "percent",
    }
    for name, value in values.items():
        if value is None:
            continue
        state.update(
            SensorReading(
                name=name,
                value=float(value),
                unit=units[name],
                source=SourceMode.VIRTUAL,
                quality="good",
                received_at_ms=now_ms,
                valid=True,
            )
        )
    return state
