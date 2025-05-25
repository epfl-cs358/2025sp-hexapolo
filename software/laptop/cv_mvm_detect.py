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
 
# Camera settings
CAMERA_HFOV = 40  # Horizontal field of view in degrees
TURN_THRESHOLD = 5 # Minimum angle difference to trigger a turn command
MAX_TURN_ANGLE = 60 # Maximum turn angle to send

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
conf_threshold = 0.2  # Minimum confidence to consider detection

# Initialize video capture
cap = cv2.VideoCapture(URL)
prev_center = None
movement_threshold = 50  # Pixels for movement detection

def process_frame(frame):
    global prev_center

    frame_height, frame_width, _ = frame.shape    
    frame_area = frame_width * frame_height
    
    """Run YOLO on frame and focus on closest valid person"""
    results = model(frame, verbose=False)
    result = results[0]

    best_box = None
    best_center = None
    largest_area = 0
    color = (0, 255, 0)  # Default color (green)

    frame_width = frame.shape[1]
    frame_center = frame_width / 2

    for box in result.boxes:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
        confidence = float(box.conf[0])
        class_id = int(box.cls[0])

        if confidence < conf_threshold or class_id != 0:  # Only look for people
            continue

        width = x2 - x1
        height = y2 - y1
        area = width * height

        if height < 100 or area < 15000:  # Filter small detections
            continue

        cx = (x1 + x2) // 2  # Center x-coordinate of detection
        
        if area > largest_area:
            largest_area = area
            best_box = (x1, y1, x2, y2)
            best_center = cx
            
            # Update color based on area (proximity)
            if area > 60000:
                color = (0, 0, 255)  # Red for close
            elif area > 30000:
                color = (0, 255, 255)  # Yellow for medium
            else:
                color = (0, 255, 0)  # Green for far

    if best_center and best_box:
        # Draw bounding box
        x1, y1, x2, y2 = best_box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Draw center dot
        cv2.circle(frame, (best_center, (y1 + y2) // 2), 5, (255, 0, 0), -1)

        # Calculate how far off center the person is
        pixels_from_center = best_center - frame_center
        
        # Convert to angle based on camera's FOV
        relative_pos = pixels_from_center / (frame_width / 2)
        turn_angle = relative_pos * (CAMERA_HFOV / 2)

        # Only send command if the offset is significant
        if abs(turn_angle) > TURN_THRESHOLD and (prev_center is None or abs(best_center - prev_center) > 10):
            # Limit maximum turn angle
            turn_angle = max(min(turn_angle, MAX_TURN_ANGLE), -MAX_TURN_ANGLE)
            
            direction = 'right' if turn_angle > 0 else 'left'
            command = f"{direction} {abs(turn_angle):.1f}"
            
            # Send the command
            response = send_message(command)
            print(f"[Laptop]: {command} (offset: {pixels_from_center:.1f}px, {turn_angle:.1f}°)")
         
        # Update previous center position
        prev_center = best_center
        
        # Draw visualization elements
        cv2.line(frame, (int(frame_center), 0), (int(frame_center), frame.shape[0]), (0, 255, 0), 1)  # Center line
        cv2.line(frame, (best_center, 0), (best_center, frame.shape[0]), (0, 0, 255), 1)  # Person center line
        cv2.putText(frame, f"Angle: {turn_angle:.1f}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

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
