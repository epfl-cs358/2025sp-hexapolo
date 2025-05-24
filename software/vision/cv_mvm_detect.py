import cv2
import time
import torch
import logging
import requests
from flask import Flask, request, jsonify
from ultralytics import YOLO

# Suppress ultralytics logging
logging.getLogger("ultralytics").setLevel(logging.WARNING)

app = Flask(__name__)

# ESP32-CAM stream URL
esp_ip = "172.21.78.5" # Replace with your ESP32-CAM IP address since it may change based on the network
port = 81
LAPTOP_IP = "0.0.0.0"     # Will listen on all available network interfaces
LAPTOP_PORT = 5000        # Port for the laptop server

URL = f"http://{esp_ip}:{port}/stream"
MESSAGE_ENDPOINT = f"http://{esp_ip}:8080/message"
TIMEOUT_SECONDS = 3  # Fail fast if ESP32 isn't responding

# Store the last received message from ESP32/Raspberry Pi
last_received_message = ""

@app.route('/esp32_message', methods=['GET', 'POST'])
def handle_esp32_message():
    global last_received_message
    if request.method == 'GET':
        return jsonify({"message": last_received_message})
    elif request.method == 'POST':
        last_received_message = request.json.get('text', '')
        print(f"\n[Pi]: {last_received_message}")
        return jsonify({"status": "success"})

# Check for GPU
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")

# Load YOLO model
model = YOLO("yolo11n.pt").to(device)
conf_threshold = 0.5  # Minimum confidence to consider detection

# Initialize video capture
cap = cv2.VideoCapture(URL)
prev_center = None
movement_threshold = 20  # Pixels for movement detection

def process_frame(frame):
    """Run YOLO on frame and focus on closest valid person"""
    global prev_center

    results = model(frame, verbose=False)
    result = results[0]

    best_box = None
    best_center = None
    largest_area = 0
    proximity_level = "Far"
    color = (0, 255, 0)

    for box in result.boxes:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
        confidence = float(box.conf[0])
        class_id = int(box.cls[0])

        if confidence < conf_threshold or class_id != 0:
            continue

        width = x2 - x1
        height = y2 - y1
        area = width * height

        # Filter out small or partial detections
        if height < 100 or area < 15000:
            continue

        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if area > largest_area:
            largest_area = area
            best_box = (x1, y1, x2, y2)
            best_center = (cx, cy)

            # Assign proximity color/label
            if area > 60000:
                proximity_level = "Close"
                color = (0, 0, 255)  # Red
            elif area > 30000:
                proximity_level = "Medium"
                color = (0, 255, 255)  # Yellow
            else:
                proximity_level = "Far"
                color = (0, 255, 0)  # Green

    if best_center:
        x1, y1, x2, y2 = best_box
        cx, cy = best_center

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        label = proximity_level
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
        cv2.rectangle(frame, (x1, y1 - text_size[1] - 5), (x1 + text_size[0], y1), color, -1)
        cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

        # Movement direction
        if prev_center:
            dx = cx - prev_center[0]
            dy = cy - prev_center[1]
            if abs(dx) > abs(dy):
                if dx > movement_threshold:
                    response = send_message("right")
                    print(f"[Laptop]: right, ACK: {response}")
                elif dx < -movement_threshold:
                    response = send_message("left")
                    print(f"[Laptop]: left, ACK: {response}")

        prev_center = (cx, cy)

    return frame

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

if __name__ == '__main__':
    prev_time = time.time()

    # Run Flask server in a separate thread
    from threading import Thread
    server_thread = Thread(target=lambda: app.run(host=LAPTOP_IP, port=LAPTOP_PORT))
    server_thread.daemon = True
    server_thread.start()

    while True:
        if cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Failed to get frame")
                time.sleep(1)
                cap = cv2.VideoCapture(URL)
                continue

            processed_frame = process_frame(frame)
            fps = 1 / (time.time() - prev_time)
            prev_time = time.time()
            cv2.putText(processed_frame, f"FPS: {fps:.2f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            cv2.imshow("ESP32 YOLO Detection", processed_frame)

            if cv2.waitKey(1) == 27:  # ESC to exit
                break

    cap.release()
    cv2.destroyAllWindows()
