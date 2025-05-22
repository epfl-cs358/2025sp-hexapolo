from usb_4_mic_array.tuning import Tuning
import usb.core
import usb.util
from time import sleep
import pyaudio
import json
import pvporcupine
import pyaudio
import struct
import os

motor = Motor(forward=23, backward=24)
current_angle = 0  
SPR = 200  

def turn_motor(direction):
   
    if direction:
        motor.forward()
    else:
        motor.backward()
    sleep(0.1)
    motor.stop()
    sleep(0.05)




def turn_to_angle(target_angle):
  
    global current_angle
    delta = (target_angle - current_angle) % 360
    if delta > 180:
        delta -= 360  # Choose shortest path

    direction = delta > 0
    steps = int(abs(delta) / 360 * SPR)
    print(f"Turning {'CW' if direction else 'CCW'} by {abs(delta)}° ({steps} steps)")

    for _ in range(steps):
        turn_motor(direction)

    current_angle = target_angle



def get_doa_angle():
    dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
    if not dev:
        print("Mic Array not found.")
        return None

    Mic_tuning = Tuning(dev)
    print("Listening for voice direction...")

    while True:
        if Mic_tuning.is_voice():
            angle = Mic_tuning.direction
            print(f"Voice detected at {angle}°")
            return angle
        sleep(0.05)




def wait_for_wake_word():
    print("Initializing Porcupine on Raspberry Pi...")

    library_path = "libpv_porcupine.so"  # ARMv6 version
    keyword_path = "keyword.ppn"
    access_key = "+QaATGRUbeBmooQyrWr9tnsItC6JR6ZgCO3F+tmdkRV//dSWCZuK0A=="

    porcupine = pvporcupine.create(
        access_key=access_key,
        library_path=library_path,
        model_path=None,  # Use default unless custom needed
        keyword_paths=[keyword_path],
        sensitivities=[0.7]
    )

    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    print("Say 'polo' to activate...")

    try:
        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("Wake word detected!")
                break

    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()


def main():
    bz = Buzzer(25)
    bz.beep(on_time=0.2, off_time=0.1, n=2)

    try:
        while True:
            wait_for_wake_word()
            doa = get_doa_angle()
            if doa is not None:
                turn_to_angle(doa)
            sleep(0.5)
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")



if __name__ == "__main__":
    main()










# ## To test keyword detection on PC without motors
# from vosk import Model, KaldiRecognizer
# import pyaudio
# import json
# import time

# # Load Vosk model
# model = Model("model")  # path to unzipped Vosk model folder
# recognizer = KaldiRecognizer(model, 16000)

# # PyAudio settings
# p = pyaudio.PyAudio()
# stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
#                 input=True, frames_per_buffer=8000)
# stream.start_stream()

# print("Say 'marco' to activate...")

# try:
#     while True:
#         data = stream.read(4000, exception_on_overflow=False)
#         if recognizer.AcceptWaveform(data):
#             result = recognizer.Result()
#             text = json.loads(result).get("text", "")
#             print("Recognized:", text)

#             if "marco" in text.lower() or "michael" in text.lower():
#                 print("Wake word 'marco' detected!")
#                 # Add your DOA call here
#                 break
# except KeyboardInterrupt:
#     print("\nStopped by user.")
# finally:
#     stream.stop_stream()
#     stream.close()
#     p.terminate()





## Zak's old main


# if __name__ == "__main__":
#     bz = Buzzer(25)
#     bz.on()
#     bz.beep()
#     bz.off()

#     try:
#         while True:
#             doa = get_doa_angle()
#             if doa is not None:
#                 turn_to_angle(doa)
#             sleep(0.5)
#     except KeyboardInterrupt:
#         print("\nProgram terminated cleanly.")
