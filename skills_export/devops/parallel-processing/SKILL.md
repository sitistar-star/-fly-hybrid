---
name: parallel-processing
description: Run multiple Hermes agents and tasks in parallel — background processes, delegate_task, queue files, multi-session orchestration.
version: 1.0.0
author: Agent (derived from session)
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [parallel, background, multi-agent, orchestration, queue, delegate]
    related_skills: [gateway-ops, hermes-agent]
---

# Parallel Processing (parallel-processing)

Run Hermes agents and tasks in parallel — background subprocesses, queued messaging,
cross-process queue files, and multi-terminal orchestration.

## Why This Exists

Hermes processes one user message at a time in a single session. When the user wants
to work on something while you're busy, or run multiple tasks simultaneously, you need
parallel processing patterns.

---

## Patterns

### Pattern 1: delegate_task (synchronous subagent)

Built into Hermes — spawns a child agent with isolated context and tools.
Runs inside the parent turn (synchronous). Best for:

- Reasoning-heavy subtasks (debugging, research)
- Tasks that would flood your context with intermediate data
- Parallel independent workstreams (up to 3 concurrent children)

```python
delegate_task(goal="...", context="...", toolsets=["terminal", "file"])
# Batch mode:
delegate_task(tasks=[{goal: "task1"}, {goal: "task2"}])
```

**Limitation:** If the parent is interrupted (user sends /new, /stop), children are cancelled.
Not durable. For durable work, use cron or background terminal processes.

### Pattern 2: Background terminal process (durable)

Hermes process spawned with `terminal(background=True, notify_on_complete=True)`.
Runs independently — if the parent session ends, the child continues.

**Best for:** Long-running tasks, installs, builds, scrapes.

```python
# Start
terminal(command="hermes chat -q '...' -Q", background=True, notify_on_complete=True)

# Check status
process(action="poll", session_id="...")
```

**Warning:** Do NOT use `shell=True` backgrounding (`&`, `nohup`) in foreground
terminal calls. Use `background=True` on the tool call itself.

### Pattern 3: Queue file (async cross-process)

VoiceBridge-to-Hermes pattern: one process writes JSONL entries to a shared
file, the other reads them. Works across any two processes that share a filesystem.

```jsonl
{"timestamp": "...", "text": "hello", "id": "voice_12345"}
```

**Reader pattern** (Python):
```python
with open("queue.jsonl") as f:
    for line in f:
        entry = json.loads(line)
        if entry["id"] not in seen:
            process(entry["text"])
            seen.add(entry["id"])
```

### Pattern 4: Multiple terminal windows

Open separate terminal windows and run `hermes` in each. Each is fully independent.
The user can chat in one while the other does background work.

Also works across different platforms — Telegram, CLI, and Discord are all
independent sessions.

### Pattern 5: Cron jobs (scheduled)

For recurring tasks (daily digests, monitoring, data collection).
Durable — survive reboots.

```bash
hermes cron create "every 2h" --name "check-prices" --prompt "check prices"
```

See `hermes-agent` skill for full cron reference.

---

## Queue File Pattern (Detailed)

This is the most flexible cross-process pattern, demonstrated with VoiceBridge.

### Writer (separate process)

```python
import json, time
from pathlib import Path

QUEUE = Path("/path/to/queue.jsonl")

def enqueue(text, source="voice"):
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "text": text,
        "id": f"{source}_{int(time.time()*1000)}"
    }
    with open(QUEUE, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
```

### Reader (Hermes agent)

Use `execute_code` or `voice_listener.py` to poll:

```python
from pathlib import Path
import json

queue = Path("/path/to/queue.jsonl")
seen_file = Path("/path/to/.seen.txt")

seen = set()
if seen_file.exists():
    seen = set(l.strip() for l in open(seen_file))

new = []
for line in open(queue):
    entry = json.loads(line)
    if entry["id"] not in seen:
        new.append(entry)
        seen.add(entry["id"])

open(seen_file, "w").writelines(id + "\n" for id in seen)

if new:
    latest = new[-1]
    print(json.dumps({"text": latest["text"]}))
else:
    print("NO_INPUT")
```

---

## Windows-Specific Quirks

### pythonw.exe for GUI apps

On Windows, `pythonw.exe` (not `python.exe`) launches GUI apps without a console
window. Always use pythonw.exe for tkinter/PyQt apps:

```bash
# Correct — no console window
pythonw.exe my_gui_app.py

# Wrong — opens an extra console + GUI window
python.exe my_gui_app.py
```

### Desktop Path (OneDrive)

On Windows with OneDrive sync, `[Environment]::GetFolderPath('Desktop')` returns
`C:\Users\<user>\OneDrive\Desktop`, NOT `C:\Users\<user>\Desktop`.
Always use PowerShell to resolve the Desktop path:

```powershell
$desktop = [Environment]::GetFolderPath('Desktop')
```

In bash, do NOT hardcode `~/Desktop` or `C:\Users\user\Desktop` — use PowerShell.

### Pythonw + Start-Process for GUIs

To launch a GUI app from a terminal session (e.g., git-bash) so it stays alive
independently:

```powershell
powershell.exe -Command "Start-Process -FilePath 'pythonw.exe' -ArgumentList 'app.py' -WindowStyle Normal"
```

---

## Related

- `gateway-ops` — Gateway health monitoring and auto-restart watchdog
- `hermes-agent` — CLI reference for cron, delegate_task, sessions
- `references/hermes-desktop-client.md` — Building custom desktop Hermes clients (PySide6, HTML, SQLite sessions, file attach)
