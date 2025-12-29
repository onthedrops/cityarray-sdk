"""
CITYARRAY Voice Input
Record and transcribe speech
"""

import subprocess
import whisper
import os

DEVICE = "plughw:2,0"
model = None

def load_model():
    global model
    if model is None:
        print("Loading Whisper model...")
        model = whisper.load_model("tiny")
        print("Whisper ready!")
    return model

def record(duration=4, filename="voice_input.wav"):
    """Record audio from microphone."""
    print(f"Recording for {duration} seconds...")
    subprocess.run([
        "arecord", "-D", DEVICE, "-f", "cd",
        "-d", str(duration), filename
    ], capture_output=True)
    print("Recording done.")
    return filename

def transcribe(filename="voice_input.wav"):
    """Transcribe audio file to text."""
    m = load_model()
    result = m.transcribe(filename)
    text = result["text"].strip()
    return text

def listen(duration=4):
    """Record and transcribe in one step."""
    filename = record(duration)
    text = transcribe(filename)
    return text

if __name__ == "__main__":
    print("=== Voice Input Test ===\n")
    load_model()
    
    print("\nSpeak now...")
    text = listen(4)
    print(f"\nYou said: {text}")
