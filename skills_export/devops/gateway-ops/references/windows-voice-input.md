# Voice Input for Hermes on Windows

Practical approaches for enabling voice-to-text input to Hermes on Windows, ordered by reliability.

## Architecture Comparison

| Approach | Reliability | Dependencies | Notes |
|----------|-------------|--------------|-------|
| **Web Speech API** | ★★★★★ | Browser (Chrome) | Best — works out of box |
| **tkinter GUI** | ★★★☆☆ | Python tkinter | Window may not render from git-bash |
| **CLI hotkey** | ★★☆☆☆ | keyboard lib | Requires admin? Unreliable in git-bash |
| **PowerShell SAPI** | ★★☆☆☆ | System.Speech | Limited accuracy, needs Windows Speech feature |

## Recommended: Web Speech API + Local HTTP Server

This is the most reliable approach for Hermes-on-Windows voice input.

### Architecture

```
Chrome (Speech API) → HTTP POST → Python server → voice_queue.jsonl → Hermes reads
```

### Server

A minimal Python HTTP server (`http.server.HTTPServer`) listens on `127.0.0.1:10999`:

```python
# Serves an HTML page with 🎤 button at GET /
# Accepts POST /save_text with JSON {"text": "...", "timestamp": "..."}
# Appends to voice_queue.jsonl
```

### Client

A single HTML page using the Web Speech API:

```html
<script>
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.lang = 'ru-RU';
recognition.continuous = false;
recognition.interimResults = false;

mic.addEventListener('mousedown', () => recognition.start());  // Hold to speak
mic.addEventListener('mouseup', () => recognition.stop());      // Release to send

recognition.onresult = (event) => {
  const text = event.results[0][0].transcript;
  fetch('/save_text', { method: 'POST', body: JSON.stringify({ text }) });
};
</script>
```

### Launch

```bash
# Start server (background)
pythonw.exe voicebridge_server.py

# Open in Chrome
start http://127.0.0.1:10999
```

### Why This Works

- Chrome's Web Speech API uses Google's cloud STT — accurate, handles Russian well
- No local model download, no GPU, no Python audio packages
- Push-to-talk pattern: hold 🎤 → speak → release → text is sent
- Works in any Chrome window, no admin rights needed

## Failed/Unreliable Approaches

### tkinter GUI via git-bash
Tkinter windows launched as subprocesses from git-bash (MSYS2) often fail to render or appear off-screen. Even `pythonw.exe` doesn't guarantee visibility. Symptom: `Get-Process` shows the process running with MainWindowTitle set, but no window appears on screen.

### keyboard module global hotkeys
The `keyboard` library for Python hooks `SetWindowsHookEx` which may not fire when Python runs inside MSYS2's pseudo-console. Hotkeys (Ctrl+Shift+V, Scroll Lock) would register but never trigger the callback.

### PowerShell System.Speech
Windows built-in speech recognition via `System.Speech.Recognition.SpeechRecognitionEngine` has poor accuracy for Russian and requires the Windows Speech Recognition feature to be installed (not present by default on Windows 10/11 Home).

## Project Layout

```
voicebridge/
├── voicebridge_server.py    # Python HTTP server
├── voicebridge.htm          # HTML page with 🎤 button
├── voice_queue.jsonl        # Queue file (Hermes reads this)
├── voice_listener.py        # Hermes-side reader for queue
└── VoiceBridge.bat          # Desktop shortcut (starts server + opens browser)
```

## Hermes-Side Integration

The Hermes agent reads `voice_queue.jsonl` via `voice_listener.py`:

```python
# Returns new (unseen) voice inputs
def get_new_voice_input():
    # read queue file, track seen IDs in .voice_seen.txt
    # return [{"text": "...", "id": "...", "timestamp": "..."}]
```

The user says "проверь" to trigger a check, or the agent checks automatically if configured for always-listening mode.
