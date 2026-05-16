#include <WiFi.h>
#include "Adafruit_MQTT.h"
#include "Adafruit_MQTT_Client.h"

// --- WIFI SETUP ---
#define WLAN_SSID "GFiber_2.4_Coverage_D1617"
#define WLAN_PASS "8EB32B5D"

// --- ADAFRUIT IO SETUP ---
#define AIO_SERVER      "io.adafruit.com"
#define AIO_SERVERPORT  1883
#define AIO_USERNAME    "CaineJimenez"
#define AIO_KEY         "aio_MGZR666bEpMv2pI5e2BmhX83cN1E"

// --- HARDWARE PINS ---
const int relayPin = 4;
const int moisturePin = 32;
const int greenLedPin = 25;  // Wet Status
const int yellowLedPin = 26; // Perfect Status
const int redLedPin = 27;    // Dry Status

// --- CALIBRATION THRESHOLDS (Percentages) ---
const int dryThreshold = 35; // Below 35% is DRY
const int wetThreshold = 65; // Above 65% is WET

// --- MQTT SETUP ---
WiFiClient client;
Adafruit_MQTT_Client mqtt(&client, AIO_SERVER, AIO_SERVERPORT, AIO_USERNAME, AIO_KEY);
Adafruit_MQTT_Subscribe Example_Feed = Adafruit_MQTT_Subscribe(&mqtt, AIO_USERNAME "/feeds/Energy_Management_System");

void MQTT_connect();

void setup() {
  Serial.begin(115200);
  delay(10);
  
  pinMode(relayPin, OUTPUT);
  pinMode(greenLedPin, OUTPUT);
  pinMode(yellowLedPin, OUTPUT);
  pinMode(redLedPin, OUTPUT);
  pinMode(moisturePin, INPUT);

  // Default: Pump OFF (Active-Low relay)
  digitalWrite(relayPin, HIGH);

  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(WLAN_SSID);

  WiFi.begin(WLAN_SSID, WLAN_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected!");

  mqtt.subscribe(&Example_Feed);
}

void loop() {
  MQTT_connect();

  // --- 1. LOCAL DASHBOARD (Automatic Monitoring) ---
  int rawMoisture = analogRead(moisturePin);
  
  // Translate raw sensor values (2540 to 1400) into 0% to 100%
  // 2540 = Bone Dry (0%), 1400 = Soaking Wet (100%)
  int moisturePercent = map(rawMoisture, 2540, 1400, 0, 100);
  
  // Keep the percentage strictly between 0 and 100
  moisturePercent = constrain(moisturePercent, 0, 100);

  Serial.print("Soil Moisture: ");
  Serial.print(moisturePercent);
  Serial.println("%");

  // Update Indicator LEDs based on Percentage
  if (moisturePercent < dryThreshold) {
    // DRY (Red)
    digitalWrite(redLedPin, HIGH);
    digitalWrite(yellowLedPin, LOW);
    digitalWrite(greenLedPin, LOW);
  } 
  else if (moisturePercent >= dryThreshold && moisturePercent <= wetThreshold) {
    // PERFECT (Yellow)
    digitalWrite(redLedPin, LOW);
    digitalWrite(yellowLedPin, HIGH);
    digitalWrite(greenLedPin, LOW);
  } 
  else {
    // WET (Green)
    digitalWrite(redLedPin, LOW);
    digitalWrite(yellowLedPin, LOW);
    digitalWrite(greenLedPin, HIGH);
  }

  // --- 2. VOICE CONTROL (Manual Override via Cloud) ---
  Adafruit_MQTT_Subscribe *subscription;
  while ((subscription = mqtt.readSubscription(2000))) {
    if (subscription == &Example_Feed) {
      Serial.print("Voice Command Received: ");
      Serial.println((char *)Example_Feed.lastread);

      if (!strcmp((char*) Example_Feed.lastread, "ON")) {
        digitalWrite(relayPin, LOW);   // Pump ON
        Serial.println(">>> Pump ACTIVATED via Google Assistant");
      } 
      else if (!strcmp((char*) Example_Feed.lastread, "OFF")) {
        digitalWrite(relayPin, HIGH);  // Pump OFF
        Serial.println(">>> Pump DEACTIVATED via Google Assistant");
      }
    }
  }
}

void MQTT_connect() {
  int8_t ret;
  if (mqtt.connected()) return;

  Serial.print("Connecting to Adafruit IO... ");
  uint8_t retries = 5;
  while ((ret = mqtt.connect()) != 0) {
    Serial.println(mqtt.connectErrorString(ret));
    Serial.println("Retrying in 5 seconds...");
    mqtt.disconnect();
    delay(5000);
    retries--;
    if (retries == 0) while (1);
  }
  Serial.println("Adafruit IO Connected!");
}
