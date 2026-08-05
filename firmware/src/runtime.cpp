// Stage 4 roadmap tasks 24-30: asynchronous runtime, shared state, events,
// stale-data detection, recovery, HTTP server, and request-size/validation
// limits (env:runtime).
//
// This is infrastructure only -- it does not call a decision engine or
// drive any actuator. Wiring the actual first vertical slice (virtual
// temperature -> decision -> servo/OLED/JSON response) is Stage 5
// (roadmap tasks 31-40), not this file. Validating sensor-specific ranges
// and full protocol semantics is also Stage 5 (roadmap task 33); this
// layer only enforces generic HTTP/JSON guardrails (size, parse success,
// sequence monotonicity, known field names).
//
// Requires firmware/include/secrets.h (copy secrets.h.example, fill in
// real WiFi credentials, do not commit) and the ArduinoJson library
// (declared in platformio.ini).
//
// Build/upload with: pio run -e runtime -t upload
// None of this has been built or flashed from this environment -- there is
// no PlatformIO toolchain, WiFi network, or physical board access here, so
// treat it as a reviewed draft, not verified working code.
#include <string.h>

#include <ArduinoJson.h>
#include <WebServer.h>
#include <WiFi.h>

#include "secrets.h"
#include "shared_state.h"

namespace {

// Roadmap task 30: request-size limit. Tunable, not a hardware fact.
//
// Known limitation found on recheck: WebServer.h reads and buffers the
// entire request body into RAM *before* handleSensorPost() runs, so this
// check rejects oversized bodies after they're already allocated, not
// before. It stops bad data from being processed, but does not by itself
// prevent memory pressure from a large body. True pre-buffer protection
// would need a streaming/upload handler (WebServer.h's onUpload-style API)
// or a switch to ESPAsyncWebServer -- not done here, to keep this draft
// small and reviewable.
constexpr size_t kMaxRequestBodyBytes = 2048;

// Roadmap-hardening fix, ported from mqtt_test_harness.cpp 2026-08-05
// after being found and validated there first: minimum gap between
// WiFi.begin() calls from loop(). Calling WiFi.begin() again while a
// connection attempt is already resolving produces "sta is connecting,
// return error" and can itself destabilize the connection.
constexpr unsigned long kWifiReconnectBackoffMs = 5000;
unsigned long lastWifiAttemptMs = 0;

void maintainWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;
  unsigned long nowMs = millis();
  if (nowMs - lastWifiAttemptMs < kWifiReconnectBackoffMs) return;
  lastWifiAttemptMs = nowMs;
  Serial.println("WiFi not connected, retrying...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

WebServer server(80);
SharedState shared;

const char* sensorIdName(SensorId id) {
  switch (id) {
    case SensorId::TEMPERATURE:
      return "temperature";
    case SensorId::SOIL_MOISTURE:
      return "soil_moisture";
    case SensorId::RAIN:
      return "rain";
    case SensorId::WATER_LEVEL_PERCENT:
      return "water_level_percent";
    default:
      return "";
  }
}

bool sensorIdFromName(const char* name, SensorId* outId) {
  for (uint8_t i = 0; i < static_cast<uint8_t>(SensorId::COUNT); i++) {
    SensorId id = static_cast<SensorId>(i);
    if (strcmp(name, sensorIdName(id)) == 0) {
      *outId = id;
      return true;
    }
  }
  return false;
}

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

void handleSensorPost() {
  unsigned long nowMs = millis();

  // Roadmap task 30: reject oversized/missing bodies before parsing.
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

  if (!doc["session_id"].is<const char*>()) {
    rejectAndLog(400, "missing or invalid session_id", nowMs, "Missing or invalid session_id field");
    return;
  }
  String sessionId = doc["session_id"].as<String>();
  if (!doc["sequence"].is<long>()) {
    rejectAndLog(400, "missing or invalid sequence", nowMs, "Missing or invalid sequence field");
    return;
  }
  long sequence = doc["sequence"].as<long>();
  if (!shared.acceptSequence(sessionId, sequence)) {
    rejectAndLog(400, "duplicate or out-of-order sequence", nowMs, "Duplicate or out-of-order sequence");
    return;
  }

  JsonObject values = doc["values"];
  if (values.isNull()) {
    rejectAndLog(400, "missing values object", nowMs, "Missing values object");
    return;
  }

  // Reject the whole message if it names a sensor we don't recognize.
  // Per-sensor range/type validation is Stage 5 (roadmap task 33).
  for (JsonPair kv : values) {
    SensorId id;
    if (!sensorIdFromName(kv.key().c_str(), &id)) {
      rejectAndLog(400, "unknown sensor field", nowMs, String("Unknown sensor field: ") + kv.key().c_str());
      return;
    }
  }

  for (JsonPair kv : values) {
    SensorId id;
    sensorIdFromName(kv.key().c_str(), &id);
    shared.sensors.update(id, kv.value().as<float>(), nowMs);
  }

  shared.lastSequence = static_cast<unsigned long>(sequence);
  shared.haveSequence = true;
  shared.recovery.recordValid();
  shared.events.push(nowMs, "ACCEPTED", String("sequence ") + sequence);

  JsonDocument response;
  response["accepted"] = true;
  response["sequence"] = sequence;
  String responseBody;
  serializeJson(response, responseBody);
  server.send(200, "application/json", responseBody);
}

void handleNotFound() { sendJsonError(404, "not found"); }

}  // namespace

void setup() {
  Serial.begin(115200);

  shared.system.transitionTo(Mode::CONNECTING);
  shared.system.setCommunicationState(CommunicationState::CONNECTING);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  // No connect-timeout/fallback safe state yet: if WiFi never connects the
  // board stays in CONNECTING and never serves HTTP. Worth adding once
  // credentials are confirmed and this can be tested against real hardware.
  while (WiFi.status() != WL_CONNECTED) {
    delay(200);
  }
  shared.system.setCommunicationState(CommunicationState::ONLINE);
  shared.system.transitionTo(Mode::READY);
  shared.system.transitionTo(Mode::AUTOMATIC);
  shared.events.push(millis(), "WIFI_CONNECTED", WiFi.localIP().toString());
  Serial.print("WiFi connected, IP: ");
  Serial.println(WiFi.localIP());

  server.on("/sensor", HTTP_POST, handleSensorPost);
  server.onNotFound(handleNotFound);
  server.begin();
}

void loop() {
  maintainWiFi();
  server.handleClient();
  shared.tick(millis());
}
