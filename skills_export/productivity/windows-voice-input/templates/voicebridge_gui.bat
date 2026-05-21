@echo off
title VoiceBridge — голос для Hermes
cd /d "C:\Users\sitis\voicebridge"
start /B "" "C:\Users\sitis\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe" "C:\Users\sitis\voicebridge\voicebridge.py"
echo VoiceBridge launched. Speak into the mic, text goes to Hermes.
timeout /t 5
