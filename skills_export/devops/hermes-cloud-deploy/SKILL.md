---
name: hermes-cloud-deploy
description: Deploy Hermes Agent as a 24/7 cloud service on platforms like Fly.io, Railway, or any Docker host — API server, Telegram gateway, and hybrid local/cloud setups.
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos, windows]
---

# Hermes Cloud Deploy

Deploy Hermes Agent as a persistent cloud service with API server (OpenAI-compatible endpoints) and/or Telegram gateway.

## When to Use

- User wants Hermes running 24/7 in the cloud (not just on their local machine)
- Need an OpenAI-compatible API endpoint for external tools (Open WebUI, etc.)
- Hybrid setup: local Hermes for CLI, cloud Hermes for always-on Telegram/API access

## Architecture

```
┌──────────────────┐     ┌──────────────────┐
│  Local Hermes    │     │  Cloud Hermes    │
│  (CLI + possibly │     │  (24/7 on Fly.io)│
│   Telegram)      │     │                  │
│                  │     │  • API Server    │
│                  │     │    :8642         │
│                  │     │  • Telegram GW   │
│                  │     │  • Cron jobs   │
└──────────────────┘     └──────────────────┘
```

## Prerequisites

- Fly.io account (or similar Docker host)
- `flyctl` installed on the deploying machine
- Hermes Agent installed locally (for config reference)

### Install flyctl

```bash
# macOS/Linux
curl -fsSL https://fly.io/install.sh | sh

# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex
```

### Authenticate

```bash
fly auth login                          # browser-based
# or use token:
export FLY_ACCESS_TOKEN="FlyV1 ..."     # from Fly.io API tokens page
fly auth whoami                         # verify
```

## Dockerfile

Create a `Dockerfile` in your project directory:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# hermes-agent + aiohttp (required for API server platform)
RUN pip install -U pip && pip install hermes-agent aiohttp

# Config directory
RUN mkdir -p /root/.hermes

# Copy pre-made config
COPY config.yaml /root/.hermes/config.yaml

EXPOSE 8642

CMD ["hermes", "gateway", "run"]
```

## Config (config.yaml)

Minimal config for cloud instance:

```yaml
model:
  default: google/gemini-2.0-flash      # or any model
  provider: google                       # or openrouter, nous, etc.
terminal:
  backend: local
  timeout: 180
display:
  compact: true
approvals:
  mode: off                              # no approval prompts in headless mode
platforms:
  api_server:
    enabled: true
    extra:
      host: "0.0.0.0"
      port: 8642
```

## fly.toml

```toml
app = "your-app-name"
primary_region = "ams"                   # choose nearest region

[build]
  dockerfile = "Dockerfile"

[http_service]
  internal_port = 8642
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512

[env]
  API_SERVER_HOST = "0.0.0.0"
  HERMES_HOME = "/root/.hermes"
```

## Secrets

Set sensitive values via `fly secrets set` (never bake into the image):

```bash
fly secrets set \
  GOOGLE_API_KEY="..." \
  TELEGRAM_BOT_TOKEN="..." \
  TELEGRAM_ALLOWED_USERS="12345" \
  API_SERVER_ENABLED="true" \
  API_SERVER_KEY="$(openssl rand -hex 32)" \
  --stage
```

**Critical:** `API_SERVER_KEY` is REQUIRED when `API_SERVER_HOST=0.0.0.0`. The API server refuses to bind to a network-accessible address without it.

### Extracting secrets from local .env

On Windows/git-bash, use `od -c` or `xxd` to read raw token values without redaction:

```bash
sed -n '478p' ~/.hermes/.env | cut -d= -f2 | xxd
```

## Deploy

```bash
fly deploy --no-cache --remote-only
```

The first deploy creates the app and provisions IP addresses:
- Dedicated IPv6
- Shared IPv4 (add dedicated with `fly ips allocate-v4`)

## Platform Activation

The API server platform is activated by EITHER:
1. `platforms.api_server.enabled: true` in config.yaml (with extra.host/port)
2. `API_SERVER_ENABLED=true` env var
3. `API_SERVER_KEY` being set (auto-enables)

The Telegram platform is activated by `TELEGRAM_BOT_TOKEN` env var.

## Telegram Polling Conflict

If both local and cloud Hermes instances use the **same** Telegram bot token, they'll conflict: `terminated by other getUpdates request`.

Solutions:
- **Separate bots:** Create a new bot via @BotFather for the cloud instance
- **Webhook mode:** Use `TELEGRAM_WEBHOOK_URL` on cloud, polling on local
- **One instance only:** Stop the local Telegram gateway, let cloud handle it

## Costs (Fly.io, 2026)

| Size | Price/month |
|------|------------|
| shared-cpu-1x, 256MB | $1.94 |
| shared-cpu-1x, 512MB | $3.19 |
| shared-cpu-1x, 1GB | $5.70 |

Free tier: $5 welcome credit. Trial machines stop after 5 min without a credit card.

## Troubleshooting

### "No adapter available for api_server"
Cause: `aiohttp` not installed. Add to `pip install` in Dockerfile.

### "The app is not listening on the expected address"
Cause: API server didn't start. Check logs for `aiohttp` or `API_SERVER_KEY` errors.

### Telegram token rejected despite being valid
Check:
- Token stored correctly via `fly secrets set` (no stray whitespace/newlines)
- Fly machine can reach `api.telegram.org` (should work)
- Not being rate-limited by Telegram

## References

See `references/flyio-deployment-notes.md` for session-specific deployment details and quirks.
