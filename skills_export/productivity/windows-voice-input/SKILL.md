---
name: windows-voice-input
description: "Build and operate local voice input (STT) for Hermes Agent on Windows — microphone capture, faster-whisper transcription, desktop GUI with tkinter, and queue-based integration with the active Hermes session. Covers the full pipeline from installing dependencies to speaking into a desktop app and having the transcribed text arrive in the agent conversation."
version: 1.0.0
author: Agent (derived from session)
platforms: [windows]
metadata:
  hermes:
    tags: [voice, stt, speech-to-text, whisper, windows, desktop, gui]
    related_skills: [background-delegation]
---

# Windows Voice Input (VoiceBridge)

Local speech-to-text for Hermes Agent on Windows. No internet required — runs faster-whisper locally.

## Architecture

```
Microphone → sounddevice → numpy array → faster-whisper → voice_queue.jsonl → Hermes Agent (this session)
```

The desktop app (tkinter) captures audio, transcribes it, writes to a queue file. The Hermes agent reads the queue file to get voice input in its active conversation.

## Quick Start

### 1. Install dependencies into Hermes venv

Ensure `pip` is available (Hermes venv may strip it during install):

```bash
# If pip missing, install it:
curl -sL https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
/c/Users/<user>/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe /tmp/get-pip.py

# Install voice packages:
/c/Users/<user>/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -m pip install faster-whisper sounddevice keyboard
```

**Packages installed:**
| Package | Size | Purpose |
|---------|------|---------|
| faster-whisper | ~500 MB RAM at runtime | Local STT (small model = good balance of speed/accuracy) |
| sounddevice | 365 KB | Microphone capture via PortAudio |
| keyboard | 58 KB | Global hotkeys (optional) |
| numpy | already in venv | Audio data handling |
| ctranslate2 | 18.8 MB | Whisper inference engine |
| onnxruntime | 13 MB | ONNX backend for ctranslate2 |

### 2. Create the VoiceBridge app

A tkinter desktop app with:
- **🎤 Talk button** — press and hold to record, release to transcribe  
- **Text input field** — fallback for typing  
- **Chat display** — history of voice/text exchanges  
- **Status bar** — shows model load state, recording state

Key files at `C:\Users\<user>\voicebridge\`:

| File | Purpose |
|------|---------|
| `voicebridge.py` | Main app (tkinter GUI + audio pipeline) |
| `voice_listener.py` | Reads queue file — call from Hermes to check for new input |
| `voice_queue.jsonl` | Shared queue: VoiceBridge writes, Hermes reads |
| `voicebridge_gui.bat` | Launch shortcut (double-click to start) |
| `test_voicebridge.py` | Quick sanity check: test mic + imports |

### 3. Launch

```bash
# Use pythonw.exe (no console window) so tkinter renders properly:
powershell.exe -Command "Start-Process -FilePath 'C:\Users\<user>\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe' -ArgumentList 'C:\Users\<user>\voicebridge\voicebridge.py' -WindowStyle Normal"
```

Or double-click `voicebridge_gui.bat`.

### 4. Speak into the conversation

The VoiceBridge app writes transcribed text to `voice_queue.jsonl`. To read it in the current Hermes conversation:

```python
# From execute_code or terminal — check for new voice input:
import json
from pathlib import Path

queue = Path("C:/Users/<user>/voicebridge/voice_queue.jsonl")
if queue.exists():
    lines = [l.strip() for l in open(queue) if l.strip()]
    for line in lines:
        entry = json.loads(line)
        print(f"Voice input: {entry['text']}")
```

Or use the dedicated listener script:
```bash
python /c/Users/<user>/voicebridge/voice_listener.py
```

## Implementation Details

### Audio Capture (sounddevice)

```python
import sounddevice as sd
import numpy as np

# Record N seconds at 16kHz mono:
recording = sd.rec(int(duration * 16000), samplerate=16000, channels=1)
sd.wait()  # blocks until done
audio = recording.flatten()  # → numpy array for whisper
```

For push-to-talk (record while button held):
```python
self.recording = True
self.audio_buffer = []

def callback(indata, frames, time_info, status):
    if self.recording:
        self.audio_buffer.append(indata.copy())

with sd.InputStream(samplerate=16000, channels=1, callback=callback):
    while self.recording:
        sd.sleep(100)

# On release:
audio = np.concatenate(self.audio_buffer, axis=0).flatten()
```

### STT (faster-whisper)

```python
from faster_whisper import WhisperModel

model = WhisperModel("small", device="cpu", compute_type="int8")
segments, info = model.transcribe(
    audio_data, beam_size=5, language="ru",
    vad_filter=True  # Voice Activity Detection — filters silence
)
text = " ".join(seg.text for seg in segments)
```

**Model sizes:**
| Model | RAM | Accuracy | Speed (CPU) |
|-------|-----|----------|-------------|
| tiny | ~150 MB | OK | Very fast |
| base | ~250 MB | Good | Fast |
| small | ~500 MB | Very good | Moderate ← default |
| medium | ~1.5 GB | Excellent | Slow |
| large-v3 | ~3 GB | Best | Very slow |

### Queue Integration (VoiceBridge ↔ Hermes)

VoiceBridge writes each transcribed utterance as a JSON line:
```python
{"timestamp": "2026-05-20T21:38:10", "text": "привет", "id": "voice_12345"}
```

Hermes reads the queue via `voice_listener.py` or `execute_code`. The listener tracks which entries it has already seen via `.voice_seen.txt`.

### UI Caveat on Windows

When launching from **git-bash (MSYS2)**, tkinter may not render properly as a subprocess. Always use:
- `pythonw.exe` (not `python.exe`) for GUI apps on Windows
- `Start-Process` via PowerShell
- Or double-click a `.bat` file

The `background=True` terminal mode in git-bash will show the process as "running" but the tkinter window may not appear. Use `Start-Process` or `pythonw.exe` directly.

## Verification

Run the test script to confirm audio + STT work:

```bash
python /c/Users/<user>/voicebridge/test_voicebridge.py
```

Expected output:
```
✓ sounddevice 0.5.5
✓ faster-whisper
✓ tkinter
✓ numpy
✓ Микрофонов найдено: N
✓ Записано: 16000 семплов
✅ Все проверки пройдены!
```

## Audio Device Troubleshooting

List available microphones:
```python
import sounddevice as sd
devices = sd.query_devices()
input_devices = [d for d in devices if d['max_input_channels'] > 0]
for d in input_devices:
    print(d['name'], d['max_input_channels'], 'channels')
```

Common issues:
- **No input devices** → Check Windows Sound Settings → Input device
- **Audio is silent** → Check microphone privacy settings (Windows → Microphone privacy)
- **sounddevice not found** → Install via `pip install sounddevice`
- **Whisper model download fails** → First load downloads ~500 MB; ensure stable internet

## Key User Preferences (DO NOT VIOLATE)

- The user wants to **speak instead of type** — make voice input the primary interaction mode, not an afterthought
- Voice input should go to the **current Hermes conversation**, not a separate session
- The user expects **push-to-talk** (hold button → speak → release → send), not continuous listening
- Status feedback is essential: show "listening", "processing", "sent" states clearly
