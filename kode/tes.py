import asyncio
import websockets
import json

async def connect_to_ws():
    # Ganti dengan URL server WebSocket kamu di Glitch
    uri = "wss://dusty-steel-atlasaurus.glitch.me"

    async with websockets.connect(uri) as websocket:
        # Mengirim pesan untuk mendaftar sebagai sender
        sender_message = {
            "type": "receiver",
        }
        await websocket.send(json.dumps(sender_message))
        print("Sent: Sender registered")

        # Menunggu dan menerima pesan dari server
        while True:
            message = await websocket.recv()
            print(f"Received: {message}")

# Jalankan program
asyncio.get_event_loop().run_until_complete(connect_to_ws())
