---
name: voice-input
description: Set up voice/speech input for Hermes Agent — local STT with faster-whisper, microphone capture, GUI integration, cross-process queue delivery.
version: 1.0.0
author: Agent (derived from session)
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [voice, speech, stt, whisper, microphone, voicebridge]
    related_skills: [parallel-processing, gateway-ops]
---

# Voice Input (voice-input)

Enable voice input to Hermes Agent — speak instead of type. Speech is transcribed
locally (no internet, no API keys) via faster-whisper and delivered to the active
Hermes session.

---

## Quick Start

```bash
# 1. Install dependencies into Hermes venv (or your own)
pip install faster-whisper sounddevice

# 2. Run the GUI app
pythonw.exe voicebridge.py
```

---

## Components

| Component | Package | Purpose |
|-----------|---------|---------|
| Audio capture | `sounddevice` | Microphone input, cross-platform |
| STT engine | `faster-whisper` | Local speech-to-text (small model = ~500MB RAM) |
| GUI | `tkinter` (built-in) | Desktop window with mic button + chat history |
| Hermes bridge | Queue file (JSONL) | Cross-process text delivery (see `parallel-processing`) |

### Model Sizes

| Model | RAM | Speed (CPU) | Accuracy |
|-------|-----|-------------|----------|
| `tiny` | ~150 MB | Very fast | Low |
| `base` | ~300 MB | Fast | OK |
| `small` (recommended) | ~500 MB | Moderate | Good |
| `medium` | ~1.5 GB | Slow | Better |
| `large-v3` | ~3 GB | Very slow | Best |

For real-time voice input on CPU, use `small` with `compute_type="int8"`.

---

## Architecture

```
Microphone → sounddevice (capture) → faster-whisper (transcribe) → queue.jsonl → Hermes reads & responds
```

Two processes:
1. **VoiceBridge** (GUI app) — records and transcribes
2. **Hermes** — polls the queue file and processes text

They communicate through a shared JSONL queue file at a known path.

---

## VoiceBridge GUI

A tkinter desktop app with:
- 🎤 Push-to-talk button (press to speak, release to send)
- Text input field (type as fallback)
- Chat history display
- Dark theme
- Status indicator

### Hotkeys
- `Ctrl+V` — toggle microphone (push-to-talk)
- `Enter` — send typed text

### Running

```bash
# With console (for debugging)
python.exe voicebridge.py

# Without console (clean Windows experience)
pythonw.exe voicebridge.py
```

On Windows, always use `pythonw.exe` for GUI apps launched from terminal.

### Creating a Desktop Shortcut

```batch
@echo off
start /B "" "C:\path\to\pythonw.exe" "C:\path\to\voicebridge.py"
```

Place this `.bat` on the Desktop. The user double-clicks it to launch VoiceBridge.

---

## Windows Desktop Path Note

With OneDrive sync, the real Desktop is at `OneDrive\Desktop`, not the local
`Desktop` folder. Use PowerShell to resolve:

```powershell
$desktop = [Environment]::GetFolderPath('Desktop')
# Returns C:\Users\user\OneDrive\Desktop (or C:\Users\user\Desktop if no OneDrive)
```

Do NOT hardcode `C:\Users\user\Desktop`.

---

## Polling Pattern

When the user has VoiceBridge open and is speaking, **check proactively** — do not
wait for the user to say "проверь" (check). The user preference is "проверяй всегда"
(check always) — after every voice input, verify if a new queue entry appeared and
respond immediately.

### How to Poll

After each response to the user (or when they indicate they've spoken), run:

```python
# Check the queue file for new entries
# Return the latest unseen text or NO_INPUT
```

Integrate this into the conversation flow:
1. User indicates they spoke (or you offered voice input)
2. Poll the queue
3. If new input found → process it and respond
4. If no input → tell the user the queue is empty, ask them to try again

The first run downloads the whisper model (~500 MB for `small`). Subsequent runs
use the cached model and start instantly.

Model cache location: `~/.cache/whisper/` (or the HF_HOME cache directory).

If the download is slow, set `model_size="tiny"` in the code for a quick test,
then switch to `small` later.

---

## Troubleshooting

### "No module named 'faster_whisper'"
```bash
pip install faster-whisper sounddevice
```

### "No microphone device found"
Check available devices:
```python
import sounddevice as sd
print(sd.query_devices())
```
Look for devices with `max_input_channels > 0`.

### Audio too quiet / no speech detected
Adjust the VAD threshold in the capture code (lower = more sensitive):
```python
silence_threshold = 0.02  # default
```

### Queue file not being read
The Hermes agent reads the queue on request. The user says проверить (check) or
the agent polls periodically. Ensure the queue.jsonl path is the same in both
the writer (VoiceBridge) and reader (Hermes listener script).

---

## References

- `parallel-processing` — Queue file pattern, background processes
- `felo-mindmap` — Example of a skill that makes API calls
