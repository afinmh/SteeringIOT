import requests
import json

# URL endpoint API Django Anda yang ada di ngrok
url = "localhost:8000/update_status/"

# Data yang ingin Anda kirimkan ke API
status_data = {
    "pompa": "ON",
    "strobo": "OFF",
    "speaker": "ON",
    "fire": "Aman",
    "batre": 85,
    "distance": 120.5
}

# Mengirimkan data menggunakan POST request
response = requests.post(url, json=status_data)

# Mengecek respons dari server
if response.status_code == 201:  # Memperbaiki pengecekan untuk kode 201
    print("Status berhasil diupdate!")
    print("Response:", response.json())  # Menampilkan respons JSON dari server
else:
    print("Gagal mengupdate status!")
    print("Error:", response.status_code, response.text)
