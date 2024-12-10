#include <DFRobotDFPlayerMini.h>

// Setup komunikasi serial dengan DFPlayer
HardwareSerial mySerial(1);  // Menggunakan UART1 (atau UART2, jika diperlukan)
DFRobotDFPlayerMini myDFPlayer;

void setup() {
  // Memulai komunikasi serial untuk debugging dan input/output
  Serial.begin(115200);  // Serial monitor untuk debugging
  mySerial.begin(9600, SERIAL_8N1, 16, 17);  // RX=16, TX=17 untuk DFPlayer
  
  if (!myDFPlayer.begin(mySerial)) {
    Serial.println("DFPlayer not detected!");
    while(true);
  }
  Serial.println("DFPlayer is ready!");

  // Menunggu input dari terminal
  Serial.println("Enter command to play song:");
  Serial.println("1: Play Song 1");
  Serial.println("2: Play Song 2");
  Serial.println("3: Play Song 3");
}

void loop() {
  // Cek apakah ada input di serial monitor
  if (Serial.available()) {
    int command = Serial.read();  // Membaca input dari terminal

    if (command == '1') {
      Serial.println("Playing Song 1...");
      myDFPlayer.play(1);  // Mainkan lagu 1
    }
    else if (command == '2') {
      Serial.println("Playing Song 2...");
      myDFPlayer.play(2);  // Mainkan lagu 2
    }
    else if (command == '3') {
      Serial.println("Playing Song 3...");
      myDFPlayer.play(3);  // Mainkan lagu 3
    }
    else if (command == 's'){
      Serial.println("Music Stop");
      myDFPlayer.stop();  // Mainkan lagu 3
    }
    else {
      Serial.println("Invalid command. Please enter 1, 2, or 3.");
    }
  }
}
