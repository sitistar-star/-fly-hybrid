# Telegram Gateway Troubleshooting (Windows)

## Common Log Patterns and Fixes

### Pattern: Unauthorized User

**Log:**
```
WARNING gateway.run: Unauthorized user: 358133987 (Oleh) on telegram
```

**Root cause:** `TELEGRAM_ALLOWED_USERS` is empty or commented out in `.env`.

**Fix:**
```env
TELEGRAM_ALLOWED_USERS=358133987
```

**Verification:** After restart, log should show:
```
inbound message: platform=telegram user=Oleh chat=358133987 msg='Привіт'
response ready: platform=telegram chat=358133987 time=8.5s ...
Sending response (29 chars) to 358133987
```

### Pattern: Gateway Connects But Agent Stuck

**Log:**
```
[Telegram] Connected to Telegram (polling mode)
✓ telegram connected
...
inbound message: platform=telegram user=Oleh chat=358133987 msg='2'
...
[no "response ready" for 5+ minutes]
```

**Root cause:** The agent entered a tool-call loop and never produced a final response.
The gateway's message loop is blocked waiting for the current turn to finish.

**Fix:** Restart the gateway (or let watchdog handle it automatically).

### Pattern: Gateway Starts Then Exits (No Process)

**Log:** No entries in `gateway.log`, or only header entries.

**Root cause:** The gateway process crashes before logging. Check `gateway-stdio.log`:
```
cat ~/AppData/Local/hermes/logs/gateway-stdio.log
```

Common causes on Windows:
- Missing `python-telegram-bot` package
- Invalid `TELEGRAM_BOT_TOKEN`
- Network connectivity to api.telegram.org blocked

## Quick Diagnostic Flow

```
Gateway not responding?
│
├─ Check hermes gateway status
│  └─ "No process detected" → Start gateway:
│     ├─ hermes gateway start
│     └─ tail -20 gateway.log
│
├─ Check gateway.log
│  ├─ "Unauthorized user" → Fix TELEGRAM_ALLOWED_USERS
│  ├─ "inbound message" without "response ready" → Stuck → Restart
│  └─ Nothing at all → Startup failure, check stdio log
│
└─ Send test message
   └─ Check log for inbound → response → delivered
```

## Restart Commands

```bash
# Normal
hermes gateway stop && hermes gateway start

# Force kill via Task Scheduler (Windows)
schtasks //End //TN "Hermes_Gateway"
schtasks //Run //TN "Hermes_Gateway"

# Direct Python restart
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Hermes Gateway"
cd ~/AppData/Local/hermes/hermes-agent
HERMES_HOME="~/AppData/Local/hermes" venv/Scripts/python.exe -m hermes_cli.main gateway run
```
