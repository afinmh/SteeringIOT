#include <WiFi.h>
#include <PubSubClient.h>
#include <HTTPClient.h>
#include <DFRobotDFPlayerMini.h>

// Konfigurasi WiFi
const char* ssid = "ICT-LAB WORKSPACE";
const char* password = "ICTLAB2024";

// Konfigurasi MQTT
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* topic_direction = "motorffitenass/direction";
const char* topic_gas = "motorffitenass/gas";
const char* topic_steer = "motorffitenass/steer";
const char* topic_distance = "motorffitenass/distance";
const char* topic_sound = "motorffitenass/sound";

// Objek WiFi, MQTT, dan Web Server
WiFiClient espClient;
PubSubClient client(espClient);

// Pin motor driver
const int motorPin1 = 26;  // GPIO 26
const int motorPin2 = 27;  // GPIO 27
const int motorPin3 = 22;
const int motorPin4 = 23;

// Pin sensor ultrasonik
#define TRIG_PIN 5  // Pin Trig ke GPIO5 ESP32
#define ECHO_PIN 18 // Pin Echo ke GPIO18 ESP32

// Setup komunikasi serial dengan DFPlayer
HardwareSerial mySerial(1);  // Menggunakan UART1 (RX=16, TX=17)
DFRobotDFPlayerMini myDFPlayer;

// Variabel untuk status musik dan DFPlayer
bool isPlaying = false;
bool isDFPlayerReady = false;

// Status kontrol
String steer = "";
String direction = "";  // "maju" atau "mundur"
bool gasPressed = false;
float distance = 0.0; // Variabel jarak
unsigned long lastDistanceUpdate = 0; // Waktu pembaruan terakhir

// Fungsi untuk menghubungkan ke WiFi
void setupWiFi() {
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print("Connecting to WiFi...");
    WiFi.begin(ssid, password);
    for (int i = 0; i < 10; i++) {
      if (WiFi.status() == WL_CONNECTED) break;
      delay(500);
      Serial.print(".");
    }
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
    gasPressed = (message == "start");
    Serial.println("Gas: " + message);
  }

  if (String(topic) == topic_sound) {
    if (isDFPlayerReady) {
      int soundIndex = message.toInt();
      if (soundIndex > 0) {
        Serial.println("Memainkan musik ke-" + String(soundIndex));
        myDFPlayer.play(soundIndex);
      } else {
        myDFPlayer.stop();
        Serial.println("Input sound tidak valid: " + message);
      }
    } else {
      Serial.println("DFPlayer belum siap");
    }
  }
}

// Fungsi untuk menghubungkan ke broker MQTT
void setupMQTT() {
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("ESP32_Controller")) {
      Serial.println("Connected!");
      client.subscribe(topic_direction);
      client.subscribe(topic_gas);
      client.subscribe(topic_steer);
      client.subscribe(topic_sound);
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Retry in 5 seconds...");
      delay(5000);
    }
  }
}

// Fungsi membaca jarak dari sensor ultrasonik
float readUltrasonicDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH);
  float distance = (duration * 0.034) / 2; // Konversi ke cm
  return distance;
}

// Fungsi untuk menginisialisasi DFPlayer
void initializeDFPlayer() {
  while (!isDFPlayerReady) {
    Serial.println("Mencoba mendeteksi DFPlayer...");
    if (myDFPlayer.begin(mySerial)) {
      Serial.println("DFPlayer is ready!");
      isDFPlayerReady = true;
      myDFPlayer.volume(30);
    } else {
      Serial.println("Failed to detect DFPlayer. Retry in 2 seconds...");
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);

  // Inisialisasi pin
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(motorPin1, OUTPUT);
  pinMode(motorPin2, OUTPUT);
  pinMode(motorPin3, OUTPUT);
  pinMode(motorPin4, OUTPUT);

  mySerial.begin(9600, SERIAL_8N1, 16, 17);

  setupWiFi();
  setupMQTT();
  initializeDFPlayer();
}

void loop() {
  if (!client.connected()) {
    setupMQTT();
  }
  client.loop();

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
  if (millis() - lastDistanceUpdate > 1000) {
    distance = readUltrasonicDistance();
    Serial.println("Distance: " + String(distance) + " cm");
    client.publish(topic_distance, String(distance, 2).c_str());
    lastDistanceUpdate = millis();
  }

  if (distance < 50.0 && !isPlaying) {
    Serial.println("Jarak kurang dari 50 cm, memainkan musik 2...");
    myDFPlayer.play(2);  // Mainkan musik 2
    isPlaying = true;
  } else if (distance >= 50.0 && isPlaying) {
    Serial.println("Jarak lebih dari 50 cm, menghentikan musik...");
    myDFPlayer.stop();  // Hentikan musik
    isPlaying = false;
  }
}
