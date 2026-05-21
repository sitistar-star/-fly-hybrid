#!/usr/bin/env python3
"""Test VoiceBridge — verifies all imports, microphone, and queue work."""

import json, sys
from pathlib import Path

errors = []

try:
    import sounddevice as sd
    print(f"✓ sounddevice {sd.__version__}")
except Exception as e:
    errors.append(f"sounddevice: {e}")

try:
    from faster_whisper import WhisperModel
    print("✓ faster-whisper")
except Exception as e:
    errors.append(f"faster-whisper: {e}")

try:
    import tkinter as tk
    print("✓ tkinter")
except Exception as e:
    errors.append(f"tkinter: {e}")

try:
    import numpy as np
    print("✓ numpy")
except Exception as e:
    errors.append(f"numpy: {e}")

try:
    devices = sd.query_devices()
    inputs = [d for d in devices if d['max_input_channels'] > 0]
    print(f"✓ Микрофонов: {len(inputs)}")
except Exception as e:
    errors.append(f"microphone scan: {e}")

try:
    rec = sd.rec(int(1 * 16000), samplerate=16000, channels=1)
    sd.wait()
    print(f"✓ Запись OK: {len(rec)} samples, max={abs(rec).max():.4f}")
except Exception as e:
    errors.append(f"record: {e}")

# Queue write test
try:
    qf = Path(__file__).parent / "voice_queue.jsonl"
    entry = {"timestamp": "test", "text": "тест", "id": "test"}
    with open(qf, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"✓ Очередь записана")
except Exception as e:
    errors.append(f"queue: {e}")

if errors:
    print(f"\n❌ {len(errors)} errors:")
    for e in errors:
        print(f"  - {e}")
else:
    print("\n✅ All checks passed!")
