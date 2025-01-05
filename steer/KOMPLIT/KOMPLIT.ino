#include <WiFi.h>
#include <PubSubClient.h>
#include <HTTPClient.h>
#include <DFRobotDFPlayerMini.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>

// Konfigurasi WiFi
const char* ssid = "Wong Ayu";
const char* password = "4sehat5sempurna";

// Konfigurasi MQTT
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* topic_sensor = "motorffitenass/sensor";

WebSocketsClient webSocket;
WiFiClient espClient;
PubSubClient client(espClient);

// Pin motor driver
const int motorPin1 = 26;  // GPIO 26
const int motorPin2 = 27;  // GPIO 27
const int motorPin3 = 22;
const int motorPin4 = 23;
const int ledPin = 2;  


// Pin sensor ultrasonik
#define TRIG_PIN 5 
#define ECHO_PIN 18 

#define PUMP_RELAY_PIN 32
#define STROBE_RELAY_PIN 33

// Setup komunikasi serial dengan DFPlayer
HardwareSerial mySerial(1);  // Menggunakan UART1 (RX=16, TX=17)
DFRobotDFPlayerMini myDFPlayer;

// Variabel untuk status musik dan DFPlayer
bool isPlaying = false;
bool isDFPlayerReady = false;

// Status kontrol
String steer = "";
String direction = "";  // "maju" atau "mundur"
String gass = "";
String pompa = "OFF";
String strobo = "OFF";
String speaker = "OFF";
String fire = "Aman";
int batre = 100;
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

  Serial.println("Pesan diterima: -> " + message);
}

// Fungsi untuk menghubungkan ke broker MQTT
void setupMQTT() {
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("ESP32_Controller")) {
      Serial.println("Connected!");
      client.subscribe(topic_sensor);
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Retry in 5 seconds...");
      delay(5000);
    }
  }
}

void handleWebSocketMessage(uint8_t num, uint8_t* payload, size_t length) {
  String message = "";
  for (size_t i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  StaticJsonDocument<200> doc;

  DeserializationError error = deserializeJson(doc, message);

  if (error) {
    Serial.println("Deserialization failed: " + String(error.c_str()));
    return;
  }

  const char* topic = doc["topic"];
  const char* value = doc["value"];

  if (String(topic) == "gas") {
    gass = String(value);
    Serial.println("Gas set to: " + gass);
  } else if (String(topic) == "direction") {
    direction = String(value);
    Serial.println("Direction set to: " + direction);
  } else if (String(topic) == "strobo") {
    strobo = String(value);
    Serial.println("Strobo: " + strobo);
  } else if (String(topic) == "pompa") {
    pompa = String(value);
    Serial.println("Pompa: " + pompa);
  } else if (String(topic) == "steer") {
    steer = String(value);
    Serial.println("Steering set to: " + steer);
  } else if (String(topic) == "fire") {
    fire = String(value);
    Serial.println("Deteksi: " + fire);
  } else if (String(topic) == "sound") {
    if (isDFPlayerReady) {
      String valueString = String(value);
      int soundIndex = valueString.toInt();
      Serial.println(soundIndex);
      if (soundIndex > 0) {
        Serial.println("Memainkan musik ke-" + String(soundIndex));
        myDFPlayer.play(soundIndex);
        speaker = "ON";
      } else {
        myDFPlayer.stop();
        Serial.println("Input sound tidak valid: " + String(value));
        speaker = "OFF";
      }
    } else {
      Serial.println("DFPlayer belum siap");
    }
  }
}


void webSocketEvent(WStype_t type, uint8_t* payload, size_t length) {
  switch (type) {
    case WStype_CONNECTED:
      webSocket.sendTXT("{\"type\": \"receiver\"}");
      Serial.println("Connected to WebSocket server.");
      break;
    case WStype_DISCONNECTED:
      Serial.println("Disconnected from WebSocket server.");
      break;
    case WStype_TEXT:
      handleWebSocketMessage(0, payload, length);
      break;
    default:
      break;
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

void TaskWebSocket(void *parameter) {
    for (;;) {
        webSocket.loop();
        delay(1);
    }
}

void TaskMQTT(void *parameter) {
    for (;;) {
        if (!client.connected()) {
            setupMQTT();
        }
        client.loop();
        if (millis() - lastDistanceUpdate > 1000) {
          distance = readUltrasonicDistance();
          Serial.println("Distance: " + String(distance) + " cm");
          String jsonData = "{\"pompa\":\"" + pompa + "\",\"strobo\":\"" + strobo + "\",\"speaker\":\"" + speaker + "\",\"fire\":\"" + fire + "\",\"batre\":\"" + batre + "\",\"distance\":" + distance + "}";
          client.publish(topic_sensor, jsonData.c_str());
          batre -= 1;
          lastDistanceUpdate = millis();
        }
        delay(1);
    }
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
  pinMode(ledPin, OUTPUT);
  pinMode(PUMP_RELAY_PIN, OUTPUT);
  pinMode(STROBE_RELAY_PIN, OUTPUT);

  // Pastikan relay awalnya dalam keadaan off
  digitalWrite(PUMP_RELAY_PIN, LOW);
  digitalWrite(STROBE_RELAY_PIN, LOW);

  mySerial.begin(9600, SERIAL_8N1, 16, 17);

  setupWiFi();
  // setupMQTT();
  // initializeDFPlayer();
  webSocket.begin("192.168.1.10", 8765, "/");
  webSocket.onEvent(webSocketEvent);
  xTaskCreatePinnedToCore(TaskWebSocket, "WebSocketTask", 10000, NULL, 1, NULL, 0);
  xTaskCreatePinnedToCore(TaskMQTT, "MQTTTask", 10000, NULL, 1, NULL, 1);
}

void loop() {
  // if (!client.connected()) {
  //   setupMQTT();
  // }
  // client.loop();

  // Kontrol motor berdasarkan nilai direction, steer, dan gas
  if (direction == "maju" && gass == "start") {
    digitalWrite(ledPin, HIGH);
    digitalWrite(motorPin1, HIGH);
    digitalWrite(motorPin2, LOW);
  } else if (direction == "mundur" && gass == "start") {
    digitalWrite(ledPin, HIGH);
    digitalWrite(motorPin1, LOW);
    digitalWrite(motorPin2, HIGH);
  } else {
    digitalWrite(ledPin, LOW);
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

  if (pompa == "ON") {
    digitalWrite(ledPin, HIGH);
    digitalWrite(PUMP_RELAY_PIN, HIGH);
  } else if (pompa == "OFF") {
    digitalWrite(PUMP_RELAY_PIN, LOW);
  }

  if (strobo == "ON") {
    digitalWrite(ledPin, HIGH);
    digitalWrite(STROBE_RELAY_PIN, HIGH);
  } else if (strobo == "OFF") {
    digitalWrite(STROBE_RELAY_PIN, LOW);
  }

  // if (distance < 50.0 && !isPlaying) {
  //   Serial.println("Jarak kurang dari 50 cm, memainkan musik 2...");
  //   myDFPlayer.play(2);  // Mainkan musik 2
  //   speaker = "ON";
  //   isPlaying = true;
  // } else if (distance >= 50.0 && isPlaying) {
  //   Serial.println("Jarak lebih dari 50 cm, menghentikan musik...");
  //   myDFPlayer.stop();  // Hentikan musik
  //   speaker = "OFF";
  //   isPlaying = false;
  // }
}
