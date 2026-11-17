from io import BytesIO
from html import escape
from docx import Document
from docx.shared import Pt, Mm
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

TAMIL_FONT = "Marutham"

def make_txt(text):
    return text.encode("utf-8")

def make_docx(text):
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Mm(210), Mm(297)
    style = doc.styles["Normal"]
    style.font.name = TAMIL_FONT
    style.font.size = Pt(12)
    rpr = style._element.get_or_add_rPr()
    fonts = rpr.rFonts
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.insert(0, fonts)
    for k in ("ascii", "hAnsi", "eastAsia", "cs"):
        fonts.set(qn("w:"+k), TAMIL_FONT)
    for line in text.splitlines():
        doc.add_paragraph(line)
    b = BytesIO()
    doc.save(b)
    return b.getvalue()

def make_html(text):
    return ("<!doctype html><html lang='ta'><meta charset='utf-8'>"
            "<style>body{font-family:Marutham,'Noto Sans Tamil',Latha,sans-serif;"
            "white-space:pre-wrap;margin:25mm;line-height:1.7}</style><body>"
            + escape(text) + "</body></html>").encode("utf-8")
