from basic_movement import turn
from usb_4_mic_array.tuning import Tuning
import usb.core
import usb.util
from time import sleep
from vosk import Model, KaldiRecognizer
import pyaudio
import json

# Load Vosk model
model = Model("model")  # path to unzipped Vosk model folder
recognizer = KaldiRecognizer(model, 16000)

# PyAudio settings
p = pyaudio.PyAudio()

def get_doa_angle():
    dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
    if not dev:
        print("Mic Array not found.")
        return None

    Mic_tuning = Tuning(dev)
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                    input=True, frames_per_buffer=8000)
    stream.start_stream()

    print("Say 'marco' to activate...")

    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                text = json.loads(result).get("text", "")
                print("Recognized:", text)

                if "marco" in text.lower() or "michael" in text.lower():
                    print("Wake word 'marco' detected!")
                    if Mic_tuning.is_voice():
                        angle = Mic_tuning.direction
                        angle = (angle + 90) % 360
                        print(f"Voice detected at {angle}°")
                        return angle 
                    sleep(0.05)
    except KeyboardInterrupt:
        print("\nStopped by user.")
        return -1
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()




