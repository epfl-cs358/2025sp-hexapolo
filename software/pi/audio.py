from usb_4_mic_array.tuning import Tuning
import usb.core
import subprocess
import time
import numpy as np
import tflite_runtime.interpreter as tflite
from pathlib import Path

# Config
MODEL_PATH = Path("keyword_polo.tflite")
DETECTION_THRESHOLD = 0.5
AUDIO_DEVICE = "plughw:CARD=ArrayUAC10,DEV=0"  # Find with: arecord -L
SAMPLE_RATE = 16000
FRAME_MS = 30
CHUNK_SIZE = int(SAMPLE_RATE * FRAME_MS / 1000)  # 480 samples for 30ms

class WakeWordDetector:
    def __init__(self, model_path):
        self.interpreter = tflite.Interpreter(model_path=str(model_path))
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()[0]
        self.output_details = self.interpreter.get_output_details()[0]
        
        self.ring_buffer = np.zeros(4, dtype=np.float32)
        self.buffer_ptr = 0

    def process(self, pcm_data):
        audio = np.frombuffer(pcm_data, dtype=np.int16).astype(np.float32) / 32768.0
        self.interpreter.set_tensor(self.input_details['index'], audio.reshape(1, -1))
        self.interpreter.invoke()
        score = self.interpreter.get_tensor(self.output_details['index'])[0]
        
        # Smoothing
        self.ring_buffer[self.buffer_ptr] = score
        self.buffer_ptr = (self.buffer_ptr + 1) % 4
        return np.mean(self.ring_buffer) >= DETECTION_THRESHOLD

class AudioIn:
    def __init__(self):
        self.process = subprocess.Popen(
            ["arecord", "-t", "raw", "-D", AUDIO_DEVICE,
             "-c", "1", "-f", "S16_LE", "-r", str(SAMPLE_RATE)],
            stdout=subprocess.PIPE,
            bufsize=CHUNK_SIZE*2
        )

    def read_frame(self):
        return self.process.stdout.read(CHUNK_SIZE * 2)  # 16-bit samples

def play_wav(path):
    subprocess.run(["aplay", "-q", "-D", AUDIO_DEVICE, path])

def get_doa_angle():
    # Initialize hardware
    dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
    if not dev:
        print("Mic array not found")
        return None

    tuning = Tuning(dev)
    audio_in = AudioIn()
    detector = WakeWordDetector(MODEL_PATH)

    print("Listening for wake word...")
    try:
        while True:
            pcm = audio_in.read_frame()
            if detector.process(pcm):
                time.sleep(0.05)  # Let DOA settle
                angle = (tuning.direction + 90) % 360
                print(f"Wake word detected! Angle: {angle}°")
                play_wav("Marco.wav")
                return angle
    except KeyboardInterrupt:
        print("\nStopped by user")
        return None
    finally:
        audio_in.process.terminate()

if __name__ == "__main__":
    get_doa_angle()