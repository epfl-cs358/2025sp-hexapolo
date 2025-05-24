import struct
import sys
import usb.core
from time import sleep

import pvporcupine
import pyaudio
from usb_4_mic_array.tuning import Tuning

import wave

def play_wav(path, speed=1.0):
    import wave
    import pyaudio

    wf = wave.open(path, 'rb')
    pa = pyaudio.PyAudio()

    # Slow down = lower playback rate
    playback_rate = int(wf.getframerate() / speed)

    stream = pa.open(
        format=pa.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=playback_rate,
        output=True
    )

    data = wf.readframes(1024)
    while data:
        stream.write(data)
        data = wf.readframes(1024)

    stream.stop_stream()
    stream.close()
    pa.terminate()

# Configuration
KEYWORD_PATH = "polo.ppn" #Change it to polo_window.ppn if testing on PC
SENSITIVITY = 0.6
PA_DEVICE_NAME = "ReSpeaker"
ACCESS_KEY = "VwKDB5AYHN1P7Z9SVMbRKqVotPpxod+ohhlNtwiWWzkGPGMIyngzrQ=="  # Replace with your actual key


def find_respeaker_index(pa, name_substr="ReSpeaker"):
    for idx in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(idx)
        if name_substr.lower() in info["name"].lower() and info["maxInputChannels"] > 0:
            return idx
    return None


def get_doa_angle():
    porcupine = pvporcupine.create(
        access_key=ACCESS_KEY,
        keyword_paths=[KEYWORD_PATH],
        sensitivities=[SENSITIVITY],
    )

    pa = pyaudio.PyAudio()
    dev_index = find_respeaker_index(pa, PA_DEVICE_NAME)
    if dev_index is None:
        print("ReSpeaker device not found.")
        return -1

    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        input_device_index=dev_index,
        frames_per_buffer=porcupine.frame_length,
    )

    dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
    if not dev:
        print("Mic Array USB device not found.")
        return -1
    tuning = Tuning(dev)

    
    play_wav("Marco.wav", speed=1.2)
  

    print("Listening for polo wake word...")

    try:
        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            if porcupine.process(pcm) >= 0:
                print("Keyword 'polo polo' detected!")

                # Wait briefly to let sound settle
                sleep(0.05)

                try:
                    angle = (tuning.direction + 90) % 360
                    print(f"DOA angle at wake word: {angle} degrees")
                    return angle
                except Exception as e:
                    print("Error reading DOA:", e)
                    return -1
    except KeyboardInterrupt:
        print("Stopped by user.")
        return -1
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()


if __name__ == "__main__":
    sys.exit(get_doa_angle())
