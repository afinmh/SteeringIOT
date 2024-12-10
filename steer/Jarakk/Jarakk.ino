#define TRIG_PIN 5  // Pin Trig ke GPIO5 ESP32
#define ECHO_PIN 18 // Pin Echo ke GPIO18 ESP32

void setup() {
  Serial.begin(115200); // Serial Monitor
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
}

void loop() {
  // Mengirimkan sinyal trigger
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Menerima durasi pantulan sinyal ultrasonik
  long duration = pulseIn(ECHO_PIN, HIGH);

  // Menghitung jarak (dalam cm)
  float distance = (duration * 0.034) / 2;

  // Membatasi jarak minimum ke 20 cm
  if (distance < 20.0) {
    distance = 20.0;
  }

  // Menampilkan hasil ke Serial Monitor
  Serial.print("Jarak: ");
  Serial.print(distance);
  Serial.println(" cm");

  delay(1000); // Delay 1 detik sebelum pembacaan berikutnya
}
