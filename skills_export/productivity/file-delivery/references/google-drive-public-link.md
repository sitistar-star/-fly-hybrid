# Making Google Drive files publicly accessible after rclone upload

## 1. Read rclone token

Token is stored in the config file, e.g. `C:\Users\sitis\AppData\Local\Temp\rclone-full.conf`.

Parse it with Python configparser:

```python
import configparser, json
config = configparser.ConfigParser()
config.read(r"C:\Users\sitis\AppData\Local\Temp\rclone-full.conf")
token = json.loads(config["gdrive-full"]["token"])
access_token = token["access_token"]
```

## 2. Get file ID

```python
import requests
headers = {"Authorization": f"Bearer {access_token}"}
# Search for file by name
resp = requests.get(
    "https://www.googleapis.com/drive/v3/files?q=name='filename.pdf'",
    headers=headers
)
file_id = resp.json()["files"][0]["id"]
```

Or get the ID from rclone link output:
```
https://drive.google.com/open?id=FILE_ID_HERE
```

## 3. Share publicly

```python
perm = {"role": "reader", "type": "anyone"}
resp = requests.post(
    f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions",
    headers=headers,
    json=perm
)
```

## 4. Get public links

```python
resp = requests.get(
    f"https://www.googleapis.com/drive/v3/files/{file_id}?fields=webViewLink,id",
    headers=headers
)
data = resp.json()
view_link = data["webViewLink"]
direct_download = f"https://drive.google.com/uc?export=download&id={file_id}"
```

## Important notes

- Scope `drive.file` allows the app to see only files it created
- Scope `drive` allows full access to all user files
- The rclone OAuth flow auto-completes on Windows via localhost redirect — **no manual browser interaction needed, no link to open, no code to paste**
- The token auto-refreshes; no need to re-authorize
- **`rclone link <file>`** returns a URL (`https://drive.google.com/open?id=XXX`) even BEFORE you make the file public. The URL only works for the file owner until you add an `anyone` permission. Always call the permissions API before sharing the link.
- **Large Drives:** `rclone tree` may time out (>30s). Use `rclone ls` or `rclone lsl` instead.
