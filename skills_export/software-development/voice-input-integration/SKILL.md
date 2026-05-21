---
name: voice-input-integration
description: "Add voice input to Hermes Agent on Windows — browser Web Speech API, faster-whisper desktop, or gateway voice messages. Ranked by reliability, with known pitfalls."
author: Hermes Agent
platforms: [windows]
---

# Voice Input Integration for Hermes

Add voice input so the user can speak instead of typing. Multiple approaches tested on Windows — use the **Web Speech API (Chrome) + local server** approach by default; it is the most reliable.

## Decision Matrix

| Method | Reliability | Setup | Latency | Offline | Notes |
|--------|------------|-------|---------|---------|-------|
| **Web Speech API + HTTP server** ⭐ | ★★★★★ | None (browser built-in) | <1s | No | **Recommended.** Chrome sends to Google servers, most accurate |
| **faster-whisper desktop (PySide6)** | ★★★☆☆ | pip install | 2-5s | Yes | Good but threading issues, first-load delay |
| **faster-whisper desktop (tkinter)** | ★★☆☆☆ | pip install | 2-5s | Yes | NOT recommended — tkinter threading crashes on non-main-thread UI calls |
| **faster-whisper CLI (hotkey)** | ★★★☆☆ | pip install + admin rights | 2-5s | Yes | Works but user must know hotkey (avoid Scroll Lock, use Ctrl+Shift+V) |
| **Telegram voice messages** | ★★★★☆ | Gateway + faster-whisper | 2-5s | No* | Good if user has Telegram, gateway must be running |

## Recommended: Web Speech API + Local HTTP Server

### Architecture

```
User speaks in Chrome → Web Speech API → POST /save_text → queue.jsonl → Hermes reads queue
```

### Implementation

1. Write `voicebridge_server.py` — Python HTTP server on `127.0.0.1:10999` that:
   - Serves an HTML page with a microphone button
   - Accepts POST `/save_text` with `{"text": "..."}` from the browser
   - Writes to `voice_queue.jsonl`
   - (Optional) Also handles POST `/chat` for full chat client

2. Write `voicebridge.htm` — HTML page with:
   - Big round microphone button
   - `mousedown`/`mouseup` and `touchstart`/`touchend` for push-to-talk
   - `SpeechRecognition` / `webkitSpeechRecognition` with `lang='ru-RU'`
   - `fetch('/save_text', ...)` to send transcribed text
   - Space key binding as alternative trigger

3. Open in user's Chrome via Kimi WebBridge:
   ```bash
   curl -s -X POST http://127.0.0.1:10086/command \
     -d '{"action":"navigate","args":{"url":"http://127.0.0.1:10999/","newTab":true},"session":"voice"}'
   ```

4. From this chat session, poll `voice_queue.jsonl`:
   ```python
   with open("voice_queue.jsonl") as f:
       entries = [json.loads(l) for l in f if l.strip()]
   ```

### HTML Key Code

```javascript
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.lang = 'ru-RU';
recognition.continuous = false;
recognition.interimResults = false;

mic.addEventListener('mousedown', () => recognition.start());
mic.addEventListener('mouseup', () => recognition.stop());
recognition.onresult = (e) => {
  const text = e.results[0][0].transcript;
  fetch('/save_text', { method:'POST', body: JSON.stringify({text}) });
};
```

## Alternative: faster-whisper Desktop (PySide6, not tkinter)

Use this when the user wants a native offline desktop app.

### Critical Pitfalls

| Pitfall | Fix |
|---------|-----|
| **tkinter threading crash** | `RuntimeError: main thread is not in main loop` when calling `widget.config()` from worker thread. Use `root.after(0, lambda: ...)` or switch to PySide6 which handles cross-thread signals |
| **pythonw.exe silent exit** | pythonw swallows all stderr. Test with `python.exe` first, wrap in try/except, log to file |
| **STT model load in thread** | WhisperModel() blocks for 10-30s on first load. Must load in daemon thread. Use `root.after()` for UI updates from thread |
| **faster-whisper not in venv** | Hermes venv has pip stripped. Use `python -m ensurepip` then `pip install faster-whisper sounddevice numpy` |
| **Desktop path via OneDrive** | `os.path.expanduser("~/Desktop")` returns `C:\Users\user\Desktop` but real Desktop may be `C:\Users\user\OneDrive\Desktop`. Use `[Environment]::GetFolderPath('Desktop')` via PowerShell or `ctypes` |
| **Hermes venv path** | On Windows with git-bash: HERMES_HOME is `~/AppData/Local/hermes`, NOT `~/.hermes`. The venv is at `$HERMES_HOME/hermes-agent/venv/Scripts/python.exe` |

## User Preferences (this user)

- Desktop app preferred over browser or CLI
- AntiGravity (VS Code fork) as IDE for project work
- Clean desktop — no leftover shortcuts after cleanup
- Hotkeys should be common keys (Ctrl+Shift+V, not Scroll Lock)
- "перезагружайся когда остановка" — agent should self-heal when stalled
- Russian language, but also types in English keyboard layout accidentally

## References

- `references/gateway-watchdog.md` in this skill directory
- `references/voice-queue-architecture.md`
