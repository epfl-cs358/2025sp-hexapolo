from gpiozero import Motor
from time import sleep

walk_motor = Motor(forward=25, backward=4)
turn_motor = Motor(forward=23, backward=24)
SPR = 200  # Steps per full rotation
STEP_DELAY = 0.2  # Increased delay for better movement

def forward(duration=1, speed=1):
    """Move forward for specified duration in seconds"""
    walk_motor.forward(speed)
    sleep(duration)
    walk_motor.stop()

def backward(duration=1, speed=1):
    """Move backward for specified duration in seconds"""
    walk_motor.backward(speed)
    sleep(duration)
    walk_motor.stop()

def turn(angle, speed=1):
    """Turn by specified angle in degrees (positive=right, negative=left)"""
    # Convert angle to time-based turn (simplified approach)
    turn_time = abs(angle) / 30 * 0.5  # 0.5s per 90 degrees
    
    if angle > 0:
        turn_motor.forward(speed)  # Right turn
    else:
        turn_motor.backward(speed)  # Left turn
    
    sleep(turn_time)
    turn_motor.stop()

def main():
    print("Moving forward for 5 seconds")
    forward(5)
    
    print("Turning 90 degrees right")
    turn(90)  # Right turn
    
    print("Moving forward for 5 seconds")
    forward(5)
    
    print("Turning 180 degrees left")
    turn(-180)  # Left turn
    
    print("Moving forward for 5 seconds")
    forward(5)

if __name__ == "__main__":
    main()
