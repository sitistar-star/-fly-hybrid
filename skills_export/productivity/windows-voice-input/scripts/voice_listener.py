#!/usr/bin/env python3
"""VoiceBridge queue listener — checks for new voice input.
Call from Hermes: python voice_listener.py → JSON with text or {"found": 0}"""

import json
from pathlib import Path

QUEUE_FILE = Path(__file__).parent / "voice_queue.jsonl"
SEEN_FILE = Path(__file__).parent / ".voice_seen.txt"


def get_new_voice_input():
    if not QUEUE_FILE.exists():
        return []
    seen = set()
    if SEEN_FILE.exists():
        seen = set(line.strip() for line in open(SEEN_FILE, "r"))
    new = []
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                mid = entry.get("id", "")
                if mid not in seen:
                    new.append(entry)
                    seen.add(mid)
            except json.JSONDecodeError:
                continue
    with open(SEEN_FILE, "w") as f:
        for mid in seen:
            f.write(mid + "\n")
    return new


if __name__ == "__main__":
    inputs = get_new_voice_input()
    if inputs:
        latest = inputs[-1]
        print(json.dumps({
            "found": len(inputs),
            "text": latest["text"],
            "id": latest["id"],
        }, ensure_ascii=False))
    else:
        print(json.dumps({"found": 0}))
