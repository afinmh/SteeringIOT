import random
import time
import json
import paho.mqtt.client as mqtt

# Konfigurasi MQTT
broker = "broker.hivemq.com"
port = 1883                  

topic = "motorffitenass/sensor"

# Fungsi untuk menghasilkan data dummy sesuai format baru
def generate_dummy_data():
    pompa = random.choice(["ON", "OFF"])  # Simulasi status pompa
    strobo = random.choice(["ON", "OFF"])  # Simulasi status strobo
    speaker = random.choice(["ON", "OFF"])  # Simulasi status speaker
    fire = random.choice(["Aman", "Bahaya"])  # Simulasi status speaker
    batre = random.randint(0, 100)  # Simulasi persentase baterai
    distance = round(random.uniform(0.0, 300.0), 2)  # Simulasi jarak ultrasonic (cm)
    return {
        "pompa": pompa,
        "strobo": strobo,
        "speaker": speaker,
        "fire": fire,
        "batre": batre,
        "distance": distance,
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
        payload = json.dumps(data)  # Konversi data ke JSON
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
