import requests
import time
# Try Flask to receive messages via Wifi (similar to WebServer.h in ESP32, it can be used to create a web server so that the ESP32 can receive messages via Wifi)

# Configuration
ESP32_IP = "172.21.78.5"  # Replace with your ESP32-CAM IP
MESSAGE_ENDPOINT = f"http://{ESP32_IP}:8080/message"
TIMEOUT_SECONDS = 3  # Fail fast if ESP32 isn't responding

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
    print("\n=== ESP32-CAM Message Client ===")
    print(f"Target: {MESSAGE_ENDPOINT}")
    print("Type 'exit' to quit.\n")

    while True:
        message = input("Your message: ").strip()
        
        if not message:
            continue  # Skip empty messages
        
        if message.lower() == "exit":
            print("Exiting...")
            break

        # Send message and measure response time
        start_time = time.time()
        response = send_message(message)
        elapsed_ms = (time.time() - start_time) * 1000

        # Print results
        print("\n--- Response ---")
        print(f"ESP32-CAM replied: {response}")
        print(f"Response time: {elapsed_ms:.0f} ms\n")

if __name__ == "__main__":
    main()