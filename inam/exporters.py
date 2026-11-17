from io import BytesIO
from html import escape
from docx import Document
from docx.shared import Pt

def make_txt(text: str) -> bytes:
    return text.encode("utf-8")

def make_docx(text: str) -> bytes:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Noto Sans Tamil"
    style.font.size = Pt(12)
    for line in text.splitlines():
        doc.add_paragraph(line)
    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()

def make_html(text: str) -> bytes:
    safe = escape(text)
    html = f"""<!doctype html>
<html lang="ta"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>இனம் – அலுவல் ஆவணம்</title>
<style>
@page {{ size: A4; margin: 25mm; }}
body {{ font-family: 'Noto Sans Tamil','Latha',sans-serif; font-size: 12pt; line-height: 1.8; }}
pre {{ white-space: pre-wrap; overflow-wrap: break-word; font-family: inherit; }}
</style></head><body><pre>{safe}</pre></body></html>"""
    return html.encode("utf-8")
