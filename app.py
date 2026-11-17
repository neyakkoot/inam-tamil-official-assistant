import streamlit as st
from io import BytesIO

from inam.corrector import correct_text, convert_to_official_style
from inam.ai_assistant import (
    improve_with_ai, ai_is_configured, get_ai_model,
    generate_document_from_template,
)
from inam.documents import DOCUMENT_TYPES, build_document
from inam.exporters import make_docx, make_txt, make_html

st.set_page_config(page_title="இனம் – தமிழ் அலுவல் உதவி",
                   page_icon="📝", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: "Marutham", "Noto Sans Tamil", "Latha", sans-serif;
}
.block-container { max-width: 1200px; padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

if "run_id" not in st.session_state:
    st.session_state["run_id"] = 0
if "doc_run_id" not in st.session_state:
    st.session_state["doc_run_id"] = 0


def _clear_text_results():
    for k in ("source", "corrected", "findings", "official", "style_notes"):
        st.session_state.pop(k, None)


st.title("📝 இனம் – தமிழ் அலுவல் உதவி")
st.caption("Inam – Tamil Official Assistant · Version 2.3.0")
st.info(
    "அடிப்படைத் தமிழ் திருத்தம் API இல்லாமல் இயங்கும். "
    "பதிவேற்றிய மாதிரி ஆவணத்தைப் பின்பற்றி புதிய ஆவணம் உருவாக்க "
    "Gemini AI பயன்படுத்தப்படும்."
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
    st.caption("ரகசிய ஆவணங்கள் மற்றும் தனிப்பட்ட விவரங்களை வெளிப்புற AI-க்கு அனுப்ப வேண்டாம்.")

tab_text, tab_docs, tab_guide = st.tabs(
    ["மொழித்திருத்தம்", "அலுவல் ஆவணம்", "வழிகாட்டி"]
)

with tab_text:
    st.subheader("தமிழ் உரையைத் திருத்துதல்")
    source = st.text_area(
        "திருத்த வேண்டிய உரை",
        height=200,
        placeholder="தமிழில் தட்டச்சு செய்யவும்...",
        key="source_input",
        on_change=_clear_text_results,
    )
    c1, c2, c3, c4 = st.columns([1, 1, 1, 0.7])
    basic_clicked = c1.button("எழுத்து / சொற்றொடர் திருத்தம்",
                              type="primary", use_container_width=True)
    official_clicked = c2.button("அலுவல் மொழிநடையாக மாற்று",
                                 use_container_width=True)
    ai_clicked = c3.button("Gemini AI மூலம் மேம்படுத்து",
                           disabled=not ai_is_configured(),
                           use_container_width=True)
    if c4.button("அழி (Clear)", use_container_width=True):
        _clear_text_results()
        st.session_state["source_input"] = ""
        st.rerun()

    if basic_clicked:
        _clear_text_results()
        if source.strip():
            corrected, findings = correct_text(source)
            st.session_state["run_id"] += 1
            st.session_state.update(
                source=source,
                corrected=corrected,
                findings=findings,
                official=None,
                style_notes=[],
            )
        else:
            st.warning("முதலில் திருத்த வேண்டிய உரையை உள்ளிடவும்.")

    if official_clicked:
        _clear_text_results()
        if source.strip():
            corrected, findings = correct_text(source)
            formal, notes = convert_to_official_style(corrected)
            st.session_state["run_id"] += 1
            st.session_state.update(
                source=source,
                corrected=corrected,
                findings=findings,
                official=formal,
                style_notes=notes,
            )
        else:
            st.warning("முதலில் மாற்ற வேண்டிய உரையை உள்ளிடவும்.")

    if ai_clicked:
        _clear_text_results()
        if not source.strip():
            st.warning("முதலில் மேம்படுத்த வேண்டிய உரையை உள்ளிடவும்.")
        else:
            try:
                with st.spinner("Gemini AI பரிந்துரை உருவாக்கப்படுகிறது..."):
                    improved = improve_with_ai(source)
                st.session_state["run_id"] += 1
                st.session_state.update(
                    source=source,
                    corrected=improved,
                    findings=[{
                        "category": "Gemini AI பரிந்துரை",
                        "original": "உள்ளீட்டு உரை",
                        "suggestion": "AI மூலம் மேம்படுத்தப்பட்டது",
                        "reason": "பெயர்கள், எண்கள், தேதிகள் மற்றும் உண்மைகளைச் சரிபார்க்கவும்.",
                    }],
                    official=None,
                    style_notes=[],
                )
            except Exception as exc:
                st.error(f"AI சேவையை அணுக முடியவில்லை: {exc}")

    if "corrected" in st.session_state:
        rid = st.session_state["run_id"]
        st.divider()
        st.subheader("1. அசல் உரை")
        st.text_area(
            "அசல் உரை",
            value=st.session_state["source"],
            height=100,
            disabled=True,
            key=f"original_output_{rid}",
        )
        st.subheader("2. திருத்தப்பட்ட உரை")
        corrected_edit = st.text_area(
            "திருத்தப்பட்ட உரையைச் சரிபார்த்து மாற்றலாம்",
            value=st.session_state["corrected"],
            height=160,
            key=f"corrected_edit_{rid}",
        )
        st.download_button("திருத்தப்பட்ட உரை – TXT", make_txt(corrected_edit),
                           "inam-corrected-tamil.txt", "text/plain; charset=utf-8")
        st.subheader("கண்டறியப்பட்ட மாற்றங்கள் / பரிந்துரைகள்")
        findings_list = st.session_state.get("findings", [])
        if not findings_list:
            st.info("எவ்வித எழுத்துப் பிழையும் கண்டறியப்படவில்லை.")
        for i, item in enumerate(findings_list, 1):
            with st.expander(f"{i}. {item['category']}"):
                st.write("**அசல்:** " + item["original"])
                st.write("**பரிந்துரை:** " + item["suggestion"])
                st.caption(item["reason"])
        if st.session_state.get("official") is not None:
            st.subheader("3. அலுவல் மொழிநடை வரைவு")
            formal_edit = st.text_area(
                "அலுவல் மொழிநடையைச் சரிபார்க்கவும்",
                value=st.session_state["official"],
                height=160,
                key=f"formal_edit_{rid}",
            )
            st.download_button("அலுவல் மொழிநடை – TXT", make_txt(formal_edit),
                               "inam-official-style.txt", "text/plain; charset=utf-8")
            for note in st.session_state.get("style_notes", []):
                st.caption("• " + note)

with tab_docs:
    st.subheader("மாதிரி அலுவல் கோப்பைப் பின்பற்றி புதிய ஆவணம்")
    st.write(
        "சுற்றறிக்கை, அலுவல் கடிதம், குறிப்பாணை போன்ற மாதிரி DOCX, PDF அல்லது TXT "
        "கோப்பைப் பதிவேற்றுங்கள். உரை PDF மட்டுமன்றி ஸ்கேன் செய்யப்பட்ட PDF-யையும் "
        "Gemini AI நேரடியாகப் படித்து வரைவை உருவாக்கும்."
    )

    kind = st.selectbox("புதிய ஆவண வகை", list(DOCUMENT_TYPES.keys()))
    sample_file = st.file_uploader(
        "மாதிரி அலுவல் கோப்பைப் பதிவேற்றவும்",
        type=["docx", "pdf", "txt"],
        key="official_template_upload"
    )

    left, right = st.columns(2)
    office = left.text_input("அலுவலகம் / துறை")
    recipient = left.text_input("பெறுநர்")
    date = left.text_input("நாள்")
    reference = right.text_input("ந.க.எண் / குறிப்பு எண்")
    subject = right.text_input("பொருள்")
    place = right.text_input("இடம்")
    body = st.text_area("புதிய ஆவணத்திற்கான உள்ளடக்கம் / குறிப்புகள்", height=150)
    signatory = st.text_input("கையொப்பமிடுபவர் / பதவி")

    if sample_file is not None:
        st.success(f"கோப்பு இணைக்கப்பட்டது: {sample_file.name}")
        st.caption(
            "PDF கோப்பை இங்கு முன்கூட்டியே உரையாக மாற்ற வேண்டியதில்லை. "
            "Gemini AI-க்கு PDF கோப்பு நேரடியாக அனுப்பப்படும்; ஸ்கேன் பக்கங்களையும் "
            "படித்து உள்ளடக்கத்தைப் புரிந்துகொள்ளும்."
        )

    if st.button(
        "பதிவேற்றிய மாதிரியைப் பின்பற்றி Gemini AI மூலம் உருவாக்கு",
        type="primary",
        disabled=(not ai_is_configured() or sample_file is None)
    ):
        st.session_state.pop("doc", None)
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
            with st.spinner("மாதிரி ஆவணத்தை AI படித்து புதிய வரைவு உருவாக்குகிறது..."):
                st.session_state["doc"] = generate_document_from_template(
                    sample_bytes=sample_file.getvalue(),
                    filename=sample_file.name,
                    doc_type=kind,
                    details=details,
                )
            st.session_state["doc_run_id"] += 1
            st.success("புதிய அலுவல் ஆவண வரைவு உருவாக்கப்பட்டது.")
        except Exception as exc:
            st.error(f"AI ஆவணத்தை உருவாக்க முடியவில்லை: {exc}")

    if not ai_is_configured():
        st.info("மாதிரி ஆவணத்தை AI மூலம் படித்து எழுத Gemini API Key தேவை.")

    st.divider()
    st.subheader("AI இல்லாத அடிப்படை ஆவண உருவாக்கம்")
    with st.expander("விவரங்களை நிரப்பி அடிப்படை வரைவை உருவாக்க"):
        basic_kind = st.selectbox("அடிப்படை ஆவண வகை", list(DOCUMENT_TYPES.keys()),
                                  key="basic_kind")
        b1, b2 = st.columns(2)
        basic_office = b1.text_input("அலுவலகம்", key="basic_office")
        basic_recipient = b1.text_input("பெறுநர்", key="basic_recipient")
        basic_date = b1.text_input("நாள்", key="basic_date")
        basic_ref = b2.text_input("ந.க.எண்", key="basic_ref")
        basic_subject = b2.text_input("பொருள்", key="basic_subject")
        basic_place = b2.text_input("இடம்", key="basic_place")
        basic_body = st.text_area("உள்ளடக்கம்", key="basic_body")
        basic_sign = st.text_input("கையொப்பமிடுபவர் / பதவி", key="basic_sign")
        if st.button("அடிப்படை ஆவண வரைவை உருவாக்கு"):
            st.session_state.pop("doc", None)
            st.session_state["doc"] = build_document(
                basic_kind, basic_office, basic_recipient, basic_date,
                basic_ref, basic_subject, basic_body, basic_place, basic_sign
            )
            st.session_state["doc_run_id"] += 1

    if "doc" in st.session_state:
        drid = st.session_state["doc_run_id"]
        st.subheader("உருவாக்கப்பட்ட ஆவணம்")
        document_edit = st.text_area(
            "வரைவைத் திருத்தவும்",
            value=st.session_state["doc"],
            height=320,
            key=f"doc_edit_{drid}",
        )
        st.download_button(
            "Word (.docx)", make_docx(document_edit),
            "inam-official-document.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        st.download_button("TXT", make_txt(document_edit),
                           "inam-official-document.txt", "text/plain; charset=utf-8")
        st.download_button("HTML (PDF அச்சிடலுக்கு)", make_html(document_edit),
                           "inam-official-document.html", "text/html; charset=utf-8")
        st.caption("Word கோப்பைத் திறந்து தேவையான பக்க அமைப்பைச் சரிபார்க்கவும்.")

with tab_guide:
    st.subheader("பயன்பாட்டு வழிகாட்டி")
    st.markdown("""
- அடிப்படைத் தமிழ் திருத்தம் மற்றும் முன்வரையறுக்கப்பட்ட ஆவண உருவாக்கம் API இல்லாமல் இயங்கும்.
- மாதிரி DOCX/TXT/PDF-ஐப் பின்பற்றி AI வரைவு உருவாக்க Gemini API தேவை.
- ஸ்கேன் செய்யப்பட்ட PDF-யும் Gemini-க்கு நேரடியாக அனுப்பப்படும்; தனியாக OCR மென்பொருள் நிறுவ வேண்டியதில்லை.
- AI உருவாக்கிய வரைவை வெளியிடுவதற்கு முன் பெயர்கள், தேதிகள், எண்கள், அரசாணை மற்றும் சட்டக் குறிப்புகளைச் சரிபார்க்கவும்.
- Marutham எழுத்துரு கணினியில் நிறுவப்பட்டிருக்க வேண்டும்; இல்லையெனில் மாற்று எழுத்துரு பயன்படுத்தப்படும்.
""")
