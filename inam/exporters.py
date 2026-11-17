from io import BytesIO
from html import escape

from docx import Document
from docx.shared import Pt, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

TAMIL_FONT = "Marutham"
FONT_SIZE = 12
TITLE_SIZE = 14


def set_tamil_font(run, font_name=TAMIL_FONT, size=FONT_SIZE, bold=False):
    run.font.name = font_name
    run.font.size = Pt(size)
    run.bold = bold
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.rFonts
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for key in ("ascii", "hAnsi", "eastAsia", "cs"):
        rfonts.set(qn(f"w:{key}"), font_name)


def set_style_font(style):
    style.font.name = TAMIL_FONT
    style.font.size = Pt(FONT_SIZE)
    rpr = style._element.get_or_add_rPr()
    rfonts = rpr.rFonts
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for key in ("ascii", "hAnsi", "eastAsia", "cs"):
        rfonts.set(qn(f"w:{key}"), TAMIL_FONT)


def make_txt(text: str) -> bytes:
    return text.encode("utf-8")


def clean_document_text(text):
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    cleaned, previous_blank = [], False
    for line in lines:
        line = line.rstrip()
        if not line.strip():
            if not previous_blank:
                cleaned.append("")
            previous_blank = True
        else:
            cleaned.append(line.strip())
            previous_blank = False
    return cleaned


DOCUMENT_HEADINGS = {
    "அலுவல் கடிதம்", "அலுவலகக் குறிப்பு", "அறிக்கை",
    "சுற்றறிக்கை", "குறிப்பாணை", "நினைவூட்டல்",
    "கூட்ட நடவடிக்கைக் குறிப்புகள்",
}


def make_docx(text: str) -> bytes:
    doc = Document()
    section = doc.sections[0]
    section.page_width, section.page_height = Mm(210), Mm(297)
    section.top_margin = section.bottom_margin = Mm(22)
    section.left_margin = section.right_margin = Mm(25)
    section.header_distance = section.footer_distance = Mm(10)

    style = doc.styles["Normal"]
    set_style_font(style)
    style.paragraph_format.space_after = Pt(5)
    style.paragraph_format.line_spacing = 1.25
    style.paragraph_format.widow_control = True

    first_content = True
    for line in clean_document_text(text):
        paragraph = doc.add_paragraph()
        if not line:
            paragraph.paragraph_format.space_after = Pt(2)
            continue
        run = paragraph.add_run(line)
        paragraph.paragraph_format.space_after = Pt(5)
        paragraph.paragraph_format.line_spacing = 1.25
        paragraph.paragraph_format.keep_together = True

        if first_content:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.space_after = Pt(14)
            paragraph.paragraph_format.keep_with_next = True
            set_tamil_font(run, size=TITLE_SIZE, bold=True)
            first_content = False
        elif line in DOCUMENT_HEADINGS:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.space_before = Pt(8)
            paragraph.paragraph_format.space_after = Pt(10)
            paragraph.paragraph_format.keep_with_next = True
            set_tamil_font(run, size=TITLE_SIZE, bold=True)
        else:
            set_tamil_font(run, size=FONT_SIZE, bold=False)

    doc.core_properties.title = "இனம் – தமிழ் அலுவல் ஆவணம்"
    doc.core_properties.subject = "தமிழ் அலுவல் ஆவண உருவாக்கம்"
    doc.core_properties.author = "Inam – Tamil Official Assistant"

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def make_html(text: str) -> bytes:
    safe = escape(text)
    html = f"""<!DOCTYPE html>
<html lang="ta"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>இனம் – அலுவல் ஆவணம்</title>
<style>
@page {{ size: A4; margin: 22mm 25mm; }}
body {{ font-family: 'Marutham', 'Noto Sans Tamil', 'Latha', sans-serif;
       font-size: 12pt; line-height: 1.7; color: #111; }}
.document {{ white-space: pre-wrap; overflow-wrap: break-word; }}
</style></head><body><div class="document">{safe}</div></body></html>"""
    return html.encode("utf-8")
