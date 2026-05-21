# Hermes Terminal — Web-Based Chat App Architecture

The most reliable architecture for a desktop chat-with-Hermes app on this Windows
setup is a **local Python HTTP server + HTML/JS frontend in Chrome (via WebBridge)**.
Python GUI frameworks (tkinter, PySide6/PyQt6) produce invisible or non-rendering
windows when launched from git-bash (MSYS2). This is a durable constraint of the
runtime environment, not a fixable bug.

## Why Web-Based Works

| Factor | Web App | Python GUI |
|--------|---------|------------|
| Window renders | ✅ Always in Chrome | ❌ Often invisible from git-bash |
| Voice input | ✅ Chrome Speech API (Google STT) | ❌ Needs faster-whisper + sounddevice |
| File upload | ✅ Native `<input type=file>` + drag-drop | ✅ Possible but complex |
| Thread safety | ✅ N/A (stateless HTTP) | ❌ tkinter/PySide require careful thread mgmt |
| Debugging | ✅ DevTools | ❌ No debugger for invisible windows |
| Distribution | ✅ Single `server.py` + open browser | ❌ Needs full Python + Qt installed |

## Architecture

```text
┌─────────────────────────────────────────────┐
│              Chrome (via WebBridge)          │
│  ┌──────────────────────────────────────┐   │
│  │  HTML/JS Chat UI                     │   │
│  │  - Message bubbles                   │   │
│  │  - 🎤 Web Speech API                 │   │
│  │  - 📎 File upload (FormData)         │   │
│  │  - Session sidebar                   │   │
│  └──────────────┬───────────────────────┘   │
│                 │ POST /chat                │
└─────────────────┼───────────────────────────┘
                  │
┌─────────────────┼───────────────────────────┐
│    Python HTTP Server (server.py)           │
│  ┌──────────────┴──────────────────────┐    │
│  │  - Serves HTML/JS at GET /          │    │
│  │  - Accepts POST /chat               │    │
│  │  - Calls hermes chat -q via subproc │    │
│  │  - Stores sessions in memory dict   │    │
│  └─────────────────────────────────────┘    │
│              │ subprocess                    │
│              ▼                               │
│  ┌──────────────────────────┐               │
│  │  Hermes Agent (hermes)   │               │
│  └──────────────────────────┘               │
└─────────────────────────────────────────────┘
```

## File Structure

```text
hermes-terminal/
├── main.py              # Entry point — imports and runs server
├── server.py            # All-in-one: HTTP server + HTML template + handlers
├── TZ.md                # Technical specification
├── requirements.txt     # (minimal — only PySide6 if using, else stdlib-only)
├── sessions.db          # Auto-created SQLite (if using session persistence)
├── .vscode/
│   ├── extensions.json  # Python/Pylance recommendations
│   ├── tasks.json       # Launch tasks
│   └── mcp.json         # MCP server config for AntiGravity AI
└── README.md
```

## Key Implementation Details

### Single-File Server

The entire app is a single `server.py` with:

- A Python `BaseHTTPRequestHandler` subclass
- A raw HTML/JS string constant `HTML_PAGE` (~200 lines)
- `call_hermes()` — subprocess wrapper
- In-memory session dict (no DB dependency)

This keeps deployment trivial: one file, zero pip installs needed beyond the
existing Hermes venv.

### Session Handling

```python
sessions = {}  # In-memory dict, keyed by session ID

# Create: POST /new → returns {session, name}
# Load:  GET /session/<id> → returns {name, messages}
# List:  GET /sessions → returns [{id, name}, ...]
# Chat:  POST /chat with form data (text, session, files)
```

### HTML/JS Frontend

- Uses the **Web Speech API** for voice input (Chrome only)
- Uses **FormData + fetch** for file uploads (no multipart parsing complexity)
- Messages rendered as DOM elements with CSS animations
- Session list updates via AJAX after each send
- Dark theme (Catppuccin Mocha palette)

### File Upload

Files are sent via `FormData` in the POST body. The server uses
`cgi.FieldStorage` to parse multipart form data. For simplicity, the
current version stores sessions in memory; files are read and passed as
context to `hermes chat -q`.

## AntiGravity Integration

The project directory should be opened in AntiGravity for code editing:

```bash
antigravity C:\Users\sitis\projects\hermes-terminal
```

Desktop shortcut: `Hermes Terminal.bat` on Desktop.

### Reopening After Crash

When testing a new version, kill the old Python process on port 10997:

```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 10997 -ErrorAction SilentlyContinue).OwningProcess | Stop-Process -Force
```

Then start fresh.

## Voice Input

This architecture uses **Chrome's Web Speech API** for speech-to-text —
not faster-whisper, not sounddevice. This is intentional:

- Zero local model download (~2GB for whisper)
- Zero Python audio dependencies
- Russian language support is excellent (Google cloud STT)
- Push-to-talk via mouse hold/release
- Works reliably from git-bash because it runs in Chrome, not Python

Python-based STT (faster-whisper + sounddevice) is available via the
`microphone` button path but should only be used when Chrome is
unavailable (e.g., headless/server scenarios).
