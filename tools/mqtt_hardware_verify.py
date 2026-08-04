#!/usr/bin/env python3
"""MQTT hardware-verification client for firmware/src/mqtt_test_harness.cpp.

Publishes one simulated sensor reading to agricontrol/sensor and waits for
the board's real response on agricontrol/state -- so the actual compiled
AgriControl firmware's decision+safety output can be checked against a
physical board, not logic/decision.py's host tests and not a different
project's firmware.

Requires: pip install paho-mqtt

Credentials come from environment variables, never hardcoded here or
anywhere in this repo:
    AGRICONTROL_MQTT_HOST
    AGRICONTROL_MQTT_PORT      (default 8883)
    AGRICONTROL_MQTT_USER
    AGRICONTROL_MQTT_PASSWORD

Usage:
    python3 tools/mqtt_hardware_verify.py --temperature 32 \
        --soil-moisture 20 --tank 80 --rain 0

Not executed or verified in this environment -- no network path to any
MQTT broker and no credentials here. Written and ready for whoever runs it
against real hardware.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Optional

SENSOR_TOPIC = "agricontrol/sensor"
STATE_TOPIC = "agricontrol/state"


def build_payload(
    sequence: int,
    temperature: float,
    soil_moisture: Optional[float] = None,
    tank: Optional[float] = None,
    rain: Optional[float] = None,
) -> dict:
    """Matches firmware/src/mqtt_test_harness.cpp's expected message shape
    exactly -- the same protocol env:irrigation_slice's HTTP POST /sensor
    accepts, just carried over MQTT. Only fields actually provided are
    included, same convention as backend/app.py's forward_temperature."""
    values = {"temperature": temperature}
    if soil_moisture is not None:
        values["soil_moisture"] = soil_moisture
    if tank is not None:
        values["water_level_percent"] = tank
    if rain is not None:
        values["rain"] = rain
    return {"sequence": sequence, "values": values}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--temperature", type=float, required=True)
    parser.add_argument("--soil-moisture", type=float, default=None)
    parser.add_argument("--tank", type=float, default=None)
    parser.add_argument("--rain", type=float, default=None, choices=[0.0, 1.0])
    parser.add_argument("--sequence", type=int, default=None, help="Defaults to the current unix timestamp")
    parser.add_argument("--timeout", type=float, default=10.0, help="Seconds to wait for a response")
    args = parser.parse_args()

    host = os.environ.get("AGRICONTROL_MQTT_HOST")
    port = int(os.environ.get("AGRICONTROL_MQTT_PORT", "8883"))
    user = os.environ.get("AGRICONTROL_MQTT_USER")
    password = os.environ.get("AGRICONTROL_MQTT_PASSWORD")
    if not host or not user or not password:
        print(
            "Set AGRICONTROL_MQTT_HOST, AGRICONTROL_MQTT_USER, and "
            "AGRICONTROL_MQTT_PASSWORD before running this.",
            file=sys.stderr,
        )
        return 1

    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        print("Missing dependency: pip install paho-mqtt", file=sys.stderr)
        return 1

    sequence = args.sequence if args.sequence is not None else int(time.time())
    payload = build_payload(sequence, args.temperature, args.soil_moisture, args.tank, args.rain)

    state = {"response": None}

    def on_message(client, userdata, msg):
        try:
            body = json.loads(msg.payload.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            return
        # A rejection response omits sequence entirely if the message
        # never even parsed -- only match on sequence when the board
        # echoed one back.
        if body.get("sequence") in (sequence, None):
            state["response"] = body

    client = mqtt.Client()
    client.username_pw_set(user, password)
    client.tls_set()
    client.on_message = on_message
    client.connect(host, port, keepalive=30)
    client.subscribe(STATE_TOPIC, qos=1)
    client.loop_start()

    client.publish(SENSOR_TOPIC, json.dumps(payload), qos=1)
    print(f"Published to {SENSOR_TOPIC}: {json.dumps(payload)}")

    deadline = time.time() + args.timeout
    while state["response"] is None and time.time() < deadline:
        time.sleep(0.1)

    client.loop_stop()
    client.disconnect()

    if state["response"] is None:
        print(f"No response on {STATE_TOPIC} within {args.timeout}s", file=sys.stderr)
        return 1

    print(f"Received from {STATE_TOPIC}:\n{json.dumps(state['response'], indent=2)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
