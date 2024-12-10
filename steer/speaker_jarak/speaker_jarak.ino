#include <DFRobotDFPlayerMini.h>

// Pin untuk sensor ultrasonik
#define TRIG_PIN 5  // Pin Trig ke GPIO5 ESP32
#define ECHO_PIN 18 // Pin Echo ke GPIO18 ESP32

// Setup komunikasi serial dengan DFPlayer
HardwareSerial mySerial(1);  // Menggunakan UART1 (atau UART2, jika diperlukan)
DFRobotDFPlayerMini myDFPlayer;

// Variabel untuk status musik dan DFPlayer
bool isPlaying = false;
bool isDFPlayerReady = false;

void setup() {
  // Serial untuk debugging
  Serial.begin(115200);

  // Konfigurasi pin ultrasonik
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // Serial untuk DFPlayer
  mySerial.begin(9600, SERIAL_8N1, 16, 17);  // RX=16, TX=17 untuk DFPlayer
  
  // Inisialisasi DFPlayer
  initializeDFPlayer();
}

void loop() {
  // Jika DFPlayer tidak siap, coba sambungkan kembali
  if (!isDFPlayerReady) {
    Serial.println("DFPlayer not ready, retrying...");
    initializeDFPlayer();
    delay(1000); // Tunggu sebelum mencoba lagi
    return;      // Jangan melanjutkan loop jika DFPlayer belum siap
  }

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

  // Menampilkan jarak ke Serial Monitor
  Serial.print("Jarak: ");
  Serial.print(distance);
  Serial.println(" cm");

  // Logika kontrol musik berdasarkan jarak
  if (distance < 50.0 && !isPlaying) {
    Serial.println("Jarak kurang dari 50 cm, memainkan musik 2...");
    myDFPlayer.play(2);  // Mainkan musik 2
    isPlaying = true;
  } else if (distance >= 50.0 && isPlaying) {
    Serial.println("Jarak lebih dari 50 cm, menghentikan musik...");
    myDFPlayer.stop();  // Hentikan musik
    isPlaying = false;
  }

  delay(1000); // Delay 1 detik sebelum pembacaan berikutnya
}

// Fungsi untuk menginisialisasi DFPlayer
void initializeDFPlayer() {
  if (myDFPlayer.begin(mySerial)) {
    Serial.println("DFPlayer is ready!");
    isDFPlayerReady = true; // Tandai DFPlayer sebagai siap
    myDFPlayer.volume(30);
  } else {
    Serial.println("Failed to detect DFPlayer. Will retry...");
    isDFPlayerReady = false; // Tandai DFPlayer sebagai tidak siap
  }
}
