# Working Hermes Chat Server Template

Minimal working server that serves a voice-enabled chat UI and bridges to Hermes.

## server.py

```python
import json, os, subprocess, uuid
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "~/AppData/Local/hermes"))
HERMES_VENV = HERMES_HOME / "hermes-agent" / "venv" / "Scripts" / "python.exe"
PORT = 10997
SESSIONS = {}

def call_hermes(text, timeout=120):
    try:
        r = subprocess.run(
            [str(HERMES_VENV), "-m", "hermes_cli.main", "chat", "-q", text, "-Q"],
            capture_output=True, text=True, timeout=timeout,
            env={**os.environ, "HERMES_HOME": str(HERMES_HOME)})
        resp = (r.stdout or r.stderr or "").strip()
        if "\nsession_id:" in resp:
            resp = resp[:resp.index("\nsession_id:")]
        return resp or "✅ Готов"
    except subprocess.TimeoutExpired:
        return "⏰ Таймаут"
    except Exception as e:
        return f"❌ {e}"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(HTML.encode("utf-8"))
    
    def do_POST(self):
        if self.path == "/chat":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            text = data.get("text", "")
            response = call_hermes(text)
            self._json({"response": response})
        elif self.path == "/new":
            sid = str(uuid.uuid4())[:8]
            SESSIONS[sid] = []
            self._json({"session": sid})
    
    def _json(self, d):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(d, ensure_ascii=False).encode())

server = HTTPServer(("127.0.0.1", PORT), Handler)
server.serve_forever()
```

## HTML Skeleton (voice + chat)

```html
<!DOCTYPE html>
<html><head>
<script>
const sr = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
sr.lang = 'ru-RU';
sr.onresult = e => send(e.results[0][0].transcript);
function startMic() { sr.start(); }
async function send(text) {
  let r = await fetch('/chat', {method:'POST', 
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({text})});
  let j = await r.json();
  // display j.response in chat
}
</script>
<style>
/* Minimal calm theme */
:root{--bg:#1a1b2e;--text:#e2ddd6;--accent:#d4a373}
body{background:var(--bg);color:var(--text);font-family:Inter,sans-serif}
</style>
</head><body>
<button onclick="startMic()">🎤</button>
<div id="chat"></div>
</body></html>
```

## Launch (Windows)
```batch
@echo off
cd /d "C:\path\to\project"
start /B "" "C:\path\to\python.exe" server.py
timeout /t 3 >nul
start "" http://127.0.0.1:10997
pause
```

Use `pythonw.exe` instead of `python.exe` for a no-console background server.
