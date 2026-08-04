// Stage 7 roadmap tasks 49-57: irrigation slice (env:irrigation_slice).
//
// Extends the Stage 5 vertical slice (env:vertical_slice, left unmodified)
// with soil moisture, tank level, and rain: pump hysteresis, low-tank
// protection, rain protection (rolled into the decision engine itself --
// see firmware/include/irrigation.h), a NeoPixel status color, and a
// buzzer tone on alarm-level changes.
//
// PUMP IS NOT PHYSICALLY DRIVEN. Same situation as the fan in
// vertical_slice.cpp: no pump GPIO/relay pin has been assigned (open
// owner question, see docs/PROJECT_STATE.md and firmware/README.md). The
// commanded pump state is computed, safety-checked, reported in the OLED
// and JSON response, and logged -- never written to a pin. Wire a real
// pump pin into `pins.h` and this file once the owner picks one; do not
// guess a pin here.
//
// Build/upload with: pio run -e irrigation_slice -t upload
// Needs firmware/include/secrets.h (see runtime.cpp's header) and the
// ArduinoJson/U8g2/ESP32Servo/Adafruit_NeoPixel libraries already declared
// in platformio.ini. Never built or flashed from this environment --
// treat as a reviewed draft, not verified working code.
#include <string.h>

#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>
#include <U8g2lib.h>
#include <WebServer.h>
#include <WiFi.h>
#include <Wire.h>

#include "irrigation.h"
#include "pins.h"
#include "secrets.h"
#include "shared_state.h"

namespace {

constexpr size_t kMaxRequestBodyBytes = 2048;

// Roadmap task 33-style validation, extended to the new sensors. The
// blueprint does not specify exact bounds; these are the physically
// plausible ranges for each reading (percentages 0-100, rain as a strict
// 0/1 flag matching logic/decision.py's rain_value convention), not
// hardware facts. Confirm/adjust with the owner before relying on them.
constexpr float kTemperatureMinC = -40.0f;
constexpr float kTemperatureMaxC = 85.0f;
constexpr float kPercentMin = 0.0f;
constexpr float kPercentMax = 100.0f;

constexpr bool kEmergencyStopActive = false;
constexpr bool kControllerFaultActive = false;
constexpr bool kConfiguredSafeFanState = false;

WebServer server(80);
SharedState shared;
U8G2_SSD1306_128X64_NONAME_F_HW_I2C oled(U8G2_R0, U8X8_PIN_NONE);
Servo windowServo;
Adafruit_NeoPixel statusPixels(pins::NEOPIXEL_COUNT, pins::NEOPIXEL, NEO_GRB + NEO_KHZ800);

bool previousPumpRequested = false;
String previousAlarmLevel = "";

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

bool inRange(float value, float minValue, float maxValue) { return value >= minValue && value <= maxValue; }

// Roadmap task 56: NeoPixel status color. The blueprint documents "Green
// normal, blue automatic, yellow warning, red critical, purple manual"
// for this LED without a precise rule for combining them. This mapping
// (an explicit interpretation, not a hardware fact) uses alarm_level
// directly, since that is the one unambiguous signal available: critical
// -> red, warning -> yellow, startup_indication -> blue, normal -> green.
// Confirm with the owner before treating this as final.
void updateStatusPixels(const char* alarmLevel) {
  uint32_t color;
  if (strcmp(alarmLevel, "critical") == 0) {
    color = statusPixels.Color(60, 0, 0);
  } else if (strcmp(alarmLevel, "warning") == 0) {
    color = statusPixels.Color(60, 45, 0);
  } else if (strcmp(alarmLevel, "startup_indication") == 0) {
    color = statusPixels.Color(0, 0, 60);
  } else {
    color = statusPixels.Color(0, 45, 0);
  }
  for (int i = 0; i < pins::NEOPIXEL_COUNT; i++) {
    statusPixels.setPixelColor(i, color);
  }
  statusPixels.show();
}

// Roadmap task 56: buzzer sounds only on alarm-level state changes, per
// the blueprint ("Buzzer sounds only on state changes"). One short,
// non-blocking tone() call per change -- severity communicated by pitch
// (lower = more urgent), not by a multi-beep pattern, so this never
// blocks the HTTP handler with delay(). This pitch choice is an explicit
// design decision, not specified by the blueprint.
void soundAlarmChangeTone(const char* alarmLevel) {
  if (strcmp(alarmLevel, "critical") == 0) {
    tone(pins::BUZZER, 440, 400);
  } else if (strcmp(alarmLevel, "warning") == 0) {
    tone(pins::BUZZER, 660, 250);
  } else {
    tone(pins::BUZZER, 880, 120);
  }
}

void showOnOled(float temperatureC, bool hasMoisture, float moisturePercent, bool hasTank, float tankPercent,
                const FullDecision& decision, const FullSafetyResult& safety) {
  oled.clearBuffer();
  oled.setFont(u8g2_font_6x10_tf);
  char line1[24];
  snprintf(line1, sizeof(line1), "TEMP:%.1fC WIN:%d", temperatureC, safety.commandedWindowDeg);
  oled.drawStr(0, 12, line1);

  char line2[24];
  if (hasMoisture) {
    snprintf(line2, sizeof(line2), "SOIL: %.0f%%", moisturePercent);
  } else {
    snprintf(line2, sizeof(line2), "SOIL: --");
  }
  oled.drawStr(0, 26, line2);

  char line3[24];
  if (hasTank) {
    snprintf(line3, sizeof(line3), "TANK: %.0f%%", tankPercent);
  } else {
    snprintf(line3, sizeof(line3), "TANK: --");
  }
  oled.drawStr(0, 40, line3);

  char line4[32];
  snprintf(
      line4, sizeof(line4), "PUMP:%s FAN:%s", safety.commandedPump ? "ON" : "OFF",
      safety.commandedFan ? "ON" : "OFF");
  oled.drawStr(0, 54, line4);

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

  // Known fields for this slice: temperature (required), soil_moisture,
  // water_level_percent, rain (all optional). Anything else is rejected.
  for (JsonPair kv : values) {
    const char* key = kv.key().c_str();
    if (strcmp(key, "temperature") != 0 && strcmp(key, "soil_moisture") != 0 &&
        strcmp(key, "water_level_percent") != 0 && strcmp(key, "rain") != 0) {
      rejectAndLog(400, "unknown sensor field", nowMs, String("Unknown sensor field: ") + key);
      return;
    }
  }

  float temperatureC = values["temperature"].as<float>();
  if (!inRange(temperatureC, kTemperatureMinC, kTemperatureMaxC)) {
    rejectAndLog(400, "temperature out of range", nowMs, String("Temperature out of range: ") + temperatureC);
    return;
  }

  bool hasMoisture = values["soil_moisture"].is<float>();
  float moisturePercent = 0.0f;
  if (hasMoisture) {
    moisturePercent = values["soil_moisture"].as<float>();
    if (!inRange(moisturePercent, kPercentMin, kPercentMax)) {
      rejectAndLog(400, "soil_moisture out of range", nowMs, String("soil_moisture out of range: ") + moisturePercent);
      return;
    }
  }

  bool hasTank = values["water_level_percent"].is<float>();
  float tankPercent = 0.0f;
  if (hasTank) {
    tankPercent = values["water_level_percent"].as<float>();
    if (!inRange(tankPercent, kPercentMin, kPercentMax)) {
      rejectAndLog(400, "water_level_percent out of range", nowMs, String("water_level_percent out of range: ") + tankPercent);
      return;
    }
  }

  bool hasRain = values["rain"].is<float>();
  float rainValue = 0.0f;
  if (hasRain) {
    rainValue = values["rain"].as<float>();
    if (rainValue != 0.0f && rainValue != 1.0f) {
      rejectAndLog(400, "rain must be 0 or 1", nowMs, String("rain out of range: ") + rainValue);
      return;
    }
  }

  bool isStartup = !shared.haveSequence;

  shared.sensors.update(SensorId::TEMPERATURE, temperatureC, nowMs);
  if (hasMoisture) shared.sensors.update(SensorId::SOIL_MOISTURE, moisturePercent, nowMs);
  if (hasTank) shared.sensors.update(SensorId::WATER_LEVEL_PERCENT, tankPercent, nowMs);
  if (hasRain) shared.sensors.update(SensorId::RAIN, rainValue, nowMs);
  shared.lastSequence = static_cast<unsigned long>(sequence);
  shared.haveSequence = true;
  shared.recovery.recordValid();

  FullDecision decision =
      evaluateFullDecision(temperatureC, hasMoisture, moisturePercent, hasRain, rainValue, previousPumpRequested);

  bool dataStale = shared.system.communicationState() == CommunicationState::DATA_STALE;
  FullSafetyResult safety = evaluateFullSafety(
      decision, hasTank, tankPercent, kEmergencyStopActive, kControllerFaultActive, dataStale, isStartup,
      kConfiguredSafeFanState);

  previousPumpRequested = decision.requestedPump;

  // Roadmap task 35: servo is the only physical actuator this slice
  // drives. Pump/fan are reported only -- see file header.
  windowServo.write(safety.commandedWindowDeg);

  updateStatusPixels(safety.alarmLevel);
  if (previousAlarmLevel != safety.alarmLevel) {
    soundAlarmChangeTone(safety.alarmLevel);
    previousAlarmLevel = safety.alarmLevel;
  }

  showOnOled(temperatureC, hasMoisture, moisturePercent, hasTank, tankPercent, decision, safety);

  shared.events.push(nowMs, "DECISION", decision.temperatureReason + " | " + decision.irrigationReason);
  if (safety.overrideCode != nullptr) {
    shared.events.push(nowMs, "SAFETY_OVERRIDE", safety.overrideCode);
  }

  JsonDocument response;
  response["accepted"] = true;
  response["sequence"] = sequence;
  response["mode"] = safety.appliedPriority == SafetyPriority::AUTOMATIC_OPERATION ? "automatic" : "safety_override";
  response["alarm_level"] = safety.alarmLevel;
  JsonObject commands = response["commands"].to<JsonObject>();
  commands["fan"] = safety.commandedFan;
  commands["window_angle"] = safety.commandedWindowDeg;
  commands["pump"] = safety.commandedPump;
  JsonArray triggeredRules = response["triggered_rules"].to<JsonArray>();
  triggeredRules.add(decision.temperatureRule);
  triggeredRules.add(decision.irrigationRule);
  JsonArray reasons = response["reasons"].to<JsonArray>();
  reasons.add(decision.temperatureReason);
  reasons.add(decision.irrigationReason);
  if (safety.overrideCode != nullptr) {
    triggeredRules.add(safety.overrideCode);
    reasons.add(String("Safety override: ") + safety.overrideCode);
  }
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
  statusPixels.begin();

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
