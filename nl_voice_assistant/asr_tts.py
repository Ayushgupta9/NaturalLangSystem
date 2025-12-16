import json
import queue
import sys
import os
import subprocess
import sounddevice as sd
from vosk import Model, KaldiRecognizer

# ======================================================
# CONFIGURATION
# ======================================================
MODEL_PATH = "vosk-model-small-en-us-0.15"
SAMPLE_RATE = 16000

print("ASR_TTS program started")

# ======================================================
# CHECK MODEL
# ======================================================
if not os.path.exists(MODEL_PATH):
    print("ERROR: Vosk model not found")
    sys.exit(1)

# ======================================================
# LOAD ASR
# ======================================================
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)

audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    audio_queue.put(bytes(indata))

# ======================================================
# WINDOWS NATIVE TTS (GUARANTEED)
# ======================================================
def speak(text):
    print("Assistant:", text)
    ps_command = f'''
    Add-Type -AssemblyName System.Speech;
    $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer;
    $speak.Speak("{text}");
    '''
    subprocess.run(
        ["powershell", "-Command", ps_command],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

# ======================================================
# LISTEN ONCE
# ======================================================
def listen_once():
    print("Listening... Speak now.")
    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=audio_callback
    ):
        while True:
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip()
                if text:
                    return text

# ======================================================
# MAIN LOOP (SEQUENTIAL)
# ======================================================
if __name__ == "__main__":
    try:
        speak("Hello. I am your voice assistant.")

        while True:
            user_text = listen_once()
            print("User:", user_text)
            speak("You said " + user_text)

    except KeyboardInterrupt:
        speak("Goodbye!")
        print("\nProgram stopped by user.")
        sys.exit(0)
