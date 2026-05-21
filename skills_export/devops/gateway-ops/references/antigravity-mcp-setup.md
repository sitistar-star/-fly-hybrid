# MCP Integration with AntiGravity (VS Code fork)

Hermes can integrate with AntiGravity (a Russian VS Code fork, v1.107.0 based on Code OSS) via MCP.

## Option A: Hermes as MCP Server for AntiGravity

Hermes runs as an MCP server that AntiGravity's built-in AI chat can call as a tool provider.

### AntiGravity Side (settings.json)

```json
{
  "mcp.servers": {
    "hermes-agent": {
      "command": "C:\\Users\\<user>\\AppData\\Local\\hermes\\hermes-agent\\venv\\Scripts\\python.exe",
      "args": ["-m", "hermes_cli.main", "mcp", "serve"]
    }
  }
}
```

Path on this system: `%APPDATA%\Antigravity\User\settings.json`

### Via CLI

```bash
antigravity --add-mcp '{"name":"hermes-agent","command":"C:\\...\\python.exe","args":["-m","hermes_cli.main","mcp","serve"]}'
```

Note: `--add-mcp` may only work when AntiGravity is already running with a window open.

## Option B: AntiGravity CLI from Hermes

Hermes can directly invoke AntiGravity's AI chat for coding tasks:

```bash
antigravity chat -m agent -q "Build a FastAPI auth module"
antigravity chat -m ask -q "Explain this error"
antigravity chat -m edit --add-file main.py -q "Add input validation"
```

## Key Facts

- **Executable:** `%LOCALAPPDATA%\Programs\Antigravity\Antigravity.exe`
- **CLI tools:** `%LOCALAPPDATA%\Programs\Antigravity\bin\antigravity.exe` (and .cmd)
- **Config:** `%APPDATA%\Antigravity\User\settings.json`
- **MCP config location:** settings.json under `mcp.servers`
- **Version seen:** 1.107.0
- **Based on:** VS Code / Code OSS (uses Chromium embedded)
- **Has extensions, MCP, Gemini Code Assist**

## Troubleshooting

- `--add-mcp` needs Antigravity running (with a window) to take effect
- For headless config, write directly to settings.json
- AntiGravity stores user data in `%APPDATA%\Antigravity\` (not `%APPDATA%\Code\`)
