# Rclone Google Drive Setup (Alternative to Full OAuth)

When the full Google Workspace OAuth setup (client_secret.json flow) is too heavy, use **rclone** for a minimal, self-contained Google Drive setup. Rclone handles the entire OAuth dance automatically via a local redirect server on port 53682.

## Requirements

- Windows with internet access
- No existing Google Cloud project needed — rclone uses its own pre-registered OAuth client

## Setup

### 1. Download rclone binary

```bash
curl -L -o /tmp/rclone.zip "https://downloads.rclone.org/rclone-current-windows-amd64.zip"
unzip -o /tmp/rclone.zip "*/rclone.exe" -d /tmp/
```

### 2. Create a Drive remote

**Read-only (all files, no write):**
```bash
/tmp/rclone.exe config create gdrive drive scope drive.readonly --config /tmp/rclone.conf
```

**Write access (only files this app creates):**
```bash
/tmp/rclone.exe config create gdrive drive scope drive.file --config /tmp/rclone.conf
```

**Full access (all files, read & write):**
```bash
/tmp/rclone.exe config create gdrive drive scope drive --config /tmp/rclone.conf
```

Rclone will:
1. Open a local HTTP server on `http://127.0.0.1:53682/`
2. Automatically handle the OAuth redirect
3. Save the token to the config file

### 3. Upload a file

```bash
/tmp/rclone.exe copy <local_file> gdrive: --config /tmp/rclone.conf
```

### 4. Make file public & get link

```python
import json, requests, configparser

with open(r"C:\Users\<user>\AppData\Local\Temp\rclone.conf") as f:
    cfg = configparser.ConfigParser()
    cfg.read_string(f.read())
    token = json.loads(cfg["gdrive"]["token"])

headers = {"Authorization": f"Bearer {token['access_token']}"}

# Find file by name
files = requests.get("https://www.googleapis.com/drive/v3/files?q=name='filename.pdf'", headers=headers).json()
file_id = files["files"][0]["id"]

# Make public
requests.post(f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions",
    headers=headers, json={"role": "reader", "type": "anyone"})

# Get public link
info = requests.get(f"https://www.googleapis.com/drive/v3/files/{file_id}?fields=webViewLink", headers=headers).json()
print(info["webViewLink"])
```

### 5. List files

```bash
/tmp/rclone.exe ls gdrive: --config /tmp/rclone.conf
/tmp/rclone.exe tree gdrive: --config /tmp/rclone.conf
```

## Pitfalls

- **Config path on Windows**: Rclone stores config at `C:\Users\<user>\AppData\Local\Temp\rclone.conf` when `--config /tmp/rclone.conf` is used. In MSYS2/bash on Windows, `/tmp` resolves to `C:\Users\<user>\AppData\Local\Temp\`.
- **Scope matters**: `drive.file` only sees files created by this app. Use `drive` for all files or `drive.readonly` for read-only access to everything.
- **Token refresh**: Rclone auto-refreshes tokens. The config file must persist.
- **No rclone CLI in PATH**: The Python pip package `rclone` does NOT install the CLI binary. Always download the binary separately.
- **Large listings may timeout**: Use `--max-depth 2` and specific paths for fast queries.

## Compared to Full Google Workspace OAuth

| Aspect | Rclone method | Full OAuth (google-workspace skill) |
|--------|---------------|--------------------------------------|
| Google Cloud project | Not needed | Required |
| Client secret JSON | Not needed | Required (manual download) |
| OAuth flow | Automatic (local server) | Browser-based code exchange |
| Services | Drive only | Gmail, Calendar, Drive, Sheets, Docs |
| Token storage | Config file | google_token.json |
