import random
import time
import json
import paho.mqtt.client as mqtt

# Konfigurasi MQTT
broker = "broker.hivemq.com"  # Broker MQTT publik
port = 1883                   # Port MQTT

# Topik MQTT
topics = {
    "steer": "sensormobilapi/steer",
    "direction": "sensormobilapi/direction",
    "gaspressed": "sensormobilapi/gaspressed",
    "distance": "sensormobilapi/distance",
}

# Fungsi untuk menghasilkan data dummy
def generate_dummy_data():
    steer = random.choice(["Kiri", "Kanan"])  # Simulasi steer: kiri atau kanan
    direction = random.choice(["Maju", "Mundur"])  # Simulasi direction: maju atau mundur
    gaspressed = random.choice([True, False])  # Simulasi gaspressed: ditekan atau tidak
    distance = round(random.uniform(10.0, 300.0), 2)  # Simulasi jarak ultrasonic (cm)
    return {
        "steer": {"steer": steer},
        "direction": {"direction": direction},
        "gaspressed": {"gaspressed": gaspressed},
        "distance": {"distance": distance},
    }

# Callback ketika berhasil terhubung ke broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Terhubung ke broker MQTT")
    else:
        print(f"Terhubung gagal. Kode return: {rc}")

# Callback ketika pesan berhasil dipublikasikan
def on_publish(client, userdata, mid):
    print(f"Pesan berhasil dipublish: mid={mid}")

# Inisialisasi klien MQTT tanpa `client_id` (akan dibuat otomatis)
client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish

# Hubungkan ke broker MQTT
print("Menghubungkan ke broker MQTT...")
client.connect(broker, port, keepalive=60)

# Loop untuk mempublikasikan data dummy secara berkala
try:
    while True:
        data = generate_dummy_data()  # Generate data dummy
        for key, topic in topics.items():
            payload = json.dumps(data[key])  # Konversi data ke JSON
            result = client.publish(topic, payload)  # Publish ke topik
            status = result[0]
            if status == 0:
                print(f"Pesan berhasil dipublish ke {topic}: {payload}")
            else:
                print(f"Gagal mempublish pesan ke {topic}")
        time.sleep(1)  # Tunggu 1 detik sebelum publish data berikutnya
except KeyboardInterrupt:
    print("\nProgram dihentikan.")
finally:
    client.disconnect()
