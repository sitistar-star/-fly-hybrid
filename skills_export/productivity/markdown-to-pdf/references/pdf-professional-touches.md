# Professional PDF touches with fpdf2

## Page headers and footers

Add page numbers and running headers by overriding FPDF's `header()` and `footer()` methods:

```python
from fpdf import FPDF

class MyPDF(FPDF):
    def header(self):
        if self.page_no() > 1:  # skip title page
            self.set_font("Arial", "I", 8)
            self.set_text_color(136, 136, 136)
            self.cell(0, 5, "Document Title", align="C")
            self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(136, 136, 136)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

pdf = MyPDF()
pdf.alias_nb_pages()  # enables {nb} placeholder in footer
```

## Color scheme

| Element | Color | Usage |
|---------|-------|-------|
| h1 underline | `#1a3a5c` (26, 58, 92) | Primary heading accent |
| h2 underline | `#2b5797` (43, 87, 151) | Section heading accent |
| Blockquote bg | `#f0f4f8` (240, 244, 248) | Quote background |
| Blockquote border | Same as h2 underline | Quote left border |
| Footer text | `#888888` (136, 136, 136) | Page numbers, header |

## Page margins

```python
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=18)  # 18mm bottom margin
# First page might need wider top margin
pdf.add_page()
pdf.set_y(25)  # start content 25mm from top on first page
```

## Multi-column tables

For tables that are too wide, use a smaller font (8pt) and tighter line spacing (4mm):

```python
pdf.set_font("Arial", "", 8)
for row in table_data:
    pdf.set_x(10)
    for cell in row:
        pdf.cell(40, 4, cell, border=1)
    pdf.ln()
```

## Checklist for professional output

- [ ] Page numbers in footer
- [ ] Running document title in header (on page 2+)
- [ ] Color scheme consistent (2-3 accent colors max)
- [ ] Margins at least 18mm all around
- [ ] Font no smaller than 8pt for tables, 9pt for body
- [ ] Section headers have page-break-before on h2 (or use manual page breaks)
- [ ] Emoji/special chars replaced with ASCII equivalents
