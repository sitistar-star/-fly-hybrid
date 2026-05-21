---
name: voice-interface
description: "Set up voice input for Hermes Agent on Windows. Covers Web Speech API approach (reliable) and python native GUI pitfalls."
version: 1.0
author: Hermes Agent
tags: [voice, stt, speech-to-text, windows, web-speech-api, gui]
---

# Voice Interface for Hermes Agent on Windows

## When to use

Use this skill when the user asks to:
- Add voice/speech input to Hermes
- Build a voice-enabled chat client
- "Говорить голосом а не писать" (speak instead of type)
- Use microphone with Hermes

## Architecture (proven working)

The **only reliable approach on this Windows setup** is a local HTTP server + browser frontend:

```
Python HTTP server (port 10997)  ←→  Chrome browser (Web Speech API)
        │
        ▼
  Hermes CLI (subprocess)
```

Chrome's Web Speech API handles STT (Russian + English, accurate, free). The Python server bridges to Hermes.

## Components

### 1. HTTP Server (`server.py`)
Single-file server handling:
- `GET /` — serves the HTML chat UI
- `POST /chat` — receives text, calls `hermes chat -q`, returns response
- File upload via multipart form

```python
# Minimal skeleton
from http.server import HTTPServer, BaseHTTPRequestHandler
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # serve HTML
    def do_POST(self): # handle /chat
server = HTTPServer(("127.0.0.1", 10997), Handler)
```

### 2. HTML Frontend (`index.html`)
- Web Speech API for voice (`window.SpeechRecognition`)
- Chat bubbles with user/AI separation
- Dark calm theme (see color preferences below)
- Drag-and-drop file upload
- Session management (local JS)

Key JS for voice:
```javascript
const sr = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
sr.lang = 'ru-RU';
sr.onresult = e => { text = e.results[0][0].transcript; send(text); };
```

### 3. Hermes Bridge
```python
subprocess.run(
    [str(HERMES_VENV), "-m", "hermes_cli.main", "chat", "-q", text, "-Q"],
    capture_output=True, text=True, timeout=120,
    env={**os.environ, "HERMES_HOME": str(HERMES_HOME)}
)
```

## Pitfalls & Gotchas

### ❌ DO NOT USE: tkinter / PySide6 / PyQt for GUI
- Windows created via `pythonw.exe` are **invisible** when launched from git-bash
- tkinter gives `RuntimeError: main thread is not in main loop` when updating UI from threads
- PySide6 windows often crash silently — no error output visible
- **Solution:** always use web-based UI served from local Python HTTP server

### ❌ DO NOT USE: `pythonw.exe` for debugging
- Crashes are invisible (no console)
- **Solution:** use `python.exe` for development, switch to `pythonw.exe` only after confirming it works

### ❌ Threading in Python GUI
- tkinter/PySide6: UI updates MUST happen on the main thread
- Use `root.after(0, lambda: ...)` for thread-safe UI updates
- Better yet: avoid native GUI entirely — use web frontend

### ✅ Web Speech API Notes
- Works in Chrome only. Edge may work. Firefox doesn't support it.
- Uses Google's servers for STT — requires internet
- Russian language supported (`lang='ru-RU'`)
- Continuous mode: set `continuous = true` + track `interimResults`
- Session persistence: store in JS object, not SQLite on client side

### ✅ Local Whisper (faster-whisper)
- Requires `pip install faster-whisper sounddevice`
- Model `small` (~500MB RAM) good balance of speed/accuracy
- Model `tiny` (~150MB RAM) faster but less accurate
- `compute_type="int8"` for CPU optimization
- `vad_filter=True` filters silence
- First load downloads model (~30s)
- Sounddevice lists devices via `sd.query_devices()`

### Port Management
- Use different ports for different services (10997 chat, 10998 static, 10999 voice)
- `Get-NetTCPConnection -LocalPort 10997 -ErrorAction SilentlyContinue` to check
- TIME_WAIT state can block restart — wait 2-3 seconds

## User UI Preferences

When creating web UI for this user, use this calm color palette:

```css
--bg: #1a1b2e;       /* warm dark */
--surface: #222338;   /* muted dark */
--surface2: #2a2b40;
--text: #e2ddd6;      /* warm cream */
--subtext: #a8998a;   /* warm gray */
--muted: #6a5d4f;     /* brown-gray */
--accent: #d4a373;    /* peach/terracotta */
--accent2: #e0bc90;   /* light peach */
--green: #9abb8a;     /* sage */
--red: #c47a7a;       /* muted rose */
--border: #2f2f44;
```

Fonts: Inter for UI, Literata for body/reading. No neon, no high contrast.

## Startup

Create a `.bat` file on Desktop:
```batch
@echo off
cd /d "C:\Users\sitis\voicebridge"
start /B "" "C:\Users\sitis\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe" hermes_chat_server.py
timeout /t 3 /nobreak >nul
start "" http://127.0.0.1:10997
pause
```

Add to Windows Startup for permanent access.
