---
name: file-delivery
description: Deliver files to the user — generate professional PDFs, choose the right delivery channel, handle Telegram limitations and Google Drive uploads.
version: 1.0.0
author: user
platforms: [windows]
---

# File Delivery

Generate, format, and deliver files to the user through the right channel.

## When to use

The user asks you to:
- Save a file somewhere accessible
- "Скинь" / send a file
- Generate a report/document
- Upload something to Google Drive / Telegram
- Create a PDF

## Delivery channel decision

| File type | Best channel | Method |
|-----------|-------------|--------|
| Image (jpg, png, gif) | Telegram | `MEDIA:<path>` in send_message works |
| PDF document | Telegram via Google Drive or hosting | Google Drive public link (preferred) or temp.sh |
| PDF document | Hosting fallback | Upload to temp.sh, send link |
| Text / Markdown | Telegram direct | Send as plain message (split if long) |
| CSV / XLSX | Google Drive | Upload via rclone, share publicly |

## Rule: MEDIA tag limitation

`MEDIA:<path>` in send_message works for images, video, audio. It does NOT work for PDF documents — the user will see the path as text, not a downloadable file. Always use Google Drive or a file host for PDFs.

## PDF generation from Markdown (Windows)

### Preferred: fpdf2

```python
from fpdf import FPDF

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=18)
pdf.add_page()

# Windows font paths (Cyrillic support)
pdf.add_font("Arial", "", r"C:\Windows\Fonts\arial.ttf")
pdf.add_font("Arial", "B", r"C:\Windows\Fonts\arialbd.ttf")
pdf.set_font("Arial", size=10)
```

### Pitfalls

1. **fpdf2 Unicode errors**: `Not enough horizontal space to render a single character` — caused by emoji, special quotes («»→▶), and other Unicode chars the font can't render. **Fix**: Replace all non-ASCII symbols before passing to multi_cell:
   ```python
   replacements = {'→': '->', '«': '"', '»': '"', '▶': '>',
                   '✅': '[x]', '🟢': '(easy)', '🟡': '(medium)', '🔴': '(hard)',
                   '🧠': '[brain]', '👶': '[toddler]'}
   for old, new in replacements.items():
       text = text.replace(old, new)
   ```

2. **fpdf2 Bold font**: Must be added separately with `pdf.add_font("Arial", "B", path_to_bold_ttf)`. Arial Bold is at `C:\Windows\Fonts\arialbd.ttf`.

3. **weasyprint on Windows**: Requires GTK+ (libgobject-2.0-0) which is NOT installed by default. Installation is complex. Do NOT use weasyprint on Windows — use fpdf2 instead.

4. **Table rows in fpdf2**: Markdown tables rendered as `| cell | cell |` format cause width overflow. Flatten to `cell1 | cell2 | cell3` text with small font.

### Simple text file fallback

If PDF generation is too complex, create a `.txt` version:
```python
import re
text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', md_content)
text = text.replace('**', '').replace('*', '').replace('`', '')
```

## Upload to temp.sh (quick fallback)

```python
import requests
with open(pdf_path, "rb") as f:
    resp = requests.post("https://temp.sh/upload", files={"file": f})
url = resp.text.strip()  # Returns direct download URL
```

## Google Drive upload

### If rclone + OAuth token already configured

```bash
# Upload
/tmp/rclone.exe copy "<local_path>" gdrive: --config /tmp/rclone.conf

# Get shareable link
/tmp/rclone.exe link gdrive:"<filename>" --config /tmp/rclone.conf

# Make public (if drive scope)
# Use Python Google API with token from rclone config
```

### First-time Google Drive setup

1. Install rclone: `pip install rclone`, then download binary from rclone.org
2. Config auto-creates: `/tmp/rclone.exe config create gdrive drive scope drive --config /tmp/rclone-full.conf`
   — **OAuth auto-completes via localhost redirect on Windows (no browser interaction, no user action needed)**.
     rclone starts a local HTTP server on `http://127.0.0.1:53682/`, Google redirects the OAuth flow there, and the token is received immediately. No manual link-opening or code-pasting.
3. Token stored in `C:\\Users\\<user>\\AppData\\Local\\Temp\\rclone-full.conf`
4. Make file public via Google Drive API (see reference)

### Scope: `drive.file` vs `drive`

| Scope | Visibility | Use case |
|-------|-----------|----------|
| `drive.file` | Only files created by this app | Upload-only, user's existing files invisible |
| `drive` | All files on the user's Drive | Full access — can list/search all files |

The user's existing documents, photos, and other files are ONLY visible with `scope drive`. Use `drive.file` when the user only needs uploads; use `drive` when they ask "what files do I have on Drive".

### rclone `link` caveat

`rclone link <file>` returns a URL like `https://drive.google.com/open?id=XXX` even before the file is publicly shared. This URL will only work for the file owner until a public `anyone` permission is added. Always share publicly after upload (see reference).

## References

- `references/google-drive-public-link.md` — making files publicly accessible after rclone upload
- `references/pdf-unicode-replacements.md` — full character replacement table for fpdf2
