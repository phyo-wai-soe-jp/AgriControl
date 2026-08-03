"""Canonical sensor structures (blueprint Stage 2, roadmap task 9, Branch 6).

Both the virtual website and physical GPIO/ADC/I2C sources are adapted into
this same record shape before anything downstream reads a value, so decision
and safety code never need to know where a reading came from.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class SourceMode(str, Enum):
    VIRTUAL = "virtual"
    PHYSICAL = "physical"
    HYBRID = "hybrid"
    DISABLED = "disabled"


@dataclass(frozen=True)
class SensorReading:
    """One canonical sensor record, matching the blueprint's sensor abstraction schema."""

    name: str
    value: float
    unit: str
    source: SourceMode
    quality: str
    received_at_ms: int
    valid: bool

    def age_ms(self, now_ms: int) -> int:
        return max(0, now_ms - self.received_at_ms)


class SensorState:
    """Authoritative canonical sensor state keyed by sensor name (Branch 7: State management)."""

    def __init__(self) -> None:
        self._readings: Dict[str, SensorReading] = {}

    def update(self, reading: SensorReading) -> None:
        self._readings[reading.name] = reading

    def get(self, name: str) -> Optional[SensorReading]:
        return self._readings.get(name)

    def value_of(self, name: str) -> Optional[float]:
        """Return the reading's value only when the reading exists and is valid."""
        reading = self._readings.get(name)
        if reading is None or not reading.valid:
            return None
        return reading.value

    def all(self) -> Dict[str, SensorReading]:
        return dict(self._readings)
