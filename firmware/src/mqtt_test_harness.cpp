// MQTT hardware-verification harness (env:mqtt_test_harness) -- NOT a
// numbered blueprint roadmap task, and NOT a replacement for
// env:irrigation_slice's local-HTTP design. This exists for one reason:
// AgriControl's normal architecture assumes the tester is on the same
// local network as the ESP (a direct POST to its own HTTP server), but an
// AI agent with no physical presence and no local-network access has no
// way to reach that. This harness swaps the transport only -- sensor
// values arrive over MQTT instead of HTTP, and the computed state is
// published back over MQTT instead of returned as an HTTP response -- so
// that transport can be reached remotely over the public internet via an
// existing, already-working self-hosted Mosquitto broker.
//
// What does NOT change: the ESP is still the sole decision-making
// authority. firmware/include/irrigation.h (itself built on decision.h/
// safety.h, all already host-proven in logic/) is used completely
// unmodified -- this file only swaps how a sensor reading arrives and how
// the resulting state gets reported, never what computes it. No decision
// logic lives in this file. env:irrigation_slice, env:vertical_slice, and
// env:runtime are untouched by this file's existence.
//
// This is intentionally a near-duplicate of irrigation_slice.cpp with
// WebServer swapped for PubSubClient, following this project's existing
// convention of standalone, independently-reviewable stage/purpose files
// rather than a shared abstraction both would depend on (see
// irrigation_slice.cpp's own header: "Extends the Stage 5 vertical slice
// ... left unmodified").
//
// Protocol (deliberately separate from any other project's MQTT topics --
// this does not reuse or depend on esp32/command or esp32/state, which
// belong to a different firmware's LED/servo/sound command vocabulary):
//   Subscribes: agricontrol/sensor
//     Payload: the exact same JSON shape irrigation_slice.cpp's POST
//     /sensor accepts -- {"sequence": N, "values": {"temperature": ...,
//     "soil_moisture": ..., "water_level_percent": ..., "rain": ...}}
//     (temperature required, the rest optional).
//   Publishes: agricontrol/state
//     Payload: the exact same JSON shape irrigation_slice.cpp's HTTP
//     response returns -- {"accepted", "sequence", "mode", "alarm_level",
//     "commands": {"fan","window_angle","pump"}, "triggered_rules",
//     "reasons"} on success, or {"accepted": false, "error", "sequence"}
//     on rejection (sequence omitted if the message couldn't even be
//     parsed).
//
// Build/upload with: pio run -e mqtt_test_harness -t upload
// Needs firmware/include/secrets.h (WiFi) and
// firmware/include/mqtt_secrets.h (MQTT broker identity -- copy
// mqtt_secrets.h.example and fill in real values; never commit it). Never
// built or flashed from this environment -- treat as a reviewed draft,
// not verified working code, exactly like every other firmware file in
// this project, until it is actually flashed and observed on real
// hardware.
#include <string.h>

#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>
#include <PubSubClient.h>
#include <U8g2lib.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <Wire.h>

#include "irrigation.h"
#include "mqtt_secrets.h"
#include "pins.h"
#include "secrets.h"
#include "shared_state.h"

namespace {

// Same physically-plausible validation ranges as irrigation_slice.cpp --
// duplicated intentionally, not shared, per this file's header.
constexpr float kTemperatureMinC = -40.0f;
constexpr float kTemperatureMaxC = 85.0f;
constexpr float kPercentMin = 0.0f;
constexpr float kPercentMax = 100.0f;

constexpr bool kEmergencyStopActive = false;
constexpr bool kControllerFaultActive = false;
constexpr bool kConfiguredSafeFanState = false;

// LEDC-backed buzzer, not tone()/noTone() -- see irrigation_slice.cpp's
// identical comment for why.
constexpr int kBuzzerChannel = 5;
constexpr int kBuzzerPwmResolutionBits = 10;
bool buzzerAttached = false;
unsigned long buzzerOffAtMs = 0;

void playBuzzerTone(int frequency, int durationMs) {
  if (!buzzerAttached) {
    ledcSetup(kBuzzerChannel, 1000, kBuzzerPwmResolutionBits);
    ledcAttachPin(pins::BUZZER, kBuzzerChannel);
    buzzerAttached = true;
  }
  ledcWriteTone(kBuzzerChannel, frequency);
  buzzerOffAtMs = millis() + static_cast<unsigned long>(durationMs);
}

void serviceBuzzer(unsigned long nowMs) {
  if (buzzerOffAtMs != 0 && nowMs >= buzzerOffAtMs) {
    ledcWriteTone(kBuzzerChannel, 0);
    buzzerOffAtMs = 0;
  }
}

const char* kSensorTopic = "agricontrol/sensor";
const char* kStateTopic = "agricontrol/state";

WiFiClientSecure mqttSecureClient;
PubSubClient mqttClient(mqttSecureClient);
SharedState shared;
U8G2_SSD1306_128X64_NONAME_F_HW_I2C oled(U8G2_R0, U8X8_PIN_NONE);
Servo windowServo;
Adafruit_NeoPixel statusPixels(pins::NEOPIXEL_COUNT, pins::NEOPIXEL, NEO_GRB + NEO_KHZ800);

bool previousPumpRequested = false;
String previousAlarmLevel = "";
long lastPublishedSequence = -1;

bool inRange(float value, float minValue, float maxValue) { return value >= minValue && value <= maxValue; }

// Identical color mapping to irrigation_slice.cpp's updateStatusPixels --
// see that file for the rationale/caveat.
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

void soundAlarmChangeTone(const char* alarmLevel) {
  if (strcmp(alarmLevel, "critical") == 0) {
    playBuzzerTone(440, 400);
  } else if (strcmp(alarmLevel, "warning") == 0) {
    playBuzzerTone(660, 250);
  } else {
    playBuzzerTone(880, 120);
  }
}

void showOnOled(float temperatureC, bool hasMoisture, float moisturePercent, bool hasTank, float tankPercent,
                const FullSafetyResult& safety) {
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

void publishError(long sequence, bool haveSequence, const char* error) {
  JsonDocument doc;
  doc["accepted"] = false;
  doc["error"] = error;
  if (haveSequence) doc["sequence"] = sequence;
  String body;
  serializeJson(doc, body);
  mqttClient.publish(kStateTopic, body.c_str());
}

void rejectAndLog(long sequence, bool haveSequence, const char* error, unsigned long nowMs, const String& detail) {
  publishError(sequence, haveSequence, error);
  shared.events.push(nowMs, "REJECTED", detail);
  shared.recovery.recordFailure();
}

// Mirrors irrigation_slice.cpp's handleSensorPost() exactly, field for
// field, with the HTTP-specific parts (request body access, HTTP status
// codes) replaced by their MQTT equivalents (message payload, published
// state). The validation/decision/safety/actuation sequence itself is
// unchanged.
void handleSensorMessage(const String& body) {
  unsigned long nowMs = millis();

  JsonDocument doc;
  DeserializationError parseError = deserializeJson(doc, body);
  if (parseError) {
    rejectAndLog(0, false, "invalid JSON", nowMs, String("JSON parse error: ") + parseError.c_str());
    return;
  }

  if (!doc["sequence"].is<long>()) {
    rejectAndLog(0, false, "missing or invalid sequence", nowMs, "Missing or invalid sequence field");
    return;
  }
  long sequence = doc["sequence"].as<long>();
  if (shared.haveSequence && sequence <= static_cast<long>(shared.lastSequence)) {
    rejectAndLog(sequence, true, "duplicate or out-of-order sequence", nowMs, "Duplicate or out-of-order sequence");
    return;
  }

  JsonObject values = doc["values"];
  if (values.isNull() || !values["temperature"].is<float>()) {
    rejectAndLog(sequence, true, "missing or invalid temperature", nowMs, "Missing or invalid values.temperature");
    return;
  }

  for (JsonPair kv : values) {
    const char* key = kv.key().c_str();
    if (strcmp(key, "temperature") != 0 && strcmp(key, "soil_moisture") != 0 &&
        strcmp(key, "water_level_percent") != 0 && strcmp(key, "rain") != 0) {
      rejectAndLog(sequence, true, "unknown sensor field", nowMs, String("Unknown sensor field: ") + key);
      return;
    }
  }

  float temperatureC = values["temperature"].as<float>();
  if (!inRange(temperatureC, kTemperatureMinC, kTemperatureMaxC)) {
    rejectAndLog(sequence, true, "temperature out of range", nowMs, String("Temperature out of range: ") + temperatureC);
    return;
  }

  bool hasMoisture = values["soil_moisture"].is<float>();
  float moisturePercent = 0.0f;
  if (hasMoisture) {
    moisturePercent = values["soil_moisture"].as<float>();
    if (!inRange(moisturePercent, kPercentMin, kPercentMax)) {
      rejectAndLog(sequence, true, "soil_moisture out of range", nowMs, String("soil_moisture out of range: ") + moisturePercent);
      return;
    }
  }

  bool hasTank = values["water_level_percent"].is<float>();
  float tankPercent = 0.0f;
  if (hasTank) {
    tankPercent = values["water_level_percent"].as<float>();
    if (!inRange(tankPercent, kPercentMin, kPercentMax)) {
      rejectAndLog(sequence, true, "water_level_percent out of range", nowMs, String("water_level_percent out of range: ") + tankPercent);
      return;
    }
  }

  bool hasRain = values["rain"].is<float>();
  float rainValue = 0.0f;
  if (hasRain) {
    rainValue = values["rain"].as<float>();
    if (rainValue != 0.0f && rainValue != 1.0f) {
      rejectAndLog(sequence, true, "rain must be 0 or 1", nowMs, String("rain out of range: ") + rainValue);
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

  windowServo.write(safety.commandedWindowDeg);

  updateStatusPixels(safety.alarmLevel);
  if (previousAlarmLevel != safety.alarmLevel) {
    soundAlarmChangeTone(safety.alarmLevel);
    previousAlarmLevel = safety.alarmLevel;
  }

  showOnOled(temperatureC, hasMoisture, moisturePercent, hasTank, tankPercent, safety);

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
  mqttClient.publish(kStateTopic, responseBody.c_str());
  lastPublishedSequence = sequence;
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String body;
  body.reserve(length);
  for (unsigned int i = 0; i < length; i++) body += static_cast<char>(payload[i]);
  handleSensorMessage(body);
}

void connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  unsigned long started = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - started < 15000) {
    delay(250);
  }
}

void connectMqtt() {
  if (mqttClient.connected()) return;
  if (mqttClient.connect(MQTT_CLIENT_ID, MQTT_USER, MQTT_PASSWORD)) {
    mqttClient.subscribe(kSensorTopic, 1);
    shared.events.push(millis(), "MQTT_CONNECTED", kSensorTopic);
  }
}

}  // namespace

void setup() {
  Serial.begin(115200);
  Wire.begin(pins::I2C_SDA, pins::I2C_SCL);
  oled.begin();
  windowServo.attach(pins::CN3_SERVO);
  statusPixels.begin();

  shared.system.transitionTo(Mode::CONNECTING);
  shared.system.setCommunicationState(CommunicationState::CONNECTING);
  connectWiFi();
  shared.system.setCommunicationState(CommunicationState::ONLINE);
  shared.system.transitionTo(Mode::READY);
  shared.system.transitionTo(Mode::AUTOMATIC);
  shared.events.push(millis(), "WIFI_CONNECTED", WiFi.localIP().toString());

  // TLS posture matches every other MQTT-connected firmware this project
  // has read as reference: no cert pinning/validation.
  mqttSecureClient.setInsecure();
  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
  mqttClient.setBufferSize(1024);
  mqttClient.setCallback(mqttCallback);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) connectWiFi();
  if (WiFi.status() == WL_CONNECTED && !mqttClient.connected()) {
    connectMqtt();
  } else if (mqttClient.connected()) {
    mqttClient.loop();
  }

  shared.tick(millis());
  serviceBuzzer(millis());
}
