#include <WiFi.h>
#include <PubSubClient.h>
#include <WebSocketsServer.h>
#include <DFRobotDFPlayerMini.h>

// Konfigurasi WiFi
const char* ssid = "Wong Ayu";
const char* password = "4sehat5sempurna";

// Objek WiFi dan WebSocket Server
// WebSocketsServer webSocket = WebSocketsServer(81);

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

// DFPlayer
HardwareSerial mySerial(1); 
DFRobotDFPlayerMini myDFPlayer;
bool isDFPlayerReady = false;

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

// Fungsi untuk menginisialisasi DFPlayer
void initializeDFPlayer() {
  while (!isDFPlayerReady) {
    Serial.println("Mencoba mendeteksi DFPlayer...");
    if (myDFPlayer.begin(mySerial)) {
      Serial.println("DFPlayer is ready!");
      isDFPlayerReady = true;
      myDFPlayer.volume(30);  // Set volume (0 to 30)
    } else {
      Serial.println("Failed to detect DFPlayer. Retry in 2 seconds...");
      delay(2000);
    }
  }
}

// Callback WebSocket saat menerima pesan
#include <ArduinoJson.h>

void handleWebSocketMessage(uint8_t num, uint8_t* payload, size_t length) {
  String message = "";
  for (size_t i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  Serial.println("Pesan diterima: " + message);

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
  } else if (String(topic) == "steer") {
    steer = String(value);
    Serial.println("Steering set to: " + steer);
  } else if (String(topic) == "sound") {
    if (isDFPlayerReady) {
      String valueString = String(value);
      int soundIndex = valueString.toInt();
      Serial.println(soundIndex);
      if (soundIndex > 0) {
        Serial.println("Memainkan musik ke-" + String(soundIndex));
        myDFPlayer.play(soundIndex);
      } else {
        myDFPlayer.stop();
        Serial.println("Input sound tidak valid: " + String(value));
      }
    } else {
      Serial.println("DFPlayer belum siap");
    }
  }
}


// Fungsi untuk menangani event WebSocket
void onWebSocketEvent(uint8_t num, WStype_t type, uint8_t* payload, size_t length) {
  switch (type) {
    case WStype_TEXT:
      handleWebSocketMessage(num, payload, length);
      break;
    case WStype_DISCONNECTED:
      Serial.println("Client disconnected");
      break;
    case WStype_CONNECTED:
      Serial.println("Client connected");
      break;
    default:
      break;
  }
}

void setup() {
  Serial.begin(115200);

  setupWiFi();

  // Inisialisasi WebSocket
  webSocket.begin();
  webSocket.onEvent(onWebSocketEvent);

  // Inisialisasi pin motor driver
  pinMode(motorPin1, OUTPUT);
  pinMode(motorPin2, OUTPUT);
  pinMode(motorPin3, OUTPUT);
  pinMode(motorPin4, OUTPUT);
  pinMode(ledPin, OUTPUT);
  mySerial.begin(9600, SERIAL_8N1, 16, 17);

  // Inisialisasi DFPlayer
  initializeDFPlayer();
}

void loop() {
  // Jalankan WebSocket server
  webSocket.loop();

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
}
