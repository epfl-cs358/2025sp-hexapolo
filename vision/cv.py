import cv2

# ESP32 URL
esp_ip = "172.21.78.5"
port = 81
URL = f"http://{esp_ip}:{port}/stream"

cap = cv2.VideoCapture(URL)

if __name__ == '__main__':
    while True:
        if cap.isOpened():
            ret, frame = cap.read()

            cv2.imshow("ESP32 stream", frame)

            key = cv2.waitKey(1)

            # Ends stream if escape is pressed
            if key == 27:
                break

    cap.release()
    cv2.destroyAllWindows()
