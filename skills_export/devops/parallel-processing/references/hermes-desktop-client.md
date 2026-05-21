# Building Custom Hermes Desktop Clients

Pattern for building native desktop applications that communicate with Hermes Agent.
This reference covers the architecture used in the **Hermes Terminal** project.

## Architecture

```
┌─────────────────────────────────────────────────┐
│            Custom Desktop Client                 │
├─────────────────┬───────────────────────────────┤
│  Frontend (GUI) │  Backend (Python)              │
│                 │                                │
│  • Chat display │  • HermesBridge (subprocess)   │
│  • Text input   │  • SessionManager (SQLite)     │
│  • Voice button │  • STT engine                  │
│  • File attach  │  • Queue file handler          │
└─────────────────┴───────────────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   Hermes Agent      │
              │  (hermes chat -q)   │
              └─────────────────────┘
```

## Framework Choice

| Framework | Verdict | Reason |
|-----------|---------|--------|
| **PySide6** | ✅ Best | Native look, stable, dark theme, full Qt API. Installed via pip. |
| tkinter | ⚠️ Works | Threading issues, dated look on Windows, hard to make modern |
| Electron | ❌ Heavy | ~150MB install, overkill for a chat client |
| Web (HTML+JS+server) | ✅ Good | Reliable via local HTTP server + Chrome. Best for voice (Web Speech API). |

## Key Components

### 1. HermesBridge — subprocess wrapper

```python
import subprocess, threading

def send_to_hermes(text, on_success, on_error):
    def work():
        result = subprocess.run(
            ["hermes", "chat", "-q", text, "-Q"],
            capture_output=True, text=True, timeout=120
        )
        response = (result.stdout or result.stderr or "").strip()
        if response:
            on_success(response)
        else:
            on_error("Empty response")
    threading.Thread(target=work, daemon=True).start()
```

### 2. SessionManager — SQLite persistence

SQLite schema for chat history:

```sql
CREATE TABLE sessions (id TEXT PRIMARY KEY, name TEXT NOT NULL,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL);

CREATE TABLE messages (id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL, role TEXT NOT NULL,
    text TEXT NOT NULL, timestamp TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id));
```

### 3. File Attach

Pass files to Hermes via `-a` flag:

```python
cmd = ["hermes", "chat", "-q", prompt, "-Q"]
for fp in file_paths:
    cmd.extend(["-a", fp])
```

## Dark Theme (Catppuccin Mocha Palette)

- Background: `#1e1e2e`
- Text: `#cdd6f4`
- User accent: `#89b4fa` (blue)
- Hermes accent: `#a6e3a1` (green)
- Error/recording: `#f38ba8` (red)
- Sending: `#fab387` (peach)
- Surface: `#313244`
- Muted: `#585b70`

## Desktop Launch Pattern

```bat
@echo off
title Hermes Terminal
cd /d "C:\path\to\project"
start /B "" "C:\path\to\pythonw.exe" "main.py"
```

```powershell
Start-Process -FilePath "pythonw.exe" -ArgumentList "main.py" -WindowStyle Normal
```

## Related

- `parallel-processing` — queue file integration pattern
- `references/windows-voice-input.md` — voice input approaches
