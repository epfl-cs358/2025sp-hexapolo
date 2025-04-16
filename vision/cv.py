import cv2
import time
import torch
from ultralytics import YOLO

# ESP32 URL
esp_ip = "172.21.78.5"
port = 81
URL = f"http://{esp_ip}:{port}/stream"

# Check for GPU availability
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")

model = YOLO("yolo11n.pt").to(device)

# Model Configuration
conf_threshold = 0.5  # Confidence threshold for detections
class_names = model.names

cap = cv2.VideoCapture(URL)

def process_frame(frame):
    """Process frame with YOLO model and draw bounding boxes"""
    # Perform prediction
    results = model(frame)
    
    # Get the first result
    result = results[0]
    
    # Process detection results
    for box in result.boxes:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

        confidence = float(box.conf[0])
        class_id = int(box.cls[0])
        
        if confidence < conf_threshold:
            continue

        class_name = class_names[class_id]
        
        # Only detect people
        if class_id ==0:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{class_name}: {confidence:.2f}"
            
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(frame, (x1, y1 - text_size[1] - 5), (x1 + text_size[0], y1), (0, 255, 0), -1)
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    
    return frame

if __name__ == '__main__':
    prev_time = time.time()

    while True:
        if cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                print("Failed to get frame")
                # If connection is lost, try to reconnect
                time.sleep(1)
                cap = cv2.VideoCapture(URL)
                continue
            
            # Process frame with YOLO
            processed_frame = process_frame(frame)
            
            # Calculate and display FPS
            current_time = time.time()
            fps = 1 / (current_time - prev_time)
            prev_time = current_time
            cv2.putText(processed_frame, f"FPS: {fps:.2f}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            cv2.imshow("ESP32 YOLO Detection", processed_frame)
            
            key = cv2.waitKey(1)

            # Ends stream if escape is pressed
            if key == 27:
                break

    cap.release()
    cv2.destroyAllWindows()
