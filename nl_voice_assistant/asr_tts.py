import json
import queue
import sys
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import pyttsx3
import os

MODEL_PATH = "vosk-model-small-en-us-0.15"  # adjust if your folder differs
SAMPLE_RATE = 16000

# ------------------------
# 1. Load ASR model
# ------------------------
if not os.path.exists(MODEL_PATH):
    print(f"ERROR: Vosk model not found at {MODEL_PATH}. Download and unzip it there.")
    sys.exit(1)

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)

audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    """Callback from sounddevice for streaming audio to a queue."""
    if status:
        print("Audio status:", status, file=sys.stderr)
    audio_queue.put(bytes(indata))

# ------------------------
# 2. Text-to-Speech setup
# ------------------------
tts = pyttsx3.init()

def speak(text):
    print("Assistant:", text)
    tts.say(text)
    tts.runAndWait()

# ------------------------
# 3. Speech Recognition loop
# ------------------------
def listen():
    print("Listening... Speak now! (press Ctrl+C to stop)")
    try:
        with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000,
                               dtype="int16", channels=1, callback=audio_callback):
            while True:
                data = audio_queue.get()
                if recognizer.AcceptWaveform(data):
                    result = recognizer.Result()
                    result_json = json.loads(result)
                    # result_json contains {"text": "..."}
                    return result_json.get("text", "")
    except KeyboardInterrupt:
        print("Interrupted by user")
        return ""
    except Exception as e:
        print("Error in audio input:", e)
        return ""

# ------------------------
# 4. Main program
# ------------------------
if __name__ == "__main__":
    speak("Hello, I am your test assistant. Please say something.")
    text = listen()
    if text:
        print("You said:", text)
        speak("You said: " + text)
    else:
        print("No text recognized.")
        speak("I did not catch that. Please try again.")
