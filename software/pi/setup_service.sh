#!/bin/bash

# Setup script for Robot Control Service with ESP32 Communication
# Run this script with sudo on your Raspberry Pi

set -e

echo "Setting up Robot Control Service..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script with sudo"
    exit 1
fi

# Define paths
SERVICE_FILE="serial_reader.service"
SYSTEMD_PATH="/etc/systemd/system/"
SCRIPT_PATH="/home/pi/software/pi/main.py"
LOG_FILE="/var/log/robot_control.log"

# Create log file and set permissions
touch $LOG_FILE
chown pi:pi $LOG_FILE
chmod 644 $LOG_FILE

# Copy service file to systemd directory
echo "Installing service file..."
cp $SERVICE_FILE $SYSTEMD_PATH
chmod 644 $SYSTEMD_PATH$SERVICE_FILE

# Make sure the Python script is executable
chmod +x $SCRIPT_PATH
chown pi:pi $SCRIPT_PATH

# Add pi user to dialout group for serial access
usermod -a -G dialout pi

# Check if the expected serial port exists
EXPECTED_PORT="/dev/ttyUSB0"
if [ ! -e "$EXPECTED_PORT" ]; then
    echo "Warning: Expected serial port $EXPECTED_PORT not found!"
    echo "Available serial ports:"
    ls -la /dev/tty[AU]* 2>/dev/null || echo "No USB/ACM serial ports found"
    echo "You may need to update the port in read_from_serial.py"
fi

# Disable getty on serial port if it exists
if systemctl is-enabled serial-getty@ttyUSB0.service 2>/dev/null; then
    echo "Disabling serial getty service to prevent conflicts..."
    systemctl disable serial-getty@ttyUSB0.service
fi

# Reload systemd and enable service
echo "Enabling service..."
systemctl daemon-reload
systemctl enable serial_reader.service

# Start the service
echo "Starting service..."
systemctl start serial_reader.service

# Show service status
echo "Service status:"
systemctl status serial_reader.service --no-pager

echo ""
echo "Setup complete!"
echo "The robot control service will now start automatically on boot (no login required)."
echo ""
echo "IMPORTANT: Do not use minicom on the ESP32 serial port while this service is running!"
echo "The service and minicom cannot share the same serial port."
echo ""
echo "The robot will:"
echo "  1. Listen for audio DOA (Direction of Arrival)"
echo "  2. Turn toward detected sounds"
echo "  3. Follow movement commands from ESP32/laptop vision system"
echo ""
echo "Useful commands:"
echo "  Check service status: sudo systemctl status serial_reader.service"
echo "  View live logs: sudo journalctl -u serial_reader.service -f"
echo "  Stop service: sudo systemctl stop serial_reader.service"
echo "  Start service: sudo systemctl start serial_reader.service"
echo "  Restart service: sudo systemctl restart serial_reader.service"
echo "  Test connection: python3 /home/pi/software/pi/test_serial.py"
echo ""
echo "The service will survive reboots and run without anyone logged in."
echo "Robot control logs: tail -f /var/log/robot_control.log"