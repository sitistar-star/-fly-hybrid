---
name: hermes-desktop-client
description: "Build PySide6 desktop chat applications integrated with Hermes Agent. Architecture, threading patterns, session management, file handling, voice input, and AntiGravity setup."
author: Hermes Agent
platforms: [windows, macos, linux]
---

# Hermes Desktop Client

Build a native desktop chat client that communicates with Hermes Agent via subprocess. Based on the `Hermes Terminal` project pattern.

## Architecture

```
┌──────────────────────────────────────────┐
│  PySide6 Desktop App                      │
│  ┌──────────┐  ┌──────────────────────┐  │
│  │ Sidebar  │  │  Chat Area            │  │
│  │ sessions │  │  ┌──────────────────┐ │  │
│  │          │  │  │ MessageBubble    │ │  │
│  │ + Новый  │  │  │ (role + text)    │ │  │
│  └──────────┘  │  └──────────────────┘ │  │
│                │  ┌──────────────────┐ │  │
│  HermesBridge  │  │ MessageBubble... │ │  │
│  (subprocess)  │  └──────────────────┘ │  │
│                │  ┌──────────────────┐ │  │
│  SessionMgmt   │  │ [🎤] [ввод] [📎][➤]│ │  │
│  (SQLite)      │  └──────────────────┘ │  │
└────────────────┴──────────────────────┘  │
└──────────────────────────────────────────┘
```

### Component Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Window | PySide6.QMainWindow | Main application window |
| Chat area | QScrollArea + custom MessageBubble | Message display |
| Sidebar | QListWidget | Session list |
| Input | QTextEdit | Text input with Enter-to-send |
| Voice | sounddevice + faster-whisper | Microphone recording + STT |
| Files | QFileDialog + drag-drop | File attachment |
| Hermes | subprocess.Popen | `hermes chat -q` calls |
| History | SQLite via sqlite3 | Session persistence |

## Project Structure

```
hermes-terminal/
├── main.py              # Entry point, QApplication setup
├── app.py               # QMainWindow, UI layout, signal wiring
├── chat_widget.py       # MessageBubble (QFrame) + ChatWidget (QScrollArea)
├── sidebar.py           # Session list with QListWidget
├── hermes_bridge.py     # HermesBridge — subprocess to hermes chat -q
├── session_manager.py   # SQLite session CRUD
├── stt_engine.py        # faster-whisper wrapper (optional)
├── file_handler.py      # File attachment management
├── requirements.txt     # PySide6, faster-whisper, sounddevice, numpy
├── .vscode/
│   ├── extensions.json  # Python, Pylance recommendations
│   ├── tasks.json       # Run/debug tasks
│   └── mcp.json         # MCP server config for Hermes integration
├── TZ.md                # Technical specification
└── README.md
```

## Critical Patterns

### 1. HermesBridge — subprocess Communication

```python
class HermesBridge:
    def send(self, text, on_success, on_error):
        self._busy = True
        def work():
            try:
                result = subprocess.run(
                    [HERMES_VENV, "-m", "hermes_cli.main", "chat", "-q", text, "-Q"],
                    capture_output=True, text=True, timeout=120,
                    env={**os.environ, "HERMES_HOME": str(HERMES_HOME)}
                )
                response = (result.stdout or result.stderr or "").strip()
                # Strip session_id line from response
                if "\nsession_id:" in response:
                    response = response[:response.index("\nsession_id:")]
                if response: on_success(response)
                else: on_error("Empty response")
            except Exception as e:
                on_error(str(e))
            finally:
                self._busy = False
        threading.Thread(target=work, daemon=True).start()
```

### 2. Thread-Safe UI Updates (PySide6 vs tkinter)

| Framework | Thread update pattern | Reliability |
|-----------|---------------------|-------------|
| **PySide6** ⭐ | `QtCore.Signal` or `QTimer.singleShot(0, lambda)` | Excellent |
| **tkinter** | `root.after(0, lambda)` | Poor — crashes on non-main-thread widget config |

**NEVER use tkinter for a production chat client.** PySide6 (or PyQt6) is required. tkinter's threading model cannot safely handle:
- Background STT model loading → UI status updates
- Subprocess callbacks → chat widget inserts
- File dialog → async message sending

### 3. Session Management (SQLite)

```python
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    text TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

### 4. AntiGravity (VS Code) Integration

In the project's `.vscode/mcp.json`:
```json
{
    "mcp.servers": {
        "hermes-agent": {
            "command": "C:\\Users\\USER\\AppData\\Local\\hermes\\hermes-agent\\venv\\Scripts\\python.exe",
            "args": ["-m", "hermes_cli.main", "mcp", "serve"]
        }
    }
}
```

In user settings (`AppData/Roaming/Antigravity/User/settings.json`):
```json
{
    "mcp.servers": { "hermes-agent": { ... } }
}
```

### 5. Enter-to-Send Event Handling

```python
def eventFilter(self, obj, event):
    if obj == self.input_field and event.type() == event.Type.KeyPress:
        if event.key() == Qt.Key_Return and not (event.modifiers() & Qt.ShiftModifier):
            self._send_message()
            return True
    return super().eventFilter(obj, event)
```

## Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| **Qt widget garbage collection** | `RuntimeError: Signal source has been deleted` | Store ALL QWidget children as `self.*` attributes, not local vars |
| **pythonw silent crash** | App vanishes with no error | Test with `python.exe` first, add file logging |
| **Whisper first-load delay** | App "hangs" for 20-30s | Load in daemon thread, show "loading model" status |
| **OneDrive Desktop path** | Shortcuts not visible | Use `[Environment]::GetFolderPath('Desktop')` via PowerShell |
| **Missing Qt import** | `NameError: name 'Qt' is not defined` | `from PySide6.QtCore import Qt` in main.py |
| **Drag-drop not working** | Files not accepted | `self.setAcceptDrops(True)` on QMainWindow, override `dragEnterEvent` and `dropEvent` |

## User Preferences (captured from session)

- Real desktop app (PySide6), not browser-only
- AntiGravity as the development IDE
- Hotkeys: Ctrl+N new chat, Ctrl+O attach files, Ctrl+Shift+V voice
- Clean desktop — no leftover files or orphaned shortcuts
- Self-healing on stall — auto-restart when agent freezes
- Russian UI language
