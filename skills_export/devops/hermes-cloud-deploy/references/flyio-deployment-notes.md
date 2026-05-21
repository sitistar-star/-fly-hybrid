# Fly.io Deployment Notes (Session 2026-05-21)

## App Details
- **App name:** hermes-agent-cloud
- **Region:** ams (Amsterdam)
- **VM:** shared-cpu-1x, 512MB, 1 machine
- **URL:** https://hermes-agent-cloud.fly.dev/
- **API:** OpenAI-compatible on port 8642

## Secrets Set
```
GOOGLE_API_KEY=AIzaSyDRqNjTG05fZ5fg3tFFsksQBBQjONu_jsZ4
TELEGRAM_BOT_TOKEN=8573027399:AAGrsT6dH1M80jlkjn7-biAVsK1zfZArBN4
TELEGRAM_ALLOWED_USERS=358133987
TELEGRAM_HOME_CHANNEL=Alex
API_SERVER_ENABLED=true
API_SERVER_KEY=hermes-cloud-secret-key-2026-change-me  # CHANGE TO RANDOM
API_SERVER_HOST=0.0.0.0
FELO_API_KEY=fk-J04cJYBydeHnx0pkrQ4ke13kXDlwGZTYfc1rxQpW0hwT4RbU
```

## Telegram Bot Info
- **Bot ID:** 8573027399
- **Username:** @Aleksgipnobot
- **Name:** AlexOsteo
- **Token:** 8573027399:AAGrsT6dH1M80jlkjn7-biAVsK1zfZArBN4

## Known Issues

### Telegram Polling Conflict
Both local (Scheduled Task) and cloud Fly.io instance poll the same bot. Error: `Conflict: terminated by other getUpdates request`. Fix: either stop local gateway, create new bot for cloud, or use webhook mode.

### No Credit Card on Fly.io
Trial machines stop after 5 minutes. Need to add card at https://fly.io for persistent 24/7 operation.

## Commands Reference

```bash
# Manage machines
fly machine destroy <id> --app hermes-agent-cloud
fly machine start <id> --app hermes-agent-cloud
fly status --app hermes-agent-cloud

# Logs
fly logs --app hermes-agent-cloud

# Secrets (stage, then deploy)
fly secrets set KEY=VAL --stage

# Deploy with new build
fly deploy --no-cache --remote-only

# Scale
fly scale count app=1  # reduce to 1 machine
```

## Files Created
- `~/fly-hybrid/Dockerfile`
- `~/fly-hybrid/fly.toml`
- `~/fly-hybrid/config.yaml`
