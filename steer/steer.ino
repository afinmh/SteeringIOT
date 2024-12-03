#include <WiFi.h>
#include <PubSubClient.h>
#include <WebServer.h>

// Konfigurasi WiFi
const char* ssid = "ICT_LAB";
const char* password = "ICTLAB2023";

// Konfigurasi MQTT
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* topic_direction = "motorffitenass/direction";
const char* topic_gas = "motorffitenass/gas";
const char* topic_steer = "motorffitenass/steer";
const char* topic_distance = "motorffitenass/distance";

// Objek WiFi, MQTT, dan Web Server
WiFiClient espClient;
PubSubClient client(espClient);
WebServer server(80);

// Pin motor driver
const int motorPin1 = 26;  // GPIO 26
const int motorPin2 = 27;  // GPIO 27
const int motorPin3 = 22;
const int motorPin4 = 23;

// Pin sensor ultrasonik
const int trigPin = 18;
const int echoPin = 19;

// Status kontrol
String steer = "";
String direction = "";  // "maju" atau "mundur"
bool gasPressed = false;
float distance = 0.0; // Variabel jarak
unsigned long lastDistanceUpdate = 0; // Waktu pembaruan terakhir

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

// Fungsi membaca jarak dari sensor ultrasonik
float readUltrasonicDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH);
  float distance = (duration * 0.034) / 2; // Konversi ke cm
  return distance;
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
    if (message == "start") {
      gasPressed = true;
    } else if (message == "stop") {
      gasPressed = false;
    }
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

// Halaman utama untuk web server
void handleRoot() {
  String html = "<html>\
                  <head><title>Motor & Sensor Status</title></head>\
                  <body>\
                    <h1>Status Kontrol</h1>\
                    <p><b>WiFi IP:</b> " + WiFi.localIP().toString() + "</p>\
                    <p><b>MQTT Status:</b> " + (client.connected() ? "Connected" : "Disconnected") + "</p>\
                    <p><b>Gas:</b> " + String(gasPressed ? "ON" : "OFF") + "</p>\
                    <p><b>Direction:</b> " + direction + "</p>\
                    <p><b>Steering:</b> " + steer + "</p>\
                    <p><b>Distance (cm):</b> " + String(distance, 2) + " cm</p>\
                  </body>\
                </html>";
  server.send(200, "text/html", html);
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

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  server.on("/", handleRoot);
  server.begin();
  Serial.println("Web server started!");
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  server.handleClient();

  // Kontrol motor berdasarkan status gas dan arah
  if (gasPressed) {
    if (direction == "maju") {
      digitalWrite(motorPin1, HIGH);
      digitalWrite(motorPin2, LOW);
    } else if (direction == "mundur") {
      digitalWrite(motorPin1, LOW);
      digitalWrite(motorPin2, HIGH);
    }
  } else {
    digitalWrite(motorPin1, LOW);
    digitalWrite(motorPin2, LOW);
  }

  // Kontrol steer
  if (steer == "kanan") {
    digitalWrite(motorPin3, HIGH);
    digitalWrite(motorPin4, LOW);
  } else if (steer == "kiri") {
    digitalWrite(motorPin3, LOW);
    digitalWrite(motorPin4, HIGH);
  } else {
    digitalWrite(motorPin3, LOW);
    digitalWrite(motorPin4, LOW);
  }

  // Update jarak setiap 10 detik
  if (millis() - lastDistanceUpdate > 10000) {
    distance = readUltrasonicDistance();
    Serial.println("Distance: " + String(distance) + " cm");
    client.publish(topic_distance, String(distance, 2).c_str());
    lastDistanceUpdate = millis();
  }
}
