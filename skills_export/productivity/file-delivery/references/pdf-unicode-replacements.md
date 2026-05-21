# fpdf2 Unicode character replacement table

## Problem

fpdf2 with Arial/standard Windows fonts raises `Not enough horizontal space to render a single character` for characters not supported by the font (emoji, special quotes, arrows, etc.).

## Full replacement table

Use this in your cleaning function before passing text to `pdf.multi_cell()`:

```python
import re

def clean_text(text):
    """Replace problematic unicode with ASCII equivalents for fpdf2"""
    replacements = {
        # Arrows
        '→': '->', '⇒': '=>', '→ ': '-> ',
        '←': '<-', '⇐': '<=',
        '↔': '<->', '↕': '|',
        '⇒': '=>', '⇔': '<=>',
        
        # Play/action symbols
        '▶': '>', '▶': '>', '▸': '>',
        '▪': '-', '▫': '-', '▬': '-',
        '●': '*', '○': '*', '◌': '-',
        '◆': '*', '◇': '*',
        
        # Bullets and dashes
        '•': '-', '·': '-',
        '–': '-', '—': '-', '―': '-',
        
        # Quotes
        '«': '"', '»': '"',
        '“': '"', '”': '"', '„': '"',
        '‘': "'", '’': "'", '‚': "'",
        '‹': '<', '›': '>',
        
        # Check marks
        '✅': '[x]', '✔': '[x]', '☑': '[x]',
        '❌': '[!]', '✖': '[!]',
        '➕': '[+]', '➖': '[-]',
        
        # Rating indicators (colored circles common in self-help content)
        '🟢': '(легко)',
        '🟡': '(средне)',
        '🔴': '(сложно)',
        
        # Common emoji in self-help / productivity content
        '🧠': '[мозг]',
        '👶': '[малыш]',
        '🎯': '[цель]',
        '💡': '[идея]',
        '🏆': '[трофей]',
        '🚀': '[вперёд]',
        '🔥': '[огонь]',
        '💫': '[сияние]',
        '📄': '[файл]',
        '📅': '[дата]',
        '📺': '[видео]',
        '📑': '[раздел]',
        '📍': '[маркер]',
        'ℹ️': '[инфо]',
        '⭐': '*', '🌟': '*',
        '✨': '*',
        '❓': '[?]', '❗': '[!]',
        '💪': '[сила]',
        '👍': '[ok]',
        '👎': '[no]',
        '🙏': '[спасибо]',
        '😊': ':)', '😁': ':D',
        
        # Stars and decorative
        '★': '*', '☆': '*',
        '✦': '*', '✧': '*',
        '☀': '*', '☁': '~',
        '♪': '#', '♫': '#',
        '♻': '[recycle]',
        
        # Zero-width characters (invisible but cause issues)
        '\u200b': '',  # ZERO WIDTH SPACE
        '\u200c': '',  # ZERO WIDTH NON-JOINER
        '\u200d': '',  # ZERO WIDTH JOINER
        '\u2060': '',  # WORD JOINER
        '\ufeff': '',  # BOM
    }
    
    # Remove zero-width characters first
    text = re.sub(r'[\u200b\u200c\u200d\u2060\ufeff]', '', text)
    
    # Replace mapped characters
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Remove any remaining emoji (broad catch)
    # Matches most emoji ranges
    text = re.sub(r'[\U0001F300-\U0001FAFF]', '', text)
    text = re.sub(r'[\U0001F600-\U0001F64F]', '', text)
    text = re.sub(r'[\U0001F680-\U0001F6FF]', '', text)
    text = re.sub(r'[\U0001F900-\U0001F9FF]', '', text)
    text = re.sub(r'[\u2600-\u26FF]', '', text)  # Misc symbols
    text = re.sub(r'[\u2700-\u27BF]', '', text)  # Dingbats
    
    return text
```

## Also clean markdown formatting

```python
def clean_md_line(line):
    text = clean_text(line)
    # Remove markdown links: keep visible text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove images
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', text)
    # Remove code backticks
    text = text.replace('`', '')
    # Remove bold/italic markers that remain after markdown conversion
    text = text.replace('**', '').replace('*', '')
    return text.strip()
```
