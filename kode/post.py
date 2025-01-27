import requests
import json
import time
import random

# URL API
api_url = "http://ifrit.great-site.net/apisensor.php/"

def generate_random_data():
    """Generate random data to simulate sensor readings."""
    pompa = "ON" if random.randint(0, 1) else "OFF"
    strobo = "ON" if random.randint(0, 1) else "OFF"
    speaker = "ON" if random.randint(0, 1) else "OFF"
    fire = "Bahaya" if random.randint(0, 1) else "Aman"
    batre = random.randint(10, 100)
    distance = round(random.uniform(1, 10), 1)

    return {
        "pompa": pompa,
        "strobo": strobo,
        "speaker": speaker,
        "fire": fire,
        "batre": str(batre),
        "distance": distance
    }

def post_data_to_api(data):
    """POST the sensor data to the API."""
    try:
        response = requests.post(api_url, json=data)
        if response.status_code == 200:
            print(f"POST successful: {response.text}")
        else:
            print(f"Failed to POST data: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error during POST request: {e}")

def main():
    """Main loop to send data every 10 minutes."""
    while True:
        # Generate random data
        sensor_data = generate_random_data()
        print(f"Generated data: {sensor_data}")

        # POST data to API
        post_data_to_api(sensor_data)

        # Wait for 10 minutes (600 seconds)
        time.sleep(5)

if __name__ == "__main__":
    main()
