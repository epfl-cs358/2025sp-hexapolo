#!/bin/bash

# Robot Control Service Management Script
# Helps manage the robot control service and minicom usage

set -e

SERVICE_NAME="serial_reader.service"
SERIAL_PORT="/dev/ttyUSB0"
BAUDRATE="115200"

show_usage() {
    echo "Robot Control Service Manager"
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  status      - Show service status"
    echo "  start       - Start the robot control service"
    echo "  stop        - Stop the robot control service"
    echo "  restart     - Restart the robot control service"
    echo "  logs        - Show live service logs"
    echo "  minicom     - Stop service and start minicom (manual control)"
    echo "  test        - Test serial connection"
    echo "  ports       - List available serial ports"
    echo "  help        - Show this help message"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo "This command requires sudo privileges"
        exit 1
    fi
}

service_status() {
    echo "=== Robot Control Service Status ==="
    systemctl status $SERVICE_NAME --no-pager || true
    echo ""
    echo "=== Last 10 Log Lines ==="
    journalctl -u $SERVICE_NAME -n 10 --no-pager || true
}

start_service() {
    check_root
    echo "Starting robot control service..."
    
    # Kill any running minicom first
    if pgrep minicom > /dev/null; then
        echo "Stopping minicom first..."
        pkill minicom
        sleep 2
    fi
    
    systemctl start $SERVICE_NAME
    echo "Service started!"
    service_status
}

stop_service() {
    check_root
    echo "Stopping robot control service..."
    systemctl stop $SERVICE_NAME
    echo "Service stopped!"
}

restart_service() {
    check_root
    echo "Restarting robot control service..."
    systemctl restart $SERVICE_NAME
    echo "Service restarted!"
    service_status
}

show_logs() {
    echo "Showing live logs (Ctrl+C to exit)..."
    journalctl -u $SERVICE_NAME -f
}

start_minicom() {
    # Check if service is running
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo "Robot control service is currently running."
        echo "Minicom cannot access the serial port while the service is active."
        read -p "Stop the service and start minicom? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo systemctl stop $SERVICE_NAME
            echo "Service stopped."
        else
            echo "Cancelled."
            exit 0
        fi
    fi
    
    echo "Starting minicom on $SERIAL_PORT at $BAUDRATE baud..."
    echo "Press Ctrl+A X to exit minicom"
    echo "After exiting, you can restart the service with: sudo $0 start"
    echo ""
    
    if [ ! -c "$SERIAL_PORT" ]; then
        echo "Warning: Serial port $SERIAL_PORT not found!"
        list_ports
        exit 1
    fi
    
    minicom -b $BAUDRATE -D $SERIAL_PORT
}

test_connection() {
    python3 /home/pi/software/pi/test_serial.py $SERIAL_PORT
}

list_ports() {
    echo "Available serial ports:"
    ls -la /dev/tty[AU]* 2>/dev/null | while read line; do
        echo "  $line"
    done
    echo ""
    echo "Current configured port: $SERIAL_PORT"
}

case "${1:-help}" in
    status)
        service_status
        ;;
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    logs)
        show_logs
        ;;
    minicom)
        start_minicom
        ;;
    test)
        test_connection
        ;;
    ports)
        list_ports
        ;;
    help|*)
        show_usage
        ;;
esac