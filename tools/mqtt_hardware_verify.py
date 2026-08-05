#!/usr/bin/env python3
"""MQTT hardware-verification client for firmware/src/mqtt_test_harness.cpp.

Publishes one simulated sensor reading to agricontrol/sensor (or, with
--feedback, one actuator-fault message to agricontrol/feedback) and waits
for the board's real response on the matching *_state topic -- so the
actual compiled AgriControl firmware's decision+safety output (or Stage
9's controller_fault reaction) can be checked against a physical board,
not logic/ host tests and not a different project's firmware.

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

    python3 tools/mqtt_hardware_verify.py --feedback \
        --actuator pump --fault-code ACTUATOR-STUCK-OFF

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
import uuid
from typing import Optional

SENSOR_TOPIC = "agricontrol/sensor"
STATE_TOPIC = "agricontrol/state"
FEEDBACK_TOPIC = "agricontrol/feedback"
FEEDBACK_STATE_TOPIC = "agricontrol/feedback_state"


def build_payload(
    session_id: str,
    sequence: int,
    temperature: float,
    soil_moisture: Optional[float] = None,
    tank: Optional[float] = None,
    rain: Optional[float] = None,
) -> dict:
    """Matches firmware/src/mqtt_test_harness.cpp's expected message shape
    exactly -- the same protocol env:irrigation_slice's HTTP POST /sensor
    accepts, just carried over MQTT. Only fields actually provided are
    included, same convention as backend/app.py's forward_temperature.

    session_id is required (2026-08-06): the firmware now scopes its
    duplicate/out-of-order sequence check to session_id, not to the
    device's whole uptime -- see firmware/include/shared_state.h's
    acceptSequence(). A message without one is now rejected outright.
    """
    values = {"temperature": temperature}
    if soil_moisture is not None:
        values["soil_moisture"] = soil_moisture
    if tank is not None:
        values["water_level_percent"] = tank
    if rain is not None:
        values["rain"] = rain
    return {"session_id": session_id, "sequence": sequence, "values": values}


def build_feedback_payload(request_id: int, actuator: str, fault_code: Optional[str]) -> dict:
    """Matches firmware/src/mqtt_test_harness.cpp's handleFeedbackMessage()
    expected shape -- the MQTT equivalent of irrigation_slice.cpp's POST
    /feedback (roadmap task 66). fault_code=None clears a previously-set
    fault, matching the "sticky until explicitly cleared" design."""
    return {"request_id": request_id, "actuator": actuator, "fault_code": fault_code}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--feedback", action="store_true", help="Send an actuator-feedback message instead of a sensor reading.")
    parser.add_argument("--temperature", type=float, help="Required unless --feedback.")
    parser.add_argument("--soil-moisture", type=float, default=None)
    parser.add_argument("--tank", type=float, default=None)
    parser.add_argument("--rain", type=float, default=None, choices=[0.0, 1.0])
    parser.add_argument("--actuator", choices=["fan", "pump", "window"], help="Required with --feedback.")
    parser.add_argument("--fault-code", default=None, help="e.g. ACTUATOR-STUCK-OFF; omit to clear a fault.")
    parser.add_argument("--session-id", default=None, help="Defaults to a fresh UUID (sensor readings only).")
    parser.add_argument("--sequence", type=int, default=None, help="Defaults to the current unix timestamp")
    parser.add_argument("--timeout", type=float, default=10.0, help="Seconds to wait for a response")
    args = parser.parse_args()

    if args.feedback and not args.actuator:
        parser.error("--feedback requires --actuator")
    if not args.feedback and args.temperature is None:
        parser.error("--temperature is required unless --feedback")

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

    if args.feedback:
        correlation_field = "request_id"
        correlation_value = args.sequence if args.sequence is not None else int(time.time())
        payload = build_feedback_payload(correlation_value, args.actuator, args.fault_code)
        publish_topic = FEEDBACK_TOPIC
        response_topic = FEEDBACK_STATE_TOPIC
    else:
        correlation_field = "sequence"
        correlation_value = args.sequence if args.sequence is not None else int(time.time())
        session_id = args.session_id or str(uuid.uuid4())
        payload = build_payload(session_id, correlation_value, args.temperature, args.soil_moisture, args.tank, args.rain)
        publish_topic = SENSOR_TOPIC
        response_topic = STATE_TOPIC

    state = {"response": None}

    def on_message(client, userdata, msg):
        try:
            body = json.loads(msg.payload.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            return
        # A rejection response omits the correlation field entirely if the
        # message never even parsed -- only match when the board echoed
        # one back matching what we sent, or omitted it entirely.
        if body.get(correlation_field) in (correlation_value, None):
            state["response"] = body

    client = mqtt.Client()
    client.username_pw_set(user, password)
    client.tls_set()
    client.on_message = on_message
    client.connect(host, port, keepalive=30)
    client.subscribe(response_topic, qos=1)
    client.loop_start()

    client.publish(publish_topic, json.dumps(payload), qos=1)
    print(f"Published to {publish_topic}: {json.dumps(payload)}")

    deadline = time.time() + args.timeout
    while state["response"] is None and time.time() < deadline:
        time.sleep(0.1)

    client.loop_stop()
    client.disconnect()

    if state["response"] is None:
        print(f"No response on {response_topic} within {args.timeout}s", file=sys.stderr)
        return 1

    print(f"Received from {response_topic}:\n{json.dumps(state['response'], indent=2)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
