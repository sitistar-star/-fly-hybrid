# Gateway Watchdog

Production watchdog that detects stuck gateway agents and auto-restarts.

## Location

- **Script:** `~/AppData/Local/hermes/scripts/gateway-watchdog.py`
- **Cron job:** `gateway-watchdog` (runs every 2 minutes, no_agent=true)
- **Log:** `~/AppData/Local/hermes/logs/gateway-watchdog.log`

## How It Works

1. Reads last 200 lines of `gateway.log`
2. Finds the most recent `inbound message` and `response ready` entries
3. If the latest inbound has NO matching response within 300 seconds → restarts gateway
4. On restart: kills existing `python.exe` gateway processes, then launches a fresh one via `Popen`

## Detection Logic

```
inbound message @ 21:38 →  NO matching "response ready" → 21:43 (5 min later) → RESTART
inbound message @ 21:36 →  "response ready" @ 21:36     →  OK
```

## Edge Cases

- **No inbound messages at all** → healthy (gateway just idle)
- **Multiple restarts in quick succession** → Rely on Windows process launch, not rate-limited
- **Watchdog itself crashes** → cron just logs the error and exits 0 (no auto-restart loop)

## Manual Trigger

```bash
python ~/AppData/Local/hermes/scripts/gateway-watchdog.py
```

## Cron Schedule

```bash
# From hermes CLI:
hermes cron list              # Show jobs
hermes cron run gateway-watchdog    # Trigger now
hermes cron remove <job_id>   # Remove if needed
```
