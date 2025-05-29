import subprocess

AUDIO_DEVICE = "default:CARD=ArrayUAC10"  # Find with: arecord -L

def play_wav(path):
    subprocess.run(["aplay", "-q", "-D", AUDIO_DEVICE, path])
