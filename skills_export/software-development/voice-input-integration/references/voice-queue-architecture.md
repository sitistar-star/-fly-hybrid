# Voice Queue Architecture

How voice input bridges from the browser/app to the current Hermes chat session.

## Data Flow

```
User speaks → VoiceBridge (Web Speech API / whisper) 
  → writes to voice_queue.jsonl  
  → Hermes reads queue, processes, responds in-chat
```

## Queue File Format

`voice_queue.jsonl` — one JSON object per line:

```jsonl
{"timestamp": "2026-05-20T23:05:51", "text": "привет", "id": "voice_1779311151133"}
```

## Integration Points

### From a Python GUI (PySide6 / tkinter)

```python
def write_to_queue(text):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "text": text,
        "id": f"voice_{int(time.time()*1000)}"
    }
    queue_file = Path(__file__).parent / "voice_queue.jsonl"
    with open(queue_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
```

### From a local HTTP server (browser POST)

```python
# Inside do_POST handler
data = json.loads(self.rfile.read(length))
text = data.get("text", "").strip()
with open("voice_queue.jsonl", "a") as f:
    f.write(json.dumps({"text": text, "id": f"voice_{int(time.time()*1000)}", ...}) + "\n")
```

### From Hermes (this chat session) — reading the queue

```python
import json
queue_file = Path("/path/to/voice_queue.jsonl")
seen_file = Path("/path/to/.voice_seen.txt")

# Load seen IDs
seen = set()
if seen_file.exists():
    seen = set(line.strip() for line in open(seen_file))

# Find new entries
new_entries = []
with open(queue_file, "r") as f:
    for line in f:
        entry = json.loads(line.strip())
        if entry.get("id") not in seen:
            new_entries.append(entry)
            seen.add(entry["id"])

# Save seen IDs
with open(seen_file, "w") as f:
    for sid in seen:
        f.write(sid + "\n")

# Process latest
if new_entries:
    text = new_entries[-1]["text"]
    # Respond to this text in-chat
```

## Notes

- `seen_file` prevents re-processing the same voice input after the agent restarts or checks multiple times
- Queue file is append-only — no locking needed for single-writer single-reader
- HTTP server approach is most reliable because Chrome's Web Speech API handles all audio capture and cloud transcription
