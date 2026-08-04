// Stage 5 roadmap tasks 31/33/34/35/36/37: first vertical slice -- virtual
// temperature only (env:vertical_slice).
//
// Builds on the Stage 4 runtime (env:runtime, src/runtime.cpp) by adding
// temperature-range validation, the decision engine, servo output, OLED
// display, and a full JSON response with commands and reasons.
//
// Deliberately narrow scope, matching roadmap task 31 ("Implement only
// virtual temperature"): soil moisture, tank level, and rain are Stage 7,
// not here.
//
// IMPORTANT GAP: the safety supervisor (logic/safety.py) has not been
// ported to firmware yet. This slice applies the decision engine's output
// to the servo directly, with no override layer -- no low-tank pump
// protection, no emergency stop, no fault/stale-data safe-state (tick()
// still detects staleness and moves system.mode(), but nothing here reacts
// to that by forcing a safe servo position). That must be closed before
// this drives anything beyond a bench test.
//
// Build/upload with: pio run -e vertical_slice -t upload
// Needs firmware/include/secrets.h (see runtime.cpp's header) and the
// ArduinoJson/U8g2/ESP32Servo libraries already declared in platformio.ini.
// Never built or flashed from this environment -- treat as a reviewed
// draft, not verified working code.
#include <string.h>

#include <ArduinoJson.h>
#include <ESP32Servo.h>
#include <U8g2lib.h>
#include <WebServer.h>
#include <WiFi.h>
#include <Wire.h>

#include "decision.h"
#include "pins.h"
#include "secrets.h"
#include "shared_state.h"

namespace {

constexpr size_t kMaxRequestBodyBytes = 2048;

// Roadmap task 33: temperature range validation. The blueprint does not
// specify exact acceptance bounds, so this is a conservative
// physically-plausible sensor range (-40C to 85C, typical of common
// digital temperature sensors), not a hardware fact. Confirm/adjust with
// the owner before relying on it.
constexpr float kTemperatureMinC = -40.0f;
constexpr float kTemperatureMaxC = 85.0f;

WebServer server(80);
SharedState shared;
U8G2_SSD1306_128X64_NONAME_F_HW_I2C oled(U8G2_R0, U8X8_PIN_NONE);
Servo windowServo;

void sendJsonError(int code, const char* error) {
  JsonDocument doc;
  doc["accepted"] = false;
  doc["error"] = error;
  String body;
  serializeJson(doc, body);
  server.send(code, "application/json", body);
}

void rejectAndLog(int code, const char* error, unsigned long nowMs, const String& detail) {
  sendJsonError(code, error);
  shared.events.push(nowMs, "REJECTED", detail);
  shared.recovery.recordFailure();
}

void showOnOled(float temperatureC, const TemperatureDecision& decision) {
  oled.clearBuffer();
  oled.setFont(u8g2_font_6x10_tf);
  char line1[24];
  snprintf(line1, sizeof(line1), "TEMP: %.1f C", temperatureC);
  oled.drawStr(0, 12, line1);
  oled.drawStr(0, 26, decision.requestedFan ? "FAN: ON" : "FAN: OFF");
  char line3[24];
  snprintf(line3, sizeof(line3), "WINDOW: %d deg", decision.requestedWindowDeg);
  oled.drawStr(0, 40, line3);
  oled.drawStr(0, 54, decision.triggeredRule);
  oled.sendBuffer();
}

void handleSensorPost() {
  unsigned long nowMs = millis();

  if (!server.hasArg("plain")) {
    rejectAndLog(400, "missing body", nowMs, "Missing request body");
    return;
  }
  const String& body = server.arg("plain");
  if (body.length() > kMaxRequestBodyBytes) {
    rejectAndLog(413, "request body too large", nowMs, "Request body exceeded size limit");
    return;
  }

  JsonDocument doc;
  DeserializationError parseError = deserializeJson(doc, body);
  if (parseError) {
    rejectAndLog(400, "invalid JSON", nowMs, String("JSON parse error: ") + parseError.c_str());
    return;
  }

  if (!doc["sequence"].is<long>()) {
    rejectAndLog(400, "missing or invalid sequence", nowMs, "Missing or invalid sequence field");
    return;
  }
  long sequence = doc["sequence"].as<long>();
  if (shared.haveSequence && sequence <= static_cast<long>(shared.lastSequence)) {
    rejectAndLog(400, "duplicate or out-of-order sequence", nowMs, "Duplicate or out-of-order sequence");
    return;
  }

  JsonObject values = doc["values"];
  if (values.isNull() || !values["temperature"].is<float>()) {
    rejectAndLog(400, "missing or invalid temperature", nowMs, "Missing or invalid values.temperature");
    return;
  }
  // First vertical slice: temperature only. Any other key in values is
  // rejected here -- soil/tank/rain arrive in Stage 7, not this slice.
  for (JsonPair kv : values) {
    if (strcmp(kv.key().c_str(), "temperature") != 0) {
      rejectAndLog(400, "unknown sensor field", nowMs, String("Unknown sensor field: ") + kv.key().c_str());
      return;
    }
  }

  float temperatureC = values["temperature"].as<float>();
  if (temperatureC < kTemperatureMinC || temperatureC > kTemperatureMaxC) {
    rejectAndLog(400, "temperature out of range", nowMs, String("Temperature out of range: ") + temperatureC);
    return;
  }

  shared.sensors.update(SensorId::TEMPERATURE, temperatureC, nowMs);
  shared.lastSequence = static_cast<unsigned long>(sequence);
  shared.haveSequence = true;
  shared.recovery.recordValid();

  TemperatureDecision decision = evaluateTemperatureDecision(temperatureC);

  // Roadmap task 35: apply the servo command. No safety supervisor is
  // wired in yet (see file header) -- this writes the decision engine's
  // output directly, unmodified.
  windowServo.write(decision.requestedWindowDeg);

  // Roadmap task 36: display the reason on OLED.
  showOnOled(temperatureC, decision);

  shared.events.push(nowMs, "DECISION", decision.reason);

  // Roadmap task 37: return the decision as JSON.
  JsonDocument response;
  response["accepted"] = true;
  response["sequence"] = sequence;
  response["mode"] = "automatic";
  JsonObject commands = response["commands"].to<JsonObject>();
  commands["fan"] = decision.requestedFan;
  commands["window_angle"] = decision.requestedWindowDeg;
  JsonArray triggeredRules = response["triggered_rules"].to<JsonArray>();
  triggeredRules.add(decision.triggeredRule);
  JsonArray reasons = response["reasons"].to<JsonArray>();
  reasons.add(decision.reason);
  String responseBody;
  serializeJson(response, responseBody);
  server.send(200, "application/json", responseBody);
}

void handleNotFound() { sendJsonError(404, "not found"); }

}  // namespace

void setup() {
  Serial.begin(115200);
  Wire.begin(pins::I2C_SDA, pins::I2C_SCL);
  oled.begin();
  windowServo.attach(pins::CN3_SERVO);

  shared.system.transitionTo(Mode::CONNECTING);
  shared.system.setCommunicationState(CommunicationState::CONNECTING);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(200);
  }
  shared.system.setCommunicationState(CommunicationState::ONLINE);
  shared.system.transitionTo(Mode::READY);
  shared.system.transitionTo(Mode::AUTOMATIC);
  shared.events.push(millis(), "WIFI_CONNECTED", WiFi.localIP().toString());

  server.on("/sensor", HTTP_POST, handleSensorPost);
  server.onNotFound(handleNotFound);
  server.begin();
}

void loop() {
  server.handleClient();
  shared.tick(millis());
}
