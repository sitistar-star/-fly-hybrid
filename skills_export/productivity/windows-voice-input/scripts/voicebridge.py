#!/usr/bin/env python3
"""
VoiceBridge — голосовой ввод для Hermes Agent
Пишет распознанный текст в очередь, откуда Hermes его читает.

Запуск: pythonw.exe voicebridge.py
Зависимости: pip install faster-whisper sounddevice keyboard
"""

import tkinter as tk
import threading
import json
import time
from datetime import datetime
from pathlib import Path

try:
    import sounddevice as sd
    import numpy as np
    from faster_whisper import WhisperModel
    HAVE_AUDIO = True
except ImportError as e:
    HAVE_AUDIO = False
    IMPORT_ERROR = str(e)

QUEUE_FILE = Path(__file__).parent / "voice_queue.jsonl"


class SttEngine:
    def __init__(self, model_size="small", device="cpu", language="ru"):
        self.model_size = model_size
        self.device = device
        self.language = language
        self.model = None
        self.ready = False

    def load(self, status_callback=None):
        if self.ready:
            return True
        try:
            if status_callback:
                status_callback("Загрузка whisper...")
            self.model = WhisperModel(self.model_size, device=self.device, compute_type="int8")
            self.ready = True
            if status_callback:
                status_callback("Готов к работе ✓")
            return True
        except Exception as e:
            if status_callback:
                status_callback(f"Ошибка: {e}")
            return False

    def transcribe(self, audio_data, samplerate=16000):
        if not self.ready or self.model is None:
            return None
        segments, info = self.model.transcribe(
            audio_data, beam_size=5,
            language=self.language if self.language else None,
            vad_filter=True
        )
        text = " ".join(seg.text for seg in segments)
        return text.strip() if text else None


class AudioCapture:
    def __init__(self, samplerate=16000, channels=1):
        self.samplerate = samplerate
        self.channels = channels
        self.recording = False
        self.audio_buffer = []
        self.record_thread = None

    def start_recording(self):
        self.recording = True
        self.audio_buffer = []
        self.record_thread = threading.Thread(target=self._record, daemon=True)
        self.record_thread.start()

    def _record(self):
        def callback(indata, frames, time_info, status):
            if self.recording:
                self.audio_buffer.append(indata.copy())
        with sd.InputStream(samplerate=self.samplerate, channels=self.channels, callback=callback):
            while self.recording:
                sd.sleep(100)

    def stop_recording(self):
        self.recording = False
        if self.record_thread:
            self.record_thread.join(timeout=2)
        if not self.audio_buffer:
            return None
        audio = np.concatenate(self.audio_buffer, axis=0)
        return audio.flatten()


def write_to_queue(text):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "text": text,
        "id": f"voice_{int(time.time()*1000)}"
    }
    with open(QUEUE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry["id"]


class VoiceBridgeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("VoiceBridge — голос для Hermes")
        self.root.geometry("600x500")
        self.root.minsize(400, 300)
        self.root.configure(bg="#1e1e2e")
        self.listening = False
        self.stt = SttEngine()
        self.audio = AudioCapture()
        self._build_ui()
        self._init_engine()

    def _build_ui(self):
        BG, FG, ACCENT = "#1e1e2e", "#cdd6f4", "#89b4fa"
        top = tk.Frame(self.root, bg=BG)
        top.pack(fill=tk.X, padx=10, pady=(10, 5))
        tk.Label(top, text="🎙 VoiceBridge", font=("Segoe UI", 14, "bold"),
                 fg=ACCENT, bg=BG).pack(side=tk.LEFT)
        self.status = tk.Label(top, text="⏳ Загрузка...", font=("Segoe UI", 10),
                               fg="#a6adc8", bg=BG)
        self.status.pack(side=tk.RIGHT)

        chat_frame = tk.Frame(self.root, bg=BG)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.chat = tk.Text(chat_frame, wrap=tk.WORD, font=("Consolas", 11),
                            bg="#181825", fg=FG, relief=tk.FLAT, borderwidth=0,
                            padx=10, pady=10, state=tk.DISABLED)
        self.chat.pack(fill=tk.BOTH, expand=True)
        self.chat.tag_config("system", foreground="#f9e2af")
        self.chat.tag_config("user", foreground="#89b4fa", font=("Consolas", 11, "bold"))
        self.chat.tag_config("hermes", foreground="#a6e3a1")

        bottom = tk.Frame(self.root, bg=BG)
        bottom.pack(fill=tk.X, padx=10, pady=(5, 10))
        self.mic_btn = tk.Button(bottom, text="🎤  Говорить",
            font=("Segoe UI", 12, "bold"), bg="#45475a", fg=FG,
            activebackground="#89b4fa", relief=tk.RAISED, borderwidth=2,
            padx=20, pady=8, command=self._toggle)
        self.mic_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.input_var = tk.StringVar()
        entry = tk.Entry(bottom, textvariable=self.input_var, font=("Segoe UI", 11),
                         bg="#313244", fg=FG, relief=tk.FLAT, borderwidth=3)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        entry.bind("<Return>", self._send_text)
        send_btn = tk.Button(bottom, text="➤", font=("Segoe UI", 14), bg=ACCENT,
                             fg="#1e1e2e", relief=tk.RAISED, borderwidth=1, width=3,
                             command=self._send_text)
        send_btn.pack(side=tk.RIGHT)
        self._add("system", "Нажми 🎤 и говори — текст пойдёт в чат с Hermes")

    def _add(self, role, text):
        self.chat.config(state=tk.NORMAL)
        if role == "user":
            self.chat.insert(tk.END, f"\n[{datetime.now():%H:%M:%S}] Вы:\n", "user")
            self.chat.insert(tk.END, f"{text}\n", "user")
        else:
            self.chat.insert(tk.END, f"\n{text}\n", "system")
        self.chat.see(tk.END)
        self.chat.config(state=tk.DISABLED)
        self.root.update()

    def _toggle(self):
        if not HAVE_AUDIO or not self.stt.ready:
            return
        if self.listening:
            self._stop()
        else:
            self._start()

    def _start(self):
        self.listening = True
        self.mic_btn.config(text="⏹  Стоп", bg="#f38ba8", fg="#1e1e2e")
        self.status.config(text="🎤 Слушаю...", fg="#f38ba8")
        self.audio.start_recording()

    def _stop(self):
        self.listening = False
        self.mic_btn.config(text="🎤  Говорить", bg="#45475a", fg="#cdd6f4")
        self.status.config(text="⏳ Распознаю...", fg="#f9e2af")
        audio = self.audio.stop_recording()
        if audio is None or len(audio) < 1000:
            self.status.config(text="✅ Готов", fg="#a6e3a1")
            return

        def process():
            text = self.stt.transcribe(audio)
            if text:
                self.root.after(0, lambda: self._add("user", text))
                self.root.after(0, lambda: write_to_queue(text))
                self.root.after(0, lambda: self.status.config(text="✅ В очереди", fg="#a6e3a1"))
            else:
                self.root.after(0, lambda: self.status.config(text="❌ Не распознано", fg="#f38ba8"))
        threading.Thread(target=process, daemon=True).start()

    def _send_text(self, event=None):
        text = self.input_var.get().strip()
        if text:
            self.input_var.set("")
            self._add("user", text)
            write_to_queue(text)

    def _init_engine(self):
        if not HAVE_AUDIO:
            return
        def load():
            self.stt.load(lambda m: self.status.config(text=m))
        threading.Thread(target=load, daemon=True).start()


def main():
    if QUEUE_FILE.exists():
        QUEUE_FILE.unlink()
    root = tk.Tk()
    VoiceBridgeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
