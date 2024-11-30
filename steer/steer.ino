#include <WiFi.h>
#include <PubSubClient.h>

// Konfigurasi WiFi
const char* ssid = "Arthaloka";
const char* password = "arthaloka_WO";

const char* mqtt_server = "broker.hivemq.com"; // Alamat broker HiveMQ
const int mqtt_port = 1883; // Port MQTT HiveMQ (Non-TLS)
const char* topic_direction = "motorffitenass/direction";  // Arah motor
const char* topic_gas = "motorffitenass/gas";              // Status gas
const char* topic_steer = "motorffitenass/steer";              // Status gas

// Objek WiFi dan MQTT
WiFiClient espClient;
PubSubClient client(espClient);

// Pin motor driver
const int motorPin1 = 26;  // GPIO 26
const int motorPin2 = 27;  // GPIO 27
const int motorPin3 = 22;
const int motorPin4 = 23;

// Status kontrol
String steer = "";
String direction = "";  // "maju" atau "mundur"
bool gasPressed = false;

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

// Callback ketika pesan diterima
void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  Serial.println("Pesan diterima: " + String(topic) + " -> " + message);

  // Arah motor
  if (String(topic) == topic_direction) {
    direction = message;
    Serial.println("Direction set to: " + direction);
  }

  if (String(topic) == topic_steer) {
    steer = message;
    Serial.println("Steering set to: " + steer);
  }

  // Gas motor
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
    if (client.connect("ESP32_MotorController")) {
      Serial.println("Connected!");
      client.subscribe(topic_direction); // Berlangganan topik arah
      client.subscribe(topic_gas); 
      client.subscribe(topic_steer);       // Berlangganan topik gas
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

  // Hubungkan ke WiFi
  setupWiFi();

  // Konfigurasi MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  // Konfigurasi pin motor sebagai output
  pinMode(motorPin1, OUTPUT);
  pinMode(motorPin2, OUTPUT);
  pinMode(motorPin3, OUTPUT);
  pinMode(motorPin4, OUTPUT);
}

void loop() {
  // Hubungkan ke broker MQTT jika terputus
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  if (steer == "kanan") {
    digitalWrite(motorPin3, HIGH);
    digitalWrite(motorPin4, LOW);
  } else if (steer == "kiri") {
    digitalWrite(motorPin3, LOW);
    digitalWrite(motorPin4, HIGH);
  } else if (steer == "netral") {
    // Matikan motor jika tombol gas dilepas
    digitalWrite(motorPin3, LOW);
    digitalWrite(motorPin4, LOW);
  }

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
    // Matikan motor jika tombol gas dilepas
    digitalWrite(motorPin1, LOW);
    digitalWrite(motorPin2, LOW);
  }
}