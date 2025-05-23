#include <WiFi.h>
#include <WebServer.h>

// Replace these with your WiFi credentials
const char* ssid = "iPhone";
const char* password = "12345678";

// Create a web server on port 80
WebServer server(80);

// This function runs when we access /message?text=Hello
void handleMessage() {
  if (server.hasArg("text")) {
    String message = server.arg("text");
    Serial.println("Received message: " + message);
    server.send(200, "text/plain", "Message received: " + message);
  } else {
    server.send(400, "text/plain", "Missing 'text' parameter");
  }
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("Connected to WiFi!");
  Serial.print("ESP32-CAM IP Address: ");
  Serial.println(WiFi.localIP());

  // Define route
  server.on("/message", handleMessage);

  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();
}
