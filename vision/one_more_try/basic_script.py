import requests

# Replace with the IP address printed by the ESP32-CAM
esp32_ip = "http://172.20.10.4" 
message = "Hello from laptop!"

response = requests.get(f"{esp32_ip}/message", params={"text": message})

print("Response from ESP32-CAM:")
print(response.text)
# Note: Make sure to replace the IP address with the one printed by the ESP32-CAM.
# This code sends a message to the ESP32-CAM using HTTP GET request.