import paho.mqtt.client as mqtt
import json

# Konfigurasi MQTT
MQTT_BROKER = "broker.hivemq.com"  # Anda bisa menggunakan broker publik atau private
MQTT_PORT = 1883
MQTT_TOPIC = "vehicle/control"  # Topik yang akan disubscribe

# Callback function ketika terhubung dengan broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}")
    # Subscribe ke topik yang ingin didengarkan
    client.subscribe(MQTT_TOPIC)
    print(f"Subscribed to {MQTT_TOPIC}")

# Callback function ketika pesan diterima
def on_message(client, userdata, msg):
    # Mencetak payload pesan yang diterima dari broker
    message = msg.payload.decode()
    print(f"Received message: {message} on topic: {msg.topic}")

# Inisialisasi client MQTT
client = mqtt.Client()

# Menetapkan callback untuk koneksi dan pesan
client.on_connect = on_connect
client.on_message = on_message

# Koneksi ke broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Mulai loop untuk mendengarkan pesan
client.loop_forever()
