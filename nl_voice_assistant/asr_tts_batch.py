"""
Modified ASR_TTS for Docker - Batch Processing with Audio Files
Processes pre-recorded audio files instead of live microphone
"""

import json
import sys
import os
import wave
import numpy as np

from vosk import Model, KaldiRecognizer
import pyttsx3

from assistant import handle_intent
from nlu import parse_intent

# CONFIGURATION
MODEL_PATH = "vosk-model-small-en-us-0.15"
SAMPLE_RATE = 16000
AUDIO_SAMPLES_DIR = "audio_samples"
OUTPUT_DIR = "output"

print("=" * 60)
print("Voice Assistant - Docker Batch Processing Mode")
print("=" * 60)

# ================= CHECK MODEL =================
if not os.path.exists(MODEL_PATH):
    print("ERROR: Vosk model not found at", MODEL_PATH)
    sys.exit(1)

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ================= ASR SETUP =================
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)

# ================= TTS TO FILE =================
def speak_to_file(text, output_path):
    """Generate TTS and save to file instead of playing"""
    print(f"Assistant: {text}")

    engine = pyttsx3.init()
    engine.setProperty("rate", 170)

    # Save to file
    engine.save_to_file(text, output_path)
    engine.runAndWait()
    engine.stop()

    print(f"  → Saved audio response to: {output_path}")

# ================= PROCESS AUDIO FILE =================
def process_audio_file(audio_path):
    """Process a single WAV audio file and return transcription"""
    print(f"\n📁 Processing: {audio_path}")

    recognizer.Reset()

    try:
        # Read WAV file
        with wave.open(audio_path, "rb") as wf:
            if wf.getnchannels() != 1:
                print("  ⚠️  Warning: Audio must be mono. Skipping.")
                return None
            if wf.getframerate() != SAMPLE_RATE:
                print(f"  ⚠️  Warning: Sample rate must be {SAMPLE_RATE}Hz. Skipping.")
                return None

            # Process audio in chunks
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break

                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "").strip()
                    if text:
                        return text

            # Get final result
            final_result = json.loads(recognizer.FinalResult())
            text = final_result.get("text", "").strip()
            return text if text else None

    except Exception as e:
        print(f"  ❌ Error processing audio: {e}")
        return None

# ================= BATCH PROCESSING =================
def process_all_audio_files():
    """Process all audio files in the audio_samples directory"""

    if not os.path.exists(AUDIO_SAMPLES_DIR):
        print(f"\n❌ ERROR: Directory '{AUDIO_SAMPLES_DIR}' not found!")
        print("Please create the directory and add your test audio files (.wav)")
        return

    # Get all WAV files
    audio_files = [f for f in os.listdir(AUDIO_SAMPLES_DIR) if f.endswith('.wav')]

    if not audio_files:
        print(f"\n❌ No .wav files found in '{AUDIO_SAMPLES_DIR}'")
        return

    print(f"\n✅ Found {len(audio_files)} audio file(s) to process\n")

    # Initialize conversation state
    conversation_state = {
        "last_place": None,
        "last_day": None,
        "last_created_event_id": None,
        "last_referenced_event_id": None
    }

    # Process results log
    results_log = []

    # Process each audio file
    for idx, audio_file in enumerate(sorted(audio_files), 1):
        print("=" * 60)
        print(f"Test {idx}/{len(audio_files)}: {audio_file}")
        print("=" * 60)

        audio_path = os.path.join(AUDIO_SAMPLES_DIR, audio_file)

        # Transcribe audio
        user_text = process_audio_file(audio_path)

        if not user_text:
            print("  ❌ Could not transcribe audio")
            results_log.append({
                "file": audio_file,
                "transcription": None,
                "intent": None,
                "response": "Failed to transcribe"
            })
            continue

        print(f"👤 User: {user_text}")

        # Parse intent
        intent_data = parse_intent(user_text, conversation_state)
        print(f"🧠 Intent: {intent_data}")

        # Generate response
        response_text = handle_intent(intent_data, conversation_state)

        # Save TTS response
        output_filename = f"response_{idx:02d}_{os.path.splitext(audio_file)[0]}.wav"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        speak_to_file(response_text, output_path)

        # Log result
        results_log.append({
            "file": audio_file,
            "transcription": user_text,
            "intent": intent_data,
            "response": response_text,
            "output_audio": output_filename
        })

        print("✅ Completed\n")

    # Save results summary
    summary_path = os.path.join(OUTPUT_DIR, "results_summary.json")
    with open(summary_path, "w") as f:
        json.dump(results_log, f, indent=2, default=str)

    print("=" * 60)
    print(f"✅ Processing complete! Results saved to: {summary_path}")
    print("=" * 60)
    print(f"\nProcessed {len(audio_files)} audio files")
    print(f"Output directory: {OUTPUT_DIR}/")
    print("\nGenerated files:")
    print(f"  - {len(audio_files)} audio responses (.wav)")
    print(f"  - 1 results summary (results_summary.json)")

# ================= MAIN =================
if __name__ == "__main__":
    try:
        # Initial greeting
        greeting_path = os.path.join(OUTPUT_DIR, "greeting.wav")
        speak_to_file("Hello. I am your voice assistant. Processing audio samples.", greeting_path)

        # Process all audio files
        process_all_audio_files()

        # Farewell
        farewell_path = os.path.join(OUTPUT_DIR, "farewell.wav")
        speak_to_file("Processing complete. Goodbye!", farewell_path)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)