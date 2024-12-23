#include <WiFi.h>
#include <PubSubClient.h>
#include <HTTPClient.h>

// Konfigurasi WiFi
const char* ssid = "Afin";
const char* password = "12345678";

// Konfigurasi MQTT
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* topic_direction = "motorffitenass/direction";
const char* topic_gas = "motorffitenass/gas";
const char* topic_steer = "motorffitenass/steer";

// Objek WiFi, MQTT, dan Web Server
WiFiClient espClient;
PubSubClient client(espClient);

// Pin motor driver
const int motorPin1 = 26;  // GPIO 26
const int motorPin2 = 27;  // GPIO 27
const int motorPin3 = 22;
const int motorPin4 = 23;
const int ledPin = 2;   

// Status kontrol
String steer = "";
String direction = "";  // "maju" atau "mundur"
String gass = "";

// Fungsi untuk menghubungkan ke WiFi
void setupWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi!");
  Serial.println("IP Address: " + WiFi.localIP().toString());
}


// Callback ketika pesan MQTT diterima
void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  Serial.println("Pesan diterima: " + String(topic) + " -> " + message);

  if (String(topic) == topic_direction) {
    direction = message;
    Serial.println("Direction set to: " + direction);
  }

  if (String(topic) == topic_steer) {
    steer = message;
    Serial.println("Steering set to: " + steer);
  }

  if (String(topic) == topic_gas) {
    gass = message;
    Serial.println("Gas: " + message);
  }

}

// Fungsi untuk menghubungkan ke broker MQTT
void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("ESP32_Controller")) {
      Serial.println("Connected!");
      client.subscribe(topic_direction);
      client.subscribe(topic_gas);
      client.subscribe(topic_steer);
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Retry in 5 seconds...");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);

  setupWiFi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  pinMode(motorPin1, OUTPUT);
  pinMode(motorPin2, OUTPUT);
  pinMode(motorPin3, OUTPUT);
  pinMode(motorPin4, OUTPUT);
  pinMode(ledPin, OUTPUT);

}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  if (direction == "maju" && gass == "start"){
    digitalWrite(ledPin, HIGH);
    digitalWrite(motorPin1, HIGH);
    digitalWrite(motorPin2, LOW);
  } else if (direction == "mundur" && gass == "start"){
    digitalWrite(ledPin, HIGH);
    digitalWrite(motorPin1, HIGH);
    digitalWrite(motorPin2, LOW);
  } else {
    digitalWrite(ledPin, LOW);
    digitalWrite(motorPin1, LOW);
    digitalWrite(motorPin1, LOW);
    digitalWrite(motorPin2, LOW);
  }

  // Kontrol steer
  if (steer == "kanan") {
    digitalWrite(ledPin, HIGH);
    digitalWrite(motorPin3, HIGH);
    digitalWrite(motorPin4, LOW);
  } else if (steer == "kiri") {
    digitalWrite(ledPin, LOW);
    digitalWrite(motorPin3, LOW);
    digitalWrite(motorPin4, HIGH);
  } else {
    digitalWrite(motorPin3, LOW);
    digitalWrite(motorPin4, LOW);
  }

}
