# Natural Language Voice Assistant - Docker Submission

## Overview
This is a local voice assistant that processes pre-recorded audio commands and generates spoken responses. It features:

- * Speech Recognition: Vosk ASR (Automatic Speech Recognition)
- * Text-to-Speech: pyttsx3 TTS engine
- * Natural Language Understanding*: Custom intent parsing with context tracking
- * Weather Integration*: Retrieves weather forecasts
- * Calendar Management*: Create, read, update, and delete appointments
- * Conversation Context*: Maintains state across multiple interactions

## Docker Setup (Hardware Limitation Workaround)

Due to Docker's inability to access microphone/speakers, this submission uses **batch audio file processing**:
- Input: Pre-recorded `.wav` audio files in `audio_samples/`
- Output: Generated TTS responses saved to `output/` directory
- Processing: Automatic batch processing of all test cases

## Project Structure

```
voice-assistant/
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose setup
├── requirements.txt            # Python dependencies
├── .dockerignore              # Files to exclude from Docker
├── README.md                   # This file
│
├── asr_tts_batch.py           # Main entry point (Docker mode)
├── asr_tts.py                 # Original live microphone version
├── assistant.py               # Intent handling and business logic
├── nlu.py                     # Natural language understanding
├── api_weather.py             # Weather API integration
├── api_calendar.py            # Calendar API integration
│
├── audio_samples/             # Test audio files (INPUT)
│   ├── 01_greeting.wav
│   ├── 02_weather_marburg.wav
│   ├── 03_check_rain.wav
│   ├── 04_create_appointment.wav
│   ├── 05_next_appointment.wav
│   ├── 06_update_location.wav
│   └── 07_delete_appointment.wav
│
├── output/                    # Generated responses (OUTPUT)
│   ├── greeting.wav
│   ├── response_01_greeting.wav
│   ├── response_02_weather_marburg.wav
│   └── results_summary.json
│
└── vosk-model-small-en-us-0.15/  # Downloaded automatically
```

## Building and Running

### Option 1: Using Docker (Recommended for submission)

```bash
# Build the Docker image
docker build -t voice-assistant .

# Run the container with volume mounts
docker run -v $(pwd)/audio_samples:/app/audio_samples:ro \
           -v $(pwd)/output:/app/output \
           voice-assistant
```

### Option 2: Using Docker Compose (Easier)

```bash
# Build and run
docker-compose up

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop and remove
docker-compose down
```

### Option 3: Local Development (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Download Vosk model
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip

# Run batch processing
python3 asr_tts_batch.py

# OR run with live microphone
python3 asr_tts.py
```

## Test Audio Files

The `audio_samples/` directory contains pre-recorded test cases demonstrating all features:

1. **01_greeting.wav** - "Hello"
2. **02_weather_marburg.wav** - "What will the weather be like in Marburg today?"
3. **03_check_rain.wav** - "Will it rain there tomorrow?"
4. **04_create_appointment.wav** - "Add an appointment titled Dentist for January 12th"
5. **05_next_appointment.wav** - "What is my next appointment?"
6. **06_update_location.wav** - "Change the location to Berlin"
7. **07_delete_appointment.wav** - "Delete the previously created appointment"

**Note**: These audio files MUST be:
- Format: WAV
- Sample Rate: 16000 Hz
- Channels: Mono (1 channel)
- Codec: PCM

### Creating Test Audio Files

You can create test audio files using:

```bash
# Using ffmpeg to convert audio
ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav

# Using SoX
sox input.mp3 -r 16000 -c 1 output.wav

# Using Python (record from microphone)
python3 -c "
import sounddevice as sd
import soundfile as sf
duration = 5  # seconds
print('Recording...')
audio = sd.rec(int(duration * 16000), samplerate=16000, channels=1)
sd.wait()
sf.write('output.wav', audio, 16000)
print('Saved!')
"
```

## Output

After processing, the `output/` directory will contain:

1. **Audio responses** - One `.wav` file per input command with TTS response
2. **results_summary.json** - Complete log of all interactions:

```json
[
  {
    "file": "01_greeting.wav",
    "transcription": "hello",
    "intent": {"intent": "greeting"},
    "response": "Hello! How can I help you?",
    "output_audio": "response_01_greeting.wav"
  },
  ...
]
```

## Supported Commands

### Weather
- "What will the weather be like in [city] [day]?"
- "Will it rain in [city] [day]?"
- Cities: Marburg, Frankfurt, Berlin, Hamburg, Munich, etc.
- Days: today, tomorrow, Monday, Tuesday, etc.

### Calendar
- "Add an appointment titled [title] for [date]"
- "What is my next appointment?"
- "Delete the previously created appointment"
- "Delete this appointment"
- "Change the location to [place]"

### General
- "Hello" / "Hi" - Greeting
- "How are you?" - Status check

### Context Features
The assistant remembers:
- Last mentioned place (for weather)
- Last mentioned day
- Last created appointment
- Last referenced appointment

## Technical Details

### Components

**ASR (Automatic Speech Recognition)**
- Engine: Vosk (offline, no cloud)
- Model: vosk-model-small-en-us-0.15 (40MB)
- Sample Rate: 16000 Hz

**NLU (Natural Language Understanding)**
- Custom rule-based parser
- Pattern matching with regex
- Fuzzy date/time extraction
- Context-aware interpretation

**TTS (Text-to-Speech)**
- Engine: pyttsx3
- Platform: Cross-platform (uses espeak on Linux)
- Rate: 170 words per minute

**State Management**
- Conversation context tracking
- Cross-turn reference resolution
- Last place/day memory

### Dependencies

- **vosk**: Offline speech recognition
- **soundfile**: Audio file I/O
- **pyttsx3**: Text-to-speech synthesis
- **requests**: HTTP API calls
- **python-dateutil**: Date parsing

## Verification

To verify the submission works correctly:

```bash
# 1. Build the image
docker build -t voice-assistant .

# 2. Run with test audio files
docker run -v $(pwd)/audio_samples:/app/audio_samples:ro \
           -v $(pwd)/output:/app/output \
           voice-assistant

# 3. Check output
ls -lh output/
cat output/results_summary.json

# 4. Listen to generated responses (on host machine)
# Use any audio player:
ffplay output/response_01_greeting.wav
# or
vlc output/response_01_greeting.wav
```

Expected output:
- ✅ 7 response audio files
- ✅ 1 results_summary.json
- ✅ All intents correctly identified
- ✅ Context maintained across interactions

## Troubleshooting

### Issue: "Vosk model not found"
**Solution**: The Dockerfile automatically downloads it. If building fails, manually download:
```bash
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
```

### Issue: "No .wav files found"
**Solution**: Ensure `audio_samples/` directory exists and contains `.wav` files

### Issue: "Sample rate must be 16000Hz"
**Solution**: Convert audio files:
```bash
ffmpeg -i input.wav -ar 16000 -ac 1 output_16k.wav
```

### Issue: "Could not transcribe audio"
**Solution**:
- Check audio quality
- Ensure mono (1 channel)
- Speak clearly with minimal background noise
- Verify file isn't corrupted

## API Configuration

### Weather API
Located in `api_weather.py`. Update the API endpoint if needed:
```python
API_URL = "http://your-weather-api.com"
```

### Calendar API
Located in `api_calendar.py`. Configure your calendar backend:
```python
CALENDAR_API = "http://your-calendar-api.com"
```

## License

This project is submitted as part of an academic assignment.

## Author

Ganesh Bhorkar
RWTH Aachen University

## Submission Information

**Submission Method**: RWTH Gigamove File Transfer
**Submission URL**: https://gigamove.rwth-aachen.de/en
**Submission Format**: Download link to Docker package

**Contents**:
- Complete source code
- Dockerfile and docker-compose.yml
- Test audio samples
- This README with full documentation
- All dependencies in requirements.txt

---

## Quick Start Summary

```bash
# Clone and navigate
git clone <your-repo>
cd voice-assistant

# Build Docker image
docker build -t voice-assistant .

# Run with test files
docker run -v $(pwd)/audio_samples:/app/audio_samples:ro \
           -v $(pwd)/output:/app/output \
           voice-assistant

# Check results
ls output/
cat output/results_summary.json
```

**For evaluation**: All test audio files are included. Simply run the Docker container and check the `output/` directory for results.