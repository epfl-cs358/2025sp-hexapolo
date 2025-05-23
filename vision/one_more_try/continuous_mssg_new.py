import requests
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuration
ESP32_IP = "172.21.78.5"  # Replace with your ESP32-CAM IP
LAPTOP_IP = "0.0.0.0"     # Will listen on all available network interfaces
LAPTOP_PORT = 5000        # Port for the laptop server

MESSAGE_ENDPOINT = f"http://{ESP32_IP}:8080/message"
TIMEOUT_SECONDS = 3

# Store the last received message from ESP32
last_received_message = ""

@app.route('/esp32_message', methods=['GET', 'POST'])
def handle_esp32_message():
    global last_received_message
    if request.method == 'GET':
        return jsonify({"message": last_received_message})
    elif request.method == 'POST':
        last_received_message = request.json.get('text', '')
        print(f"\nReceived from ESP32: {last_received_message}")
        return jsonify({"status": "success"})

def send_message(text):
    """Send a message to ESP32-CAM and return the response."""
    try:
        response = requests.get(
            MESSAGE_ENDPOINT,
            params={"text": text},
            timeout=TIMEOUT_SECONDS
        )
        if response.status_code == 200:
            return response.text.strip()
        else:
            return f"Error: HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Failed to communicate with ESP32-CAM: {str(e)}"

def main():
    # Run Flask server in a separate thread
    from threading import Thread
    server_thread = Thread(target=lambda: app.run(host=LAPTOP_IP, port=LAPTOP_PORT))
    server_thread.daemon = True
    server_thread.start()

    print("\n=== ESP32-CAM Message Client & Server ===")
    print(f"ESP32 Target: {MESSAGE_ENDPOINT}")
    print(f"Laptop Server: http://{LAPTOP_IP}:{LAPTOP_PORT}/esp32_message")
    print("Type 'exit' to quit.\n")

    while True:
        message = input("").strip()
        
        if not message:
            continue
        
        if message.lower() == "exit":
            print("Exiting...")
            break

        # Send message to ESP32
        send_message(message)
        print(f"[Laptop]: {message}")

if __name__ == "__main__":
    main()