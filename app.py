import streamlit as st
from io import BytesIO

from inam.corrector import correct_text, convert_to_official_style
from inam.ai_assistant import (
    improve_with_ai, ai_is_configured, get_ai_model,
    generate_document_from_template,
)
from inam.documents import DOCUMENT_TYPES, build_document
from inam.exporters import make_docx, make_txt, make_html

st.set_page_config(
    page_title="இனம் – தமிழ் அலுவல் உதவி",
    page_icon="📝",
    layout="wide",
)

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: "Marutham", "Noto Sans Tamil", "Latha", sans-serif;
}
.block-container { max-width: 1200px; padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

st.title("📝 இனம் – தமிழ் அலுவல் உதவி")
st.caption("Inam – Tamil Official Assistant · Version 2.1.0")
st.info(
    "தமிழ் உரைத் திருத்தம் மற்றும் அடிப்படை அலுவல் ஆவண உருவாக்கம் "
    "API இல்லாமலேயே இயங்கும். பதிவேற்றிய மாதிரியைப் பின்பற்றி புதிய "
    "ஆவணம் உருவாக்க Gemini API தேவை."
)

with st.sidebar:
    st.subheader("அடிப்படை வசதிகள்")
    st.success("அடிப்படைத் திருத்தம் – API தேவையில்லை")
    st.caption("தமிழ் உரைத் திருத்தம், அலுவல் மொழிநடை, Word/TXT/HTML பதிவிறக்கம்.")
    st.divider()
    st.subheader("விருப்பத்தேர்வு AI இணைப்பு")
    if ai_is_configured():
        st.success("Gemini API அமைக்கப்பட்டுள்ளது")
        st.caption(f"மாதிரி: {get_ai_model()}")
    else:
        st.warning("Gemini API Key அமைக்கப்படவில்லை")
    st.caption(
        "ரகசிய அரசு ஆவணங்கள், மாணவர் தனிப்பட்ட விவரங்கள், "
        "கடவுச்சொற்கள் போன்றவற்றை வெளிப்புற AI சேவைக்கு அனுப்ப வேண்டாம்."
    )

tab_text, tab_docs, tab_guide = st.tabs(
    ["மொழித்திருத்தம்", "அலுவல் ஆவணம்", "வழிகாட்டி"]
)

with tab_text:
    st.subheader("தமிழ் உரையைத் திருத்துதல்")
    source = st.text_area(
        "திருத்த வேண்டிய உரை", height=200,
        placeholder="தமிழில் தட்டச்சு செய்யவும் அல்லது உரையை ஒட்டவும்...",
        key="source_input",
    )
    c1, c2, c3 = st.columns(3)
    basic_clicked = c1.button("எழுத்து / சொற்றொடர் திருத்தம்", type="primary",
                              use_container_width=True)
    official_clicked = c2.button("அலுவல் மொழிநடையாக மாற்று",
                                 use_container_width=True)
    ai_clicked = c3.button("Gemini AI மூலம் மேம்படுத்து",
                           disabled=not ai_is_configured(),
                           use_container_width=True)

    if basic_clicked and source.strip():
        corrected, findings = correct_text(source)
        st.session_state.update(source=source, corrected=corrected,
                                findings=findings, official=None, style_notes=[])
    elif basic_clicked:
        st.warning("முதலில் திருத்த வேண்டிய உரையை உள்ளிடவும்.")

    if official_clicked and source.strip():
        corrected, findings = correct_text(source)
        formal, notes = convert_to_official_style(corrected)
        st.session_state.update(source=source, corrected=corrected,
                                findings=findings, official=formal,
                                style_notes=notes)
    elif official_clicked:
        st.warning("முதலில் மாற்ற வேண்டிய உரையை உள்ளிடவும்.")

    if ai_clicked:
        if not source.strip():
            st.warning("முதலில் மேம்படுத்த வேண்டிய உரையை உள்ளிடவும்.")
        else:
            try:
                with st.spinner("Gemini AI பரிந்துரை உருவாக்கப்படுகிறது..."):
                    improved = improve_with_ai(source)
                st.session_state.update(
                    source=source, corrected=improved,
                    findings=[{
                        "category": "Gemini AI பரிந்துரை",
                        "original": "உள்ளீட்டு உரை",
                        "suggestion": "AI மூலம் மேம்படுத்தப்பட்டது",
                        "reason": "பெயர்கள், எண்கள், தேதிகள் மற்றும் உண்மைகளைச் சரிபார்க்கவும்.",
                    }],
                    official=None, style_notes=[]
                )
            except Exception as exc:
                st.error(f"AI சேவையை அணுக முடியவில்லை: {exc}")

    if "corrected" in st.session_state:
        st.divider()
        st.subheader("1. அசல் உரை")
        st.text_area("அசல் உரை", st.session_state["source"],
                     height=100, disabled=True, key="original_output")
        st.subheader("2. திருத்தப்பட்ட உரை")
        corrected_edit = st.text_area(
            "திருத்தப்பட்ட உரையைச் சரிபார்த்து மாற்றலாம்",
            st.session_state["corrected"], height=160, key="corrected_edit"
        )
        st.download_button("திருத்தப்பட்ட உரை – TXT", make_txt(corrected_edit),
                           "inam-corrected-tamil.txt",
                           "text/plain; charset=utf-8")
        st.subheader("கண்டறியப்பட்ட மாற்றங்கள் / பரிந்துரைகள்")
        for i, item in enumerate(st.session_state.get("findings", []), 1):
            with st.expander(f"{i}. {item['category']}"):
                st.write("**அசல்:** " + item["original"])
                st.write("**பரிந்துரை:** " + item["suggestion"])
                st.caption(item["reason"])
        if st.session_state.get("official") is not None:
            st.subheader("3. அலுவல் மொழிநடை வரைவு")
            formal_edit = st.text_area("அலுவல் மொழிநடையைச் சரிபார்க்கவும்",
                                       st.session_state["official"],
                                       height=160, key="formal_edit")
            st.download_button("அலுவல் மொழிநடை – TXT", make_txt(formal_edit),
                               "inam-official-style.txt",
                               "text/plain; charset=utf-8")
            for note in st.session_state.get("style_notes", []):
                st.caption("• " + note)

with tab_docs:
    st.subheader("அலுவல் ஆவணம் உருவாக்குதல்")
    kind = st.selectbox("ஆவண வகை", list(DOCUMENT_TYPES.keys()))
    left, right = st.columns(2)
    office = left.text_input("அலுவலகம் / துறை")
    recipient = left.text_input("பெறுநர்")
    date = left.text_input("நாள்")
    reference = right.text_input("ந.க.எண் / குறிப்பு எண்")
    subject = right.text_input("பொருள்")
    place = right.text_input("இடம்")
    body = st.text_area("உள்ளடக்கம் / குறிப்புகள்", height=160)
    signatory = st.text_input("கையொப்பமிடுபவர் / பதவி")

    if st.button("அடிப்படை ஆவண வரைவை உருவாக்கு", type="primary"):
        st.session_state["doc"] = build_document(
            kind, office, recipient, date, reference, subject,
            body, place, signatory
        )

    st.divider()
    st.subheader("மாதிரி அலுவல் கோப்பைப் பின்பற்றி புதிய ஆவணம்")
    st.write(
        "சுற்றறிக்கை, அலுவல் கடிதம், குறிப்பாணை போன்ற மாதிரி DOCX, PDF "
        "அல்லது TXT கோப்பைப் பதிவேற்றுங்கள். AI அதன் வடிவமைப்பு மற்றும் "
        "மொழிநடையைப் பின்பற்றி புதிய வரைவை உருவாக்கும்."
    )
    sample_file = st.file_uploader(
        "மாதிரி அலுவல் கோப்பைப் பதிவேற்றவும்",
        type=["docx", "pdf", "txt"],
        key="official_template_upload"
    )

    sample_text = ""
    if sample_file is not None:
        raw = sample_file.getvalue()
        try:
            filename = sample_file.name.lower()
            if filename.endswith(".docx"):
                from docx import Document
                parsed = Document(BytesIO(raw))
                chunks = [p.text for p in parsed.paragraphs if p.text.strip()]
                for table in parsed.tables:
                    for row in table.rows:
                        chunks.append(" | ".join(cell.text for cell in row.cells))
                sample_text = "\n".join(chunks)
            elif filename.endswith(".pdf"):
                from pypdf import PdfReader
                reader = PdfReader(BytesIO(raw))
                sample_text = "\n".join(page.extract_text() or "" for page in reader.pages)
            else:
                sample_text = raw.decode("utf-8-sig", errors="replace")

            if sample_text.strip():
                st.success(f"மாதிரி கோப்பு வாசிக்கப்பட்டது: {sample_file.name}")
                with st.expander("வாசிக்கப்பட்ட மாதிரி உரையைப் பார்க்க"):
                    st.text(sample_text[:12000])
            else:
                st.warning(
                    "கோப்பிலிருந்து உரையைப் பெற முடியவில்லை. ஸ்கேன் செய்யப்பட்ட PDF-க்கு "
                    "OCR செய்யப்பட்ட DOCX/TXT கோப்பைப் பயன்படுத்தவும்."
                )
        except Exception as exc:
            st.error(f"மாதிரி கோப்பைப் படிக்க முடியவில்லை: {exc}")

    if sample_file is not None:
        if st.button(
            "பதிவேற்றிய மாதிரியைப் பின்பற்றி Gemini AI மூலம் உருவாக்கு",
            type="primary",
            disabled=(not ai_is_configured() or not sample_text.strip())
        ):
            details = {
                "ஆவண வகை": kind,
                "அலுவலகம் / துறை": office,
                "பெறுநர்": recipient,
                "நாள்": date,
                "ந.க.எண் / குறிப்பு எண்": reference,
                "பொருள்": subject,
                "இடம்": place,
                "புதிய ஆவணத்திற்கான உள்ளடக்கம் / குறிப்புகள்": body,
                "கையொப்பமிடுபவர் / பதவி": signatory,
            }
            try:
                with st.spinner("மாதிரி கோப்பை ஆய்ந்து புதிய ஆவணம் உருவாக்கப்படுகிறது..."):
                    st.session_state["doc"] = generate_document_from_template(
                        sample_text, kind, details
                    )
                st.success("மாதிரி வடிவத்தைப் பின்பற்றி புதிய வரைவு உருவாக்கப்பட்டது.")
            except Exception as exc:
                st.error(f"AI ஆவணத்தை உருவாக்க முடியவில்லை: {exc}")

    if not ai_is_configured():
        st.info("மாதிரி கோப்பிலிருந்து AI ஆவணம் உருவாக்க Gemini API Key தேவை.")

    if "doc" in st.session_state:
        document_edit = st.text_area(
            "உருவாக்கப்பட்ட வரைவைத் திருத்தவும்",
            st.session_state["doc"], height=300, key="doc_edit"
        )
        st.download_button(
            "Word (.docx)", make_docx(document_edit),
            "inam-official-document.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        st.download_button("TXT", make_txt(document_edit),
                           "inam-official-document.txt",
                           "text/plain; charset=utf-8")
        st.download_button("HTML (PDF அச்சிடலுக்கு)", make_html(document_edit),
                           "inam-official-document.html", "text/html; charset=utf-8")
        st.caption("HTML கோப்பை உலாவியில் திறந்து Print → Save as PDF தேர்வு செய்யலாம்.")

with tab_guide:
    st.subheader("பயன்பாட்டு வழிகாட்டி")
    st.markdown("""
- அடிப்படைத் தமிழ் திருத்தம் மற்றும் முன்வரையறுக்கப்பட்ட ஆவண உருவாக்கம் API இல்லாமல் இயங்கும்.
- பதிவேற்றிய மாதிரியைப் பின்பற்றி AI மூலம் ஆவணம் உருவாக்க Gemini API தேவை.
- DOCX, உரை PDF (உரைத் தேர்வு செய்யக்கூடிய PDF), TXT கோப்புகள் ஆதரிக்கப்படுகின்றன.
- ஸ்கேன் செய்யப்பட்ட பட-PDF-க்கு OCR வசதி இந்தப் பதிப்பில் சேர்க்கப்படவில்லை.
- AI உருவாக்கிய ஆவணத்தை வெளியிடுவதற்கு முன் பெயர்கள், தேதிகள், எண்கள், அரசாணை/சட்டக் குறிப்புகளைச் சரிபார்க்கவும்.
""")
