
from io import BytesIO
from html import escape
import re

from docx import Document
from docx.shared import Pt, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


# --------------------------------------------------
# தமிழ் எழுத்துரு அமைப்பு
# --------------------------------------------------

TAMIL_FONT = "Noto Sans Tamil"
FALLBACK_FONT = "Latha"

FONT_SIZE = 12
TITLE_SIZE = 14


def set_tamil_font(run, font_name=TAMIL_FONT, size=FONT_SIZE,
                   bold=False):

    run.font.name = font_name
    run.font.size = Pt(size)
    run.bold = bold

    rpr = run._element.get_or_add_rPr()

    rfonts = rpr.rFonts

    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)

    rfonts.set(qn("w:ascii"), font_name)
    rfonts.set(qn("w:hAnsi"), font_name)
    rfonts.set(qn("w:eastAsia"), font_name)
    rfonts.set(qn("w:cs"), font_name)


def set_style_font(style):

    style.font.name = TAMIL_FONT
    style.font.size = Pt(FONT_SIZE)

    rpr = style._element.get_or_add_rPr()

    rfonts = rpr.rFonts

    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)

    rfonts.set(qn("w:ascii"), TAMIL_FONT)
    rfonts.set(qn("w:hAnsi"), TAMIL_FONT)
    rfonts.set(qn("w:eastAsia"), TAMIL_FONT)
    rfonts.set(qn("w:cs"), TAMIL_FONT)


# --------------------------------------------------
# TXT ஏற்றுமதி
# --------------------------------------------------

def make_txt(text: str) -> bytes:

    return text.encode("utf-8")


# --------------------------------------------------
# வெற்றிடங்களைச் சீரமைத்தல்
# --------------------------------------------------

def clean_document_text(text):

    lines = text.replace("\r\n", "\n").replace(
        "\r", "\n"
    ).split("\n")

    cleaned = []
    previous_blank = False

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


# --------------------------------------------------
# அலுவல் ஆவண வகைகள்
# --------------------------------------------------

DOCUMENT_HEADINGS = {
    "அலுவல் கடிதம்",
    "அலுவலகக் குறிப்பு",
    "அறிக்கை",
    "சுற்றறிக்கை",
    "குறிப்பாணை",
    "நினைவூட்டல்",
    "கூட்ட நடவடிக்கைக் குறிப்புகள்",
}


# --------------------------------------------------
# Word DOCX உருவாக்கம்
# --------------------------------------------------

def make_docx(text: str) -> bytes:

    doc = Document()

    # A4 பக்க அமைப்பு
    section = doc.sections[0]

    section.page_width = Mm(210)
    section.page_height = Mm(297)

    section.top_margin = Mm(22)
    section.bottom_margin = Mm(22)

    section.left_margin = Mm(25)
    section.right_margin = Mm(25)

    section.header_distance = Mm(10)
    section.footer_distance = Mm(10)

    # இயல்புநிலை எழுத்துரு
    style = doc.styles["Normal"]

    set_style_font(style)

    style.paragraph_format.space_before = Pt(0)
    style.paragraph_format.space_after = Pt(5)
    style.paragraph_format.line_spacing = 1.25

    style.paragraph_format.widow_control = True

    # ஆவண உள்ளடக்கத்தைச் சீரமைத்தல்
    lines = clean_document_text(text)

    first_content = True

    for line in lines:

        # வெற்றுவரி
        if not line:

            paragraph = doc.add_paragraph()

            paragraph.paragraph_format.space_before = Pt(0)
            paragraph.paragraph_format.space_after = Pt(2)
            paragraph.paragraph_format.line_spacing = 1

            continue

        paragraph = doc.add_paragraph()

        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.space_after = Pt(5)
        paragraph.paragraph_format.line_spacing = 1.25

        paragraph.paragraph_format.widow_control = True

        run = paragraph.add_run(line)

        # முதல் வரி - அலுவலகத் தலைப்பு
        if first_content:

            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

            paragraph.paragraph_format.space_after = Pt(14)

            set_tamil_font(
                run,
                size=TITLE_SIZE,
                bold=True
            )

            paragraph.paragraph_format.keep_with_next = True

            first_content = False

        # ஆவணத்தின் தலைப்பு
        elif line in DOCUMENT_HEADINGS:

            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

            paragraph.paragraph_format.space_before = Pt(8)
            paragraph.paragraph_format.space_after = Pt(10)

            paragraph.paragraph_format.keep_with_next = True

            set_tamil_font(
                run,
                size=TITLE_SIZE,
                bold=True
            )

        # ந.க.எண், நாள், பொருள் போன்ற விவரங்கள்
        elif line.startswith(
            ("ந.க.எண்:", "நாள்:", "பெறுநர்:",
             "பொருள்:", "குறிப்பு:", "இடம்:")
        ):

            set_tamil_font(
                run,
                size=FONT_SIZE,
                bold=True
            )

            paragraph.paragraph_format.keep_with_next = True

        # பிற உரைகள்
        else:

            set_tamil_font(
                run,
                size=FONT_SIZE,
                bold=False
            )

        paragraph.paragraph_format.keep_together = True

    # ஆவணப் பண்புகள்
    doc.core_properties.title = "இனம் – தமிழ் அலுவல் ஆவணம்"
    doc.core_properties.subject = "தமிழ் அலுவல் ஆவண உருவாக்கம்"
    doc.core_properties.author = "Inam – Tamil Official Assistant"

    # DOCX கோப்பை உருவாக்குதல்
    buffer = BytesIO()

    doc.save(buffer)

    buffer.seek(0)

    return buffer.getvalue()


# --------------------------------------------------
# HTML ஏற்றுமதி
# --------------------------------------------------

def make_html(text: str) -> bytes:

    safe = escape(text)

    html = f"""<!DOCTYPE html>
<html lang="ta">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>இனம் – அலுவல் ஆவணம்</title>

<style>

@page {{
    size: A4;
    margin: 22mm 25mm;
}}

body {{

    font-family:
    'Noto Sans Tamil',
    'Latha',
    sans-serif;

    font-size: 12pt;

    line-height: 1.7;

    color: #111;

}}

.document {{

    white-space: pre-wrap;

    overflow-wrap: break-word;

    word-wrap: break-word;

}}

@media print {{

    body {{
        background: white;
    }}

}}

</style>

</head>

<body>

<div class="document">{safe}</div>

</body>

</html>
"""

    return html.encode("utf-8")
