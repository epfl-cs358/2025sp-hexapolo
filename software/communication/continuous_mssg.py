import requests

# Replace with your ESP32-CAM IP
esp32_ip = "http://172.20.10.4"

print("Type your message to send to ESP32-CAM.")
print("Type 'exit' to quit.\n")

while True:
    message = input("Your message: ")

    if message.lower() == "exit":
        print("Exiting...")
        break

    try:
        response = requests.get(f"{esp32_ip}/message", params={"text": message})
        print("Response from ESP32-CAM:")
        print(response.text)
    except Exception as e:
        print("Error communicating with ESP32-CAM:", e)
