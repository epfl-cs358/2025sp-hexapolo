#!/usr/bin/env python3
"""
Wake-word + direction-of-arrival detector for ReSpeaker 4-mic array
using a custom TensorFlow-Lite model (keyword_polo.tflite).

Author: 2025-05-26
"""

import struct
import sys
import time
import usb.core
from pathlib import Path

import numpy as np
import pyaudio
import tflite_runtime.interpreter as tflite


from usb_4_mic_array.tuning import Tuning


MODEL_PATH          = Path("keyword_polo.tflite")
PA_DEVICE_NAME      = "ReSpeaker"
DETECTION_THRESHOLD = 0.5          # tune for your model
FRAME_MS            = 30           # model expects ~30 ms windows
SCORE_SMOOTHING     = 4            # moving-average over N frames
# ────────────────────────────────────────────────────────────────────


def find_respeaker_index(pa, name_substr="ReSpeaker"):
    """Return index of the first input device whose name contains *name_substr*."""
    for idx in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(idx)
        if name_substr.lower() in info["name"].lower() and info["maxInputChannels"] > 0:
            return idx
    return None


class WakeWordDetector:
    """Thin wrapper around a TFLite wake-word model."""
    def __init__(self, model_path: Path):
        self.interpreter = tflite.Interpreter(model_path=str(model_path))


        self.interpreter.allocate_tensors()
        self.in_details  = self.interpreter.get_input_details()[0]
        self.out_details = self.interpreter.get_output_details()[0]

        # Model IO assumptions ─────────
        self.sample_rate = 16000                     # Hz
        self.frame_len   = int(self.sample_rate * FRAME_MS / 1000)
        assert self.in_details["shape"][1] == self.frame_len, \
            "Model input length doesn’t match FRAME_MS"

        # Internal state
        self._ring = np.zeros(SCORE_SMOOTHING, dtype=np.float32)
        self._ring_ptr = 0

    def process(self, pcm16: bytes) -> bool:
        """Feed one frame (raw int16) into the model, return True if keyword detected."""
        # Convert to float32 ∈ [-1,1]
        samples = np.frombuffer(pcm16, dtype=np.int16).astype(np.float32) / 32768.0
        self.interpreter.set_tensor(self.in_details["index"], samples.reshape(self.in_details["shape"]))
        self.interpreter.invoke()
        score = float(self.interpreter.get_tensor(self.out_details["index"])[0])

        # Ring-buffer smoothing
        self._ring[self._ring_ptr] = score
        self._ring_ptr = (self._ring_ptr + 1) % SCORE_SMOOTHING
        mean_score = self._ring.mean()

        return mean_score >= DETECTION_THRESHOLD


def get_doa_angle() -> int:
    """Blocks until the wake-word is heard, returns DoA angle in degrees."""
    detector = WakeWordDetector(MODEL_PATH)

    pa = pyaudio.PyAudio()
    dev_index = find_respeaker_index(pa, PA_DEVICE_NAME)
    if dev_index is None:
        print("ReSpeaker device not found.")
        return -1

    stream = pa.open(rate=detector.sample_rate,
                     channels=1,
                     format=pyaudio.paInt16,
                     input=True,
                     input_device_index=dev_index,
                     frames_per_buffer=detector.frame_len)

    dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
    if not dev:
        print("Mic Array USB device not found.")
        return -1
    tuning = Tuning(dev)

    print("Listening for wake word …")

    try:
        while True:
            pcm = stream.read(detector.frame_len, exception_on_overflow=False)
            if detector.process(pcm):
                print("Keyword detected!")
                time.sleep(0.05)                               # allow DoA to settle
                try:
                    angle = (tuning.direction + 90) % 360
                    print(f"DOA angle at wake word: {angle}°")
                    return angle
                except Exception as e:
                    print("Error reading DoA:", e)
                    return -1
    except KeyboardInterrupt:
        print("Stopped by user.")
        return -1
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()


if __name__ == "__main__":
    sys.exit(get_doa_angle())



# 
#  #!/usr/bin/env python3

# import struct
# import sys
# import usb.core
# from time import sleep

# import pvporcupine
# import pyaudio
# from usb_4_mic_array.tuning import Tuning


# # Configuration
# KEYWORD_PATH = "polo.ppn" #change it to polo_window.ppn to test it on window
# SENSITIVITY = 0.6
# PA_DEVICE_NAME = "ReSpeaker"
# ACCESS_KEY = "VwKDB5AYHN1P7Z9SVMbRKqVotPpxod+ohhlNtwiWWzkGPGMIyngzrQ=="  

# def find_respeaker_index(pa, name_substr="ReSpeaker"):
#     for idx in range(pa.get_device_count()):
#         info = pa.get_device_info_by_index(idx)
#         if name_substr.lower() in info["name"].lower() and info["maxInputChannels"] > 0:
#             return idx
#     return None


# def get_doa_angle():
#     porcupine = pvporcupine.create(
#         access_key=ACCESS_KEY,
#         keyword_paths=[KEYWORD_PATH],
#         sensitivities=[SENSITIVITY],
#     )

#     pa = pyaudio.PyAudio()
#     dev_index = find_respeaker_index(pa, PA_DEVICE_NAME)
#     if dev_index is None:
#         print("ReSpeaker device not found.")
#         return -1

#     stream = pa.open(
#         rate=porcupine.sample_rate,
#         channels=1,
#         format=pyaudio.paInt16,
#         input=True,
#         input_device_index=dev_index,
#         frames_per_buffer=porcupine.frame_length,
#     )

#     dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
#     if not dev:
#         print("Mic Array USB device not found.")
#         return -1
#     tuning = Tuning(dev)

#     print("Listening for polo wake word...")

#     try:
#         while True:
#             pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
#             pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

#             if porcupine.process(pcm) >= 0:
#                 print("Keyword 'polo polo' detected!")

            
#                 sleep(0.05)

#                 try:
#                     angle = (tuning.direction + 90) % 360
#                     print(f"DOA angle at wake word: {angle} degrees")
#                     return angle
#                 except Exception as e:
#                     print("Error reading DOA:", e)
#                     return -1
#     except KeyboardInterrupt:
#         print("Stopped by user.")
#         return -1
#     finally:
#         stream.stop_stream()
#         stream.close()
#         pa.terminate()
#         porcupine.delete()


# if __name__ == "__main__":
#     sys.exit(get_doa_angle())
