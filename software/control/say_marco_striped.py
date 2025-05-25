import sounddevice as sd
import soundfile as sf

filename = "ready_to_play.wav"
device_index = 7  # ReSpeaker
volume = 0.1 # 30% volume

# Load audio
data, samplerate = sf.read(filename, dtype='float32')

# Lower volume
data = [[s * volume for s in frame] for frame in data]  # pure Python alternative

# Play
sd.play(data, samplerate=samplerate, device=device_index)
sd.wait()
