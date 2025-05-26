from basic_movement import turn
from usb_4_mic_array.tuning import Tuning
import usb.core
import usb.util
from time import sleep
import wave
import pyaudio
import porcupine
import struct

path = 'Marco.wav'

def init_audio(path=path):
    wf = wave.open(path, 'rb')
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pa.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
        output=True
    )
    return wf, stream, pa

def play_one_chunk(wf, stream, chunk_size=1024):
    data = wf.readframes(chunk_size)
    if data:
        stream.write(data)
        return True  
    else:
        wf.rewind()
        return False 


def play_wav(path=path):
    wf = wave.open(path, 'rb')
    pa = pyaudio.PyAudio()

    stream = pa.open(
        format=pa.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
        output=True
    )

    data = wf.readframes(1024)
    while data:
        stream.write(data)
        data = wf.readframes(1024)

    stream.stop_stream()
    stream.close()
    pa.terminate()

def get_doa_angle():
    dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
    if not dev:
        print("Mic Array not found.")
        return None

    Mic_tuning = Tuning(dev)
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

    print("Say 'polo polo' to activate...")

    try:
        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("Wake word detected!")
                if Mic_tuning.is_voice():
                    angle = Mic_tuning.direction
                    angle = (angle + 90) % 360
                    print(f"Voice detected at {angle}°")
                    return angle 
                sleep(0.05)
    except KeyboardInterrupt:
        print("\nStopped by user.")
        return None
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()




