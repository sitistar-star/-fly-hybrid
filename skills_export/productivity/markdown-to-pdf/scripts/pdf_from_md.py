#!/usr/bin/env python3
"""
markdown-to-pdf: Convert Markdown to professional PDF on Windows.

Usage:
    python pdf_from_md.py input.md [output.pdf]

Requires:
    pip install fpdf2

Uses Arial from C:\\Windows\\Fonts (Regular + Bold).
Automatically handles Unicode → ASCII replacements for emoji/special chars.
"""

import os
import re
import sys
from fpdf import FPDF


# ── Unicode cleanup ──────────────────────────────────────────────────────────

EMOJI_MAP = {
    '→': '->', '▶': '>', '▪': '-', '•': '-', '–': '-', '—': '-',
    '«': '"', '»': '"', '“': '"', '”': '"', '‘': "'", '’': "'",
    '✅': '[ok]', '➕': '[+]',
    '🟢': '(легко)', '🟡': '(средне)', '🔴': '(сложно)',
    '🧠': '[мозг]', '👶': '[малыш]', '🎯': '[цель]',
    '💡': '[идея]', '🏆': '[трофей]', '🚀': '[вперёд]',
    '🔥': '[огонь]', '📄': '[файл]', '📅': '[дата]',
    '📺': '[видео]', '📑': '[содерж]',
}

FONT_REGULAR = r"C:\Windows\Fonts\arial.ttf"
FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
FONT_FALLBACK = [
    r"C:\Windows\Fonts\segoeui.ttf",
    r"C:\Windows\Fonts\Calibri.ttf",
    r"C:\Windows\Fonts\times.ttf",
]


def clean_text(text: str) -> str:
    """Replace problematic unicode with ASCII equivalents for PDF rendering."""
    text = re.sub(r'[\u200b\u200c\u200d\u2060\ufeff]', '', text)
    for old, new in EMOJI_MAP.items():
        text = text.replace(old, new)
    return text


def clean_md_line(line: str) -> str:
    """Strip markdown formatting from a single line."""
    text = clean_text(line)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # links → text
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', text)  # images → alt
    text = text.replace('`', '').replace('**', '').replace('*', '')
    return text.strip()


def find_fonts():
    """Find the best available TrueType fonts for Regular and Bold."""
    regular = FONT_REGULAR if os.path.exists(FONT_REGULAR) else None
    bold = FONT_BOLD if os.path.exists(FONT_BOLD) else None
    for f in FONT_FALLBACK:
        if os.path.exists(f):
            if not regular:
                regular = f
            if not bold:
                bold = f
            break
    return regular, bold


def md_to_pdf(md_path: str, pdf_path: str):
    """Convert a Markdown file to a styled PDF."""
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    font_reg, font_bold = find_fonts()
    if not font_reg:
        raise FileNotFoundError("No suitable TrueType font found in C:\\Windows\\Fonts")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.add_font("F", "", font_reg)
    pdf.set_font("F", size=10)
    if font_bold:
        pdf.add_font("F", "B", font_bold)

    def write(text, style='', size=10, indent=0, spacing=5):
        if not text:
            pdf.ln(spacing)
            return
        pdf.set_font("F", style, size)
        pdf.set_x(10 + indent)
        try:
            pdf.multi_cell(pdf.w - 20 - indent, spacing, text, new_x="LMARGIN")
        except Exception:
            # Last resort: truncate to first 100 chars
            try:
                pdf.set_font("F", style, size - 1)
                pdf.multi_cell(pdf.w - 20 - indent, spacing, text[:100], new_x="LMARGIN")
            except Exception:
                pass

    i = 0
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()

        if stripped == '':
            pdf.ln(2)
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^[-*]{3,}$', stripped):
            y = pdf.get_y()
            pdf.set_draw_color(180, 180, 180)
            pdf.line(10, y, pdf.w - 10, y)
            pdf.ln(4)
            i += 1
            continue

        # Table separator
        if re.match(r'^[\|\s:-]+$', stripped) and '---' in stripped:
            i += 1
            continue

        # h1
        if stripped.startswith('# ') and not stripped.startswith('## '):
            text = clean_md_line(stripped[2:])
            pdf.ln(4)
            write(text.upper(), 'B', 16, 0, 7)
            y = pdf.get_y()
            pdf.set_draw_color(26, 58, 92)
            pdf.line(10, y, pdf.w - 10, y)
            pdf.ln(4)
            i += 1
            continue

        # h2
        if stripped.startswith('## ') and not stripped.startswith('### '):
            text = clean_md_line(stripped[3:])
            pdf.ln(3)
            write(text, 'B', 13, 0, 6)
            y = pdf.get_y()
            pdf.set_draw_color(43, 87, 151)
            pdf.line(10, y, pdf.w - 10, y)
            pdf.ln(3)
            i += 1
            continue

        # h3
        if stripped.startswith('### '):
            text = clean_md_line(stripped[4:])
            pdf.ln(2)
            write(text, 'B', 11, 0, 5)
            i += 1
            continue

        # Table row
        if stripped.startswith('|') and stripped.endswith('|'):
            cells = [c.strip() for c in stripped.split('|') if c.strip()]
            if cells:
                text = ' | '.join(cells)
                write(clean_md_line(text), '', 8, 0, 4)
            i += 1
            continue

        # Blockquote
        if stripped.startswith('>'):
            text = clean_md_line(stripped.lstrip('> '))
            pdf.set_fill_color(240, 244, 248)
            write(text, '', 9, 6, 5)
            i += 1
            continue

        # Bullet
        if stripped.startswith('- ') or stripped.startswith('* '):
            text = clean_md_line(stripped[2:])
            write('- ' + text, '', 10, 5, 5)
            i += 1
            continue

        # Numbered list
        if re.match(r'^\d+[.)]\s', stripped):
            write(clean_md_line(stripped), '', 10, 5, 5)
            i += 1
            continue

        # Regular paragraph
        text = clean_md_line(stripped)
        if text:
            write(text, '', 10, 0, 5)
        i += 1

    pdf.output(pdf_path)
    return pdf.pages_count


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    md_path = sys.argv[1]
    pdf_path = sys.argv[2] if len(sys.argv) > 2 else md_path.rsplit('.', 1)[0] + '.pdf'
    if not os.path.exists(md_path):
        print(f"Error: file not found: {md_path}")
        sys.exit(1)
    pages = md_to_pdf(md_path, pdf_path)
    size = os.path.getsize(pdf_path) / 1024
    print(f"PDF saved: {pdf_path} ({size:.0f} KB, {pages} pages)")
