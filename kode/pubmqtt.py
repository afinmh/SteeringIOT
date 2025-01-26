import pygame
import asyncio
import paho.mqtt.client as mqtt
import json

# MQTT broker address (ganti dengan broker yang sesuai)
MQTT_BROKER = "broker.hivemq.com"  # Anda bisa menggunakan broker publik seperti ini atau broker pribadi
MQTT_PORT = 1883
MQTT_TOPIC = "vehicle/control"

# Inisialisasi pygame dan joystick
pygame.init()
pygame.joystick.init()

# Pastikan ada joystick yang terdeteksi
if pygame.joystick.get_count() == 0:
    print("Tidak ada joystick yang terdeteksi!")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

# Variabel untuk melacak status joystick dan tombol
direction = ""
steer = "netral"
gas_status = False
button_pressed = False
music = 3
strobo = "OFF"
pompa = "OFF"

# MQTT callback functions
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}")
    # Subscribe to topics if needed
    # client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic: {msg.topic}")

# Connect to MQTT broker
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Async function to handle joystick input and send MQTT messages
async def send_mqtt_message():
    client.loop_start()  # Start the MQTT loop to handle message sending/receiving

    while True:
        pygame.event.get()  # Mengambil semua event pygame, termasuk input joystick
        global steer, gas_status

        # Arahkan motor maju/mundur
        if joystick.get_button(5):  # R1
            if direction != "maju":
                direction = "maju"
                client.publish(MQTT_TOPIC, json.dumps({"topic": "direction", "value": "maju"}))
                print("Motor maju")
        elif joystick.get_button(4):  # L1
            if direction != "mundur":
                direction = "mundur"
                client.publish(MQTT_TOPIC, json.dumps({"topic": "direction", "value": "mundur"}))
                print("Motor mundur")

        # Mengatur steer kiri/kanan/netral berdasarkan sumbu joystick
        steer_axis = joystick.get_axis(0)  # Joystick Bagian Kiri (Kiri Kanan)
        if steer_axis > 0.5:  # Joystick ke kanan
            if steer != "kanan":
                steer = "kanan"
                client.publish(MQTT_TOPIC, json.dumps({"topic": "steer", "value": "kanan"}))
                print("Belok Kanan")
        elif steer_axis < -0.5:  # Joystick ke kiri
            if steer != "kiri":
                steer = "kiri"
                client.publish(MQTT_TOPIC, json.dumps({"topic": "steer", "value": "kiri"}))
                print("Belok Kiri")
        else:  # Joystick di tengah atau netral
            if steer != "netral":
                steer = "netral"
                client.publish(MQTT_TOPIC, json.dumps({"topic": "steer", "value": "netral"}))
                print("Netral")

        # Mengatur gas (atas/bawah)
        pedal_axis = joystick.get_axis(1)  # Joystick bagian Kiri (Atas Bawah)
        if pedal_axis < -0.5:  # Joystick ke atas
            if not gas_status:
                gas_status = True
                client.publish(MQTT_TOPIC, json.dumps({"topic": "gas", "value": "start"}))
                print("Gas dinyalakan!")
        else:
            if gas_status:
                gas_status = False
                client.publish(MQTT_TOPIC, json.dumps({"topic": "gas", "value": "stop"}))
                print("Gas dimatikan!")

        # Kontrol untuk tombol
        if joystick.get_button(1):  # Lingkaran (2)
            if not button_pressed:
                client.publish(MQTT_TOPIC, json.dumps({"topic": "sound", "value": str(music)}))
                print(f"Telolet {music}")
            button_pressed = True

        if joystick.get_button(7):  # L2 Next lagu
            if not button_pressed:
                if music < 7:
                    music += 1
                    print(f"Music {music}")
                button_pressed = True

        if joystick.get_button(6):  # R2 Prev lagu
            if not button_pressed:
                if music > 3:
                    music -= 1
                    print(f"Music {music}")
                button_pressed = True

        if joystick.get_button(3):  # Kotak
            if not button_pressed:
                client.publish(MQTT_TOPIC, json.dumps({"topic": "sound", "value": "Stop"}))
                print("Stop")
            button_pressed = True

        if joystick.get_button(0):  # Segitiga
            if not button_pressed:
                if strobo == "OFF":
                    client.publish(MQTT_TOPIC, json.dumps({"topic": "strobo", "value": "ON"}))
                    strobo = "ON"
                    print("Strobo ON")
                elif strobo == "ON":
                    client.publish(MQTT_TOPIC, json.dumps({"topic": "strobo", "value": "OFF"}))
                    strobo = "OFF"
                    print("Strobo OFF")
            button_pressed = True

        if joystick.get_button(2):  # Silang
            if not button_pressed:
                if pompa == "OFF":
                    client.publish(MQTT_TOPIC, json.dumps({"topic": "pompa", "value": "ON"}))
                    print("Pompa ON")
                    pompa = "ON"
                elif pompa == "ON":
                    client.publish(MQTT_TOPIC, json.dumps({"topic": "pompa", "value": "OFF"}))
                    print("Pompa OFF")
                    pompa = "OFF"
            button_pressed = True

        # Reset tombol ketika tidak ada tombol yang ditekan
        if not joystick.get_button(6) and not joystick.get_button(7) and not joystick.get_button(1) and not joystick.get_button(3) and not joystick.get_button(0) and not joystick.get_button(2):
            button_pressed = False


# Menjalankan program
asyncio.get_event_loop().run_until_complete(send_mqtt_message())
