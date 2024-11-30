import paho.mqtt.client as mqtt
import pygame
import time

# Konfigurasi MQTT
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC_DIRECTION = "motor/direction"
TOPIC_GAS = "motor/gas"

# Inisialisasi Joystick
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("Tidak ada joystick yang terdeteksi!")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Joystick terdeteksi: {joystick.get_name()}")

# Inisialisasi MQTT
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Terhubung ke broker MQTT!")
    else:
        print(f"Terhubung gagal dengan kode: {rc}")

client.on_connect = on_connect
client.connect(BROKER, PORT, 60)

# Fungsi utama kontrol
def control_motor():
    gas_status = False
    direction = ""

    while True:
        pygame.event.pump()  # Perbarui event joystick

        # Baca tombol gas (misalnya tombol A pada joystick)
        if joystick.get_button(0):  # Tombol A
            if not gas_status:
                gas_status = True
                client.publish(TOPIC_GAS, "start")
                print("Gas dinyalakan!")
        else:
            if gas_status:
                gas_status = False
                client.publish(TOPIC_GAS, "stop")
                print("Gas dimatikan!")

        # Baca arah dari joystick analog (misalnya Y-axis)
        y_axis = joystick.get_axis(1)  # Sumbu Y

        if y_axis < -0.5:  # Joystick ke atas
            if direction != "maju":
                direction = "maju"
                client.publish(TOPIC_DIRECTION, "maju")
                print("Motor maju")
        elif y_axis > 0.5:  # Joystick ke bawah
            if direction != "mundur":
                direction = "mundur"
                client.publish(TOPIC_DIRECTION, "mundur")
                print("Motor mundur")
        else:  # Joystick di tengah
            if direction != "":
                direction = ""
                print("Arah tidak berubah")

        time.sleep(0.1)  # Debounce loop

# Jalankan fungsi kontrol
try:
    control_motor()
except KeyboardInterrupt:
    print("\nKontrol dihentikan.")
finally:
    pygame.quit()
    client.disconnect()
