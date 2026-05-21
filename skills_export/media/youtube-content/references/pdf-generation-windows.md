# PDF Generation on Windows (fpdf2)

Use when the user wants a polished, shareable PDF deliverable from compiled YouTube research.

## ⚠️ PDF Delivery to Telegram: MEDIA tag does NOT work for PDF

The `send_message` MEDIA tag (`MEDIA:C:\path\to\file.pdf`) does **not** deliver PDFs as native downloadable documents in Telegram. The message goes through but the file does not appear. Use one of these alternatives instead:

### Option A: temp.sh (fast, no auth)
```python
import requests
with open(pdf_path, "rb") as f:
    resp = requests.post("https://temp.sh/upload", files={"file": f}, timeout=30)
link = resp.text.strip()  # e.g. "https://temp.sh/XXXXX/filename.pdf"
send_message(message=f"Download: {link}", target="telegram:...")
```
Links expire after some time but work immediately for download.

### Option B: Google Drive (persistent)
```bash
rclone copy <file> gdrive: --config /path/to/rclone.conf
rclone link gdrive:<file> --config /path/to/rclone.conf
# Then share publicly via Python Google Drive API
```
See the Google Drive skill for full OAuth setup.

## Setup

```bash
pip install fpdf2
```

Windows ships with TrueType fonts in `C:\Windows\Fonts\`. The key pair:

| File | Style |
|------|-------|
| `arial.ttf` | Regular (993 KB) |
| `arialbd.ttf` | Bold (938 KB) |

Both have full Cyrillic + Latin coverage.

## Font Registration (fpdf2 v2.8+)

```python
from fpdf import FPDF

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=18)
pdf.add_page()
pdf.add_font("Arial", "", r"C:\Windows\Fonts\arial.ttf")
pdf.add_font("Arial", "B", r"C:\Windows\Fonts\arialbd.ttf")
pdf.set_font("Arial", size=10)
```

**Important**: Register BOTH regular and bold. omitting bold causes `Undefined font: arialB` errors when calling `set_font("Arial", "B", ...)`.

## Unicode/Cyrillic Handling

fpdf2 with TTF fonts handles Cyrillic, German umlauts, French accents, etc. natively. But emoji characters cause `Not enough horizontal space to render a single character` errors because most TTF fonts don't include emoji glyphs.

### Safe approach: replace emoji with text labels

```python
import re

def clean_text(text):
    replacements = {
        '→': '->', '▶': '>', '–': '-', '—': '-',
        '«': '"', '»': '"', '“': '"', '”': '"',
        '✅': '[x]', '➕': '[+]',
        '🟢': '(easy)', '🟡': '(medium)', '🔴': '(hard)',
        '🧠': '[brain]', '👶': '[toddler]',
        '🚀': '[go]', '🔥': '[fire]',
        '💡': '[idea]', '🏆': '[trophy]',
        # Add more as encountered
    }
    # Remove zero-width chars
    text = re.sub(r'[\u200b\u200c\u200d\u2060\ufeff]', '', text)
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text
```

Also strip markdown syntax before PDF rendering:
```python
text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # [text](url) -> text
text = text.replace('**', '').replace('*', '').replace('`', '')
```

## Text Rendering Helper

Wrap `multi_cell` in a try/except as a safety net — problematic characters (rare emoji, control chars) that slip through cleaning will crash otherwise:

```python
def write_line(pdf, text, style='', size=10, indent=0, spacing=5):
    if not text:
        pdf.ln(spacing)
        return
    pdf.set_font("Arial", style, size)
    pdf.set_x(10 + indent)
    try:
        pdf.multi_cell(pdf.w - 20 - indent, spacing, text, new_x="LMARGIN")
    except:
        # Last resort: truncate to first 200 safe chars
        safe = ''.join(c for c in text if ord(c) < 128 or 0x400 <= ord(c) <= 0x52F)
        try:
            pdf.multi_cell(pdf.w - 20 - indent, spacing, safe[:200], new_x="LMARGIN")
        except:
            pass
```

## Professional Styling Techniques

| Effect | Code |
|--------|------|
| Section header (h1) | `pdf.set_font("Arial", "B", 16)` then draw horizontal rule with `pdf.line(10, y, pdf.w-10, y)` |
| Sub-header (h2) | `pdf.set_font("Arial", "B", 13)` + thinner rule |
| Sub-sub (h3) | `pdf.set_font("Arial", "B", 11)` no rule |
| Table header visual | Use **bold for first row**, alternating row bg via `pdf.set_fill_color(248, 249, 250)` |
| Page numbers | Configure via `@page` CSS in weasyprint, or manually with `pdf.footer()` override (fpdf2) |
| Table of contents | Write manually as numbered items after h1 |

## Line Height Reference

| Font size | `multi_cell` line height |
|-----------|-------------------------|
| 8 pt | 4 mm |
| 9 pt | 5 mm |
| 10 pt | 5-6 mm |
| 11 pt | 6 mm |
| 13 pt | 7 mm |
| 16 pt | 8 mm |

## Pitfalls

1. **Don't pass `uni=True`** to `add_font()` in fpdf2 v2.5.1+ — it's deprecated and the parameter is ignored anyway; TTF fonts are always Unicode.
2. **Table separator rows** (`|---:|:---|---|`) must be skipped explicitly — fpdf2 doesn't understand markdown tables and will try to render literal `---` chars.
3. **Emoji in source text** will crash `multi_cell` silently (or with the horizontal-space error). Always run `clean_text()` before writing.
4. **Bold font must be registered separately** — `pdf.add_font("Arial", "", ...)` and `pdf.add_font("Arial", "B", ...)`. Missing bold = `Undefined font` error.
5. **`execute_code` and terminal are separate runtimes** — install fpdf2 in one, but if you switch to the other, reinstall.
