from usb_4_mic_array.tuning import Tuning
import usb.core
import usb.util
import time

def get_doa_angle():
  
    dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
    if not dev:
        print("Mic Array not found.")
        return None

    Mic_tuning = Tuning(dev)
    print("Waiting for voice...")

    try:
        while True:
            if Mic_tuning.is_voice():
                angle = Mic_tuning.direction
                print(f"Voice detected at {angle}°")
                return angle 
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\n Stopped by user.")
        return None

# Example usage
if __name__ == "__main__":
    doa = get_doa_angle()
    if doa is not None:
        print(f"Returned angle: {doa}°")
