# Auto-Restart Watchdog Pattern

When a background service (gateway, chat server, etc.) gets stuck processing a message, auto-restart it.

## Cron-based watchdog

```python
# watchodg.py — check if gateway processed last message within timeout
import subprocess, json
from pathlib import Path
from datetime import datetime

LOG = Path("~/AppData/Local/hermes/logs/gateway.log")
TIMEOUT = 300  # 5 minutes

def check():
    lines = LOG.read_text().splitlines()[-100:]
    last_inbound = last_response = None
    for line in lines:
        if "inbound message:" in line: last_inbound = parse_ts(line)
        if "response ready:" in line: last_response = parse_ts(line)
    
    if last_inbound and (not last_response or last_response < last_inbound):
        elapsed = (datetime.now() - last_inbound).total_seconds()
        if elapsed > TIMEOUT:
            restart_gateway()

def restart_gateway():
    subprocess.run(["taskkill", "/F", "/IM", "python.exe"])  # careful!
    subprocess.Popen([...])  # restart command
```

## Cron job
```bash
hermes cron create --name gateway-watchdog --schedule "every 2m" --script gateway-watchdog.py --no-agent
```

## Key parameters
- Check interval: 2 minutes
- Stuck timeout: 5 minutes
- Script type: `no_agent=True` (no LLM, just runs the script)
