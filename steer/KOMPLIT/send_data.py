import asyncio
import websockets
import json
import random
import time

# Fungsi untuk menghasilkan data acak
def generate_random_data():
    topics = ['temperature', 'humidity', 'pressure']
    topic = random.choice(topics)
    value = random.uniform(20.0, 30.0) if topic == 'temperature' else random.uniform(40.0, 60.0)
    return { 'topic': topic, 'value': value }

async def send_random_data():
    uri = "ws://localhost:8765"  # WebSocket server yang kita buat
    async with websockets.connect(uri) as websocket:
        while True:
            random_data = generate_random_data()
            await websocket.send(json.dumps(random_data))  # Mengirim data acak
            print(f"Sent data: {random_data}")
            await asyncio.sleep(5)  # Tunggu 5 detik sebelum mengirim data lagi

# Jalankan pengiriman data
asyncio.run(send_random_data())
