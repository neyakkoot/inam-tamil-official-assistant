import streamlit as st
from inam.corrector import correct_text
from inam.ai_assistant import improve_with_ai, ai_is_configured
from inam.documents import DOCUMENT_TYPES, build_document
from inam.exporters import make_docx, make_txt, make_html

st.set_page_config(page_title="இனம் – தமிழ் அலுவல் உதவி", page_icon="📝", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"] { font-family: "Noto Sans Tamil", "Latha", sans-serif; }
.block-container { max-width: 1200px; padding-top: 1.5rem; }
.inam-subtitle { color: #64748b; font-size: 1rem; }
</style>
""", unsafe_allow_html=True)

st.title("📝 இனம் – தமிழ் அலுவல் உதவி")
st.markdown('<p class="inam-subtitle">தமிழ் மொழித்திருத்தம் · அலுவல் மொழிநடை · ஆவண உருவாக்கம்</p>', unsafe_allow_html=True)
st.info("இந்த முதல் பதிப்பு ஒரு தொடக்கநிலை மாதிரி. உருவாக்கப்படும் உரை மற்றும் திருத்தங்களை அலுவலர் சரிபார்த்த பிறகே பயன்படுத்த வேண்டும்.")

with st.sidebar:
    st.header("திட்ட விவரம்")
    st.write("**Inam – Tamil Official Assistant**")
    st.caption("Version 1.0.0 · Open-source prototype")
    st.divider()
    st.subheader("AI இணைப்பு")
    if ai_is_configured():
        st.success("AI API அமைக்கப்பட்டுள்ளது")
    else:
        st.warning("AI API அமைக்கப்படவில்லை. விதிமுறை அடிப்படையிலான அம்சங்கள் மட்டும் இயங்கும்.")
    st.caption("ரகசிய அல்லது தனிப்பட்ட அலுவல் ஆவணங்களை வெளிப்புற AI சேவைக்கு அனுப்ப வேண்டாம்.")

tab1, tab2, tab3 = st.tabs(["மொழித்திருத்தம்", "அலுவல் ஆவணம்", "வழிகாட்டி"])

with tab1:
    st.subheader("தமிழ் உரையைத் திருத்துதல்")
    source = st.text_area("திருத்த வேண்டிய உரையை உள்ளிடவும்", height=220,
                          placeholder="உங்கள் தமிழ் உரையை இங்கே தட்டச்சு செய்யவும் அல்லது ஒட்டவும்...")
    c1, c2 = st.columns([1, 1])
    with c1:
        run_rules = st.button("அடிப்படை மொழித்திருத்தம்", type="primary", use_container_width=True)
    with c2:
        run_ai = st.button("AI மூலம் மொழிநடையை மேம்படுத்து", use_container_width=True,
                           disabled=not ai_is_configured())
    if run_rules and source.strip():
        result, notes = correct_text(source)
        st.session_state["corrected_text"] = result
        st.session_state["correction_notes"] = notes
    if run_ai and source.strip():
        with st.spinner("AI திருத்தம் நடைபெறுகிறது..."):
            try:
                result = improve_with_ai(source)
                st.session_state["corrected_text"] = result
                st.session_state["correction_notes"] = ["AI உருவாக்கிய பரிந்துரை. இறுதியாக மனிதர் சரிபார்க்க வேண்டும்."]
            except Exception as exc:
                st.error(f"AI சேவையை அணுக முடியவில்லை: {exc}")
    if "corrected_text" in st.session_state:
        st.markdown("#### திருத்தப்பட்ட உரை")
        edited = st.text_area("திருத்தப்பட்ட உரையைச் சரிபார்த்து மாற்றலாம்",
                              value=st.session_state["corrected_text"], height=220, key="edited_result")
        st.session_state["final_text"] = edited
        for note in st.session_state.get("correction_notes", []):
            st.caption("• " + note)
        st.download_button("திருத்தப்பட்ட உரையை TXT ஆகப் பதிவிறக்கு",
                           make_txt(edited), file_name="inam-corrected-tamil.txt",
                           mime="text/plain; charset=utf-8")

with tab2:
    st.subheader("அலுவல் ஆவணம் உருவாக்குதல்")
    doc_type = st.selectbox("ஆவண வகை", list(DOCUMENT_TYPES.keys()))
    col1, col2 = st.columns(2)
    with col1:
        office = st.text_input("அலுவலகம் / துறை", placeholder="எ.கா. அரசு அலுவலகம்")
        recipient = st.text_input("பெறுநர்", placeholder="பெறுநரின் பதவி / அலுவலகம்")
        date = st.text_input("நாள்", placeholder="எ.கா. 17.11.2026")
    with col2:
        reference = st.text_input("ந.க.எண் / குறிப்பு எண்", placeholder="தேவைப்பட்டால் மட்டும்")
        subject = st.text_input("பொருள்", placeholder="ஆவணத்தின் பொருள்")
        place = st.text_input("இடம்", placeholder="இடம்")
    body = st.text_area("உள்ளடக்கம் / குறிப்புகள்", height=190,
                        placeholder="ஆவணத்தில் இடம்பெற வேண்டிய தகவல்களை உள்ளிடவும்...")
    signatory = st.text_input("கையொப்பமிடுபவர் / பதவி", placeholder="பெயர், பதவி")
    if st.button("ஆவண வரைவை உருவாக்கு", type="primary"):
        st.session_state["document_text"] = build_document(
            doc_type, office, recipient, date, reference, subject, body, place, signatory
        )
    if "document_text" in st.session_state:
        st.markdown("#### உருவாக்கப்பட்ட வரைவு")
        doc_text = st.text_area("வரைவைத் திருத்தவும்", value=st.session_state["document_text"],
                                height=360, key="document_edit")
        st.download_button("Word (.docx) பதிவிறக்கம்", make_docx(doc_text),
                           file_name="inam-official-document.docx",
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        st.download_button("TXT பதிவிறக்கம்", make_txt(doc_text),
                           file_name="inam-official-document.txt", mime="text/plain; charset=utf-8")
        st.download_button("HTML பதிவிறக்கம் (PDF அச்சிடலுக்கு)", make_html(doc_text),
                           file_name="inam-official-document.html", mime="text/html; charset=utf-8")
        st.caption("HTML கோப்பை Chrome-இல் திறந்து Print → Save as PDF தேர்வு செய்யலாம். சரியான தமிழ் எழுத்துரு நிறுவப்பட்டுள்ளதா உறுதிப்படுத்தவும்.")

with tab3:
    st.subheader("பயன்பாட்டு வழிகாட்டி")
    st.markdown("""
    1. **மொழித்திருத்தம்:** உரையை ஒட்டி அடிப்படைத் திருத்தத்தை இயக்கவும்.
    2. **AI மொழிநடை:** API அமைக்கப்பட்டிருந்தால் மட்டுமே AI திருத்தம் கிடைக்கும்.
    3. **ஆவண உருவாக்கம்:** ஆவண வகையைத் தேர்ந்தெடுத்து கிடைக்கும் விவரங்களை நிரப்பவும்.
    4. **சரிபார்ப்பு:** பெயர்கள், எண்கள், தேதிகள், சட்டக் குறிப்புகள், அரசாணை எண்கள் ஆகியவற்றைத் தனியாகச் சரிபார்க்கவும்.
    5. **பதிவிறக்கம்:** Word அல்லது TXT கோப்பைப் பதிவிறக்கவும்; HTML-ஐ PDF ஆக அச்சிடலாம்.

    **கவனம்:** இப்பதிப்பில் உள்ள விதிமுறை அடிப்படையிலான திருத்தங்கள் வரையறுக்கப்பட்ட எடுத்துக்காட்டு விதிகள் மட்டுமே. அவை முழுமையான தமிழ் இலக்கணச் சரிபார்ப்புக்கு மாற்றாகாது.
    """)
