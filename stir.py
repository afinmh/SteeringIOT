import paho.mqtt.client as mqtt
import pygame
import time

# Konfigurasi MQTT
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC_DIRECTION = "motorffitenass/direction"
TOPIC_GAS = "motorffitenass/gas"
TOPIC_STEER = "motorffitenass/steer"
TOPIC_SOUND = "motorffitenass/sound"

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
client = mqtt.Client(protocol=mqtt.MQTTv311)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Terhubung ke broker MQTT!")
    else:
        print(f"Terhubung gagal dengan kode: {rc}")

client.on_connect = on_connect
client.connect(BROKER, PORT, 60)
client.loop_start()  # Memastikan event listener berjalan

# Fungsi utama kontrol
def control_motor():
    gas_status = False
    steer = ""
    direction = ""
    running = False  # Status untuk memulai/menghentikan kontrol

    while True:
        pygame.event.pump()  # Perbarui event joystick

        # Tombol untuk memulai kontrol (Button 9)
        if joystick.get_button(23):
            if not running:
                running = True
                print("Kontrol dimulai!")
                
        if joystick.get_button(6):
            client.publish(TOPIC_SOUND, "3")
            print("Telolet")
        
        if joystick.get_button(10):
            client.publish(TOPIC_SOUND, "Stop")
            print("Stop")

        # Tombol untuk menghentikan kontrol (Button 8)
        if joystick.get_button(8):
            print("Menghentikan kontrol...")
            # Reset nilai
            gas_status = False
            steer = ""
            direction = ""
            # Publish reset ke topik masing-masing
            client.publish(TOPIC_GAS, "stop")
            client.publish(TOPIC_DIRECTION, "")
            client.publish(TOPIC_STEER, "")
            print("Nilai reset dan program dihentikan.")

        if running:
            # Baca tombol gas (misalnya tombol A pada joystick)
            if joystick.get_button(4):  # Tombol A
                if direction != "maju":
                    direction = "maju"
                    client.publish(TOPIC_DIRECTION, "maju")
                    print("Motor maju")
            elif joystick.get_button(5):  # Tombol B
                if direction != "mundur":
                    direction = "mundur"
                    client.publish(TOPIC_DIRECTION, "mundur")
                    print("Motor mundur")

            # Baca arah dari joystick analog (misalnya Y-axis)
            steer_axis = joystick.get_axis(0)  # Sumbu Y

            # Threshold untuk menentukan perubahan
            THRESHOLD = 0.5

            # Logika untuk steer
            if steer_axis > THRESHOLD:  # Joystick ke kanan
                if steer != "kanan":
                    steer = "kanan"
                    client.publish(TOPIC_STEER, "kanan")
                    print("Belok Kanan")
            elif steer_axis < -THRESHOLD:  # Joystick ke kiri
                if steer != "kiri":
                    steer = "kiri"
                    client.publish(TOPIC_STEER, "kiri")
                    print("Belok Kiri")
            else:  # Joystick di tengah atau netral
                if steer != "netral":
                    steer = "netral"
                    client.publish(TOPIC_STEER, "netral")
                    print("Netral")

            # Baca pedal gas (misalnya Y-axis)
            pedal_axis = joystick.get_axis(1)  # Sumbu Y

            if pedal_axis < -0.5:  # Joystick ke atas
                if not gas_status:
                    gas_status = True
                    client.publish(TOPIC_GAS, "start")
                    print("Gas dinyalakan!")
            else:
                if gas_status:
                    gas_status = False
                    client.publish(TOPIC_GAS, "stop")
                    print("Gas dimatikan!")

            time.sleep(0.1)  # Debounce loop

# Jalankan fungsi kontrol
try:
    control_motor()
except KeyboardInterrupt:
    print("\nKontrol dihentikan.")
finally:
    pygame.quit()
    client.disconnect()
