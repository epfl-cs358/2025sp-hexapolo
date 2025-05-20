from gpiozero import Motor
from time import sleep

turn_motor = Motor(forward=4, backward=22)
walk_motor = Motor(forward=23, backward=24)

def forward(duration=1, speed=1):
    """Move forward for specified duration in seconds"""
    print(f"Walking forward for {duration} second(s)")
    walk_motor.forward(speed)
    sleep(duration)
    walk_motor.stop()

def turn(angle, speed=1):
    """Turn by specified angle in degrees (positive=right, negative=left)"""
    # Convert angle to time-based turn (simplified approach)
    print(f"Turning CCW by {angle}°")
    
    if angle > 0:
        turn_time = angle / 30 * 0.5  # 0.5s per 90 degrees
        turn_motor.forward(speed)  # Right turn
    else:
        turn_time = (360 + angle) / 30 * 0.5  # 0.5s per 90 degrees
        turn_motor.forward(speed)  # Left turn
    
    sleep(turn_time)
    turn_motor.stop()
