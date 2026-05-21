---
name: markdown-to-pdf
description: "Convert Markdown files to professional PDF documents on Windows using fpdf2 + Arial fonts."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [pdf, markdown, document, fpdf2, windows]
related_skills: [google-workspace]
---

# Markdown → PDF Conversion (Windows)

Convert Markdown documents into professional, styled PDF files on Windows using `fpdf2` with native Windows fonts (Arial).

## When to use

- User asks for a PDF version of a Markdown document
- Need to deliver a polished, professional document (not raw markdown)
- Output needs to be shared via Telegram, email, or Google Drive
- Telegram MEDIA tag does NOT support PDF delivery — use file hosting (temp.sh) or Google Drive instead

## Setup

```bash
pip install fpdf2
```

## Windows Fonts

fpdf2 requires explicit TrueType font registration on Windows. Arial works well for Cyrillic + Latin text:

| Font | Path | Style |
|------|------|-------|
| Regular | `C:\Windows\Fonts\arial.ttf` | default |
| Bold | `C:\Windows\Fonts\arialbd.ttf` | Bold |

Alternatives: `C:\Windows\Fonts\segoeui.ttf` (Segoe UI), `C:\Windows\Fonts\times.ttf` (Times New Roman)

## Known pitfalls

### 1. fpdf2's `uni=True` parameter is deprecated since v2.5.1
Remove the `uni=True` kwarg — modern fpdf2 handles Unicode automatically with TTF fonts.

### 0. Telegram MEDIA tag does NOT deliver PDF as downloadable document
`send_message(message="MEDIA:path/to/file.pdf")` sends the PDF path as text, not as a file attachment. The MEDIA tag only works for image/audio/video types on Telegram.
**Fix:** Upload to a file host and share the link, or use Google Drive upload after OAuth setup.

### 2. "Not enough horizontal space to render a single character"
This error fires on Unicode characters the font can't render (emoji, arrows like →, special quotes «»). 
**Fix:** Replace all problematic Unicode with ASCII before passing to fpdf2:
- Emoji (🟢🟡🔴🧠👶🎯💡🏆) → text labels in parentheses
- «»→→▶ → ASCII equivalents (" -> -> >)
- Strip zero-width characters (\u200b-\u206f, \ufeff)

### 3. fpdf2 Bold font requires a separate TTF file
`pdf.set_font("Arial", "B", size)` will fail with `Undefined font` unless you separately register the bold variant:
```python
pdf.add_font("Arial", "", r"C:\Windows\Fonts\arial.ttf")
pdf.add_font("Arial", "B", r"C:\Windows\Fonts\arialbd.ttf")
```

### 4. weasyprint does NOT work on Windows
`weasyprint` depends on GTK/Pango native libraries (`libgobject-2.0-0.dll`) which are not present on standard Windows. Install attempts will fail with `OSError: cannot load library 'libgobject-2.0-0'`. Use fpdf2 instead.

## Recommended workflow

### Step 1: Read and pre-process the Markdown

```python
import re

def clean_text(text):
    """Replace problematic unicode with ASCII equivalents"""
    replacements = {
        '→': '->', '▶': '>', '–': '-', '—': '-',
        '«': '"', '»': '"', '“': '"', '”': '"',
        '✅': '[x]', '➕': '[+]',
        '🟢': '(easy)', '🟡': '(medium)', '🔴': '(hard)',
        '🧠': '[brain]', '👶': '[kid]',
        '🎯': '[goal]', '💡': '[idea]', '🏆': '[trophy]',
        # Add more emoji mappings as needed
    }
    # Strip zero-width characters
    text = re.sub(r'[\u200b\u200c\u200d\u2060\ufeff]', '', text)
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text
```

### Step 2: Build the PDF

```python
from fpdf import FPDF

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=18)
pdf.add_page()
pdf.add_font("Arial", "", r"C:\Windows\Fonts\arial.ttf")
pdf.add_font("Arial", "B", r"C:\Windows\Fonts\arialbd.ttf")

# Process Markdown lines with header detection, tables, lists, blockquotes
# Use try/except around pdf.multi_cell() — single problematic chars still slip through
```

### Step 3: Deliver the PDF

**Telegram:** MEDIA tag does NOT deliver PDFs as downloadable documents. Use:
- **temp.sh** (no auth needed, files live ~1 hour):
  ```bash
  curl -s -F "file=@output.pdf" https://temp.sh/upload
  ```
  Returns a URL like `https://temp.sh/XXXX/output.pdf`

- **Google Drive** via rclone (preferred for permanent storage, ~10s setup):

  **Quick OAuth setup (no Google Cloud Console required, no browser interaction needed):**
  ```bash
  # Install rclone
  pip install rclone

  # Download Windows binary
  curl -L -o rclone.zip "https://downloads.rclone.org/rclone-current-windows-amd64.zip"
  unzip -o rclone.zip "*/rclone.exe"
  # Move to a stable location, e.g. /tmp/rclone.exe

  # Create config — OAuth auto-completes via localhost redirect on Windows
  # rclone starts a local HTTP server on 127.0.0.1:53682 and receives the token directly
  /tmp/rclone.exe config create gdrive drive scope drive.file
  ```

  **Scope note:** `drive.file` shows only files created by this app. Use `scope drive` to see ALL user files.

  **Important rclone config path:** By default `rclone config create` writes to `C:\Users\USER\AppData\Local\Temp\rclone.conf`. This gets wiped on temp cleanup. Either pass `--config <permanent-path>` or save the temp file somewhere stable.

  **Upload a file:**
  ```bash
  rclone copy "path/to/file.pdf" gdrive: --verbose
  ```

  **Make public and get link (via Python + token from rclone config):**
  ```python
  import configparser, json, requests

  config = configparser.ConfigParser()
  config.read(r"C:\Users\USER\AppData\Local\Temp\rclone.conf")
  token = json.loads(config["gdrive"]["token"])

  file_id = "ID_FROM_RCLONE_OUTPUT"  # or upload first, then inspect
  headers = {"Authorization": f"Bearer {token['access_token']}"}

  # Make publicly readable
  requests.post(f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions",
      headers=headers, json={"role": "reader", "type": "anyone"})

  # Get share link
  resp = requests.get(f"https://www.googleapis.com/drive/v3/files/{file_id}?fields=webViewLink",
      headers=headers)
  link = resp.json()["webViewLink"]
  ```

  **Keep the config stable — DEFAULT PATH IS TEMPORARY!**  
  By default `rclone config create` writes to `C:\\Users\\USER\\AppData\\Local\\Temp\\rclone.conf`. This path gets wiped on temp cleanup. **Always save to a permanent path on first create:**
  ```bash
  rclone config create gdrive drive scope drive.file --config "C:\\Users\\USER\\AppData\\Local\\hermes\\rclone.conf"
  ```
  Then every subsequent `rclone` call must pass `--config` pointing to that permanent file. Without it, rclone falls back to the default temp path and the auth is lost.

  **rclone config file location insight:** On Windows, `rclone config file` always returns the actual location used. Run it to confirm where the file landed, then move it to the permanent path if needed.

  **Important:** rclone's `config create` opens a browser on the Windows HOST. This is the user's real browser (Chrome/Edge), NOT the Hermes headless browser — Google login works normally there. If the host is headless (no GUI), rclone supports `--config` manual flow: it prints a URL, the user opens it on any device, authorizes, and pastes the code back.

**Google Drive OAuth via `google-workspace` skill alternative:** The `google-workspace` skill provides a full Gmail/Calendar/Drive/Sheets client, but its OAuth setup requires creating a Google Cloud Console project (app type "Desktop app") and downloading a client_secret JSON. This is necessary for Gmail/Calendar access. For **Drive-only access**, `rclone` is strictly simpler.

## User preference: file delivery to Telegram

This user (Russian-speaking, Windows) expressed a clear preference:
- "мне нужен файл в телеграмме если я прошу или на облаке в гугл драйв" — deliver files as downloadable documents in Telegram OR Google Drive
- MEDIA tag in send_message() does NOT work for PDF — it sends the path as text, not a file
- The PDF should be professional quality (styled, paginated, not raw markdown)

**Delivery checklist:**
1. Create the PDF (professional, 6+ pages if content is long)
2. Upload to temp.sh for immediate access (or Google Drive if configured)
3. Send the link in Telegram — not the MEDIA tag path

## Alternatives that don't work on Windows

| Tool | Why it fails |
|------|-------------|
| weasyprint | Requires GTK native libraries (not available on Windows) |
| pdfkit | Requires wkhtmltopdf binary (may not be installed) |
| pandoc | May work but requires LaTeX engine for PDF output |

## Script template

See `scripts/pdf_from_md.py` for a working reference implementation.
See `references/pdf-professional-touches.md` for page headers, footers, color schemes, and checklist.

Usage:
```bash
python scripts/pdf_from_md.py input.md output.pdf
```
