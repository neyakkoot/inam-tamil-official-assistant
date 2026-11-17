import streamlit as st

from inam.corrector import correct_text, convert_to_official_style
from inam.ai_assistant import improve_with_ai, ai_is_configured, get_ai_model
from inam.documents import DOCUMENT_TYPES, build_document
from inam.exporters import make_docx, make_txt, make_html

st.set_page_config(
    page_title="இனம் – தமிழ் அலுவல் உதவி",
    page_icon="📝",
    layout="wide",
)

st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: "Noto Sans Tamil", "Latha", sans-serif;
    }
    .block-container {
        max-width: 1200px;
        padding-top: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📝 இனம் – தமிழ் அலுவல் உதவி")
st.caption("Inam – Tamil Official Assistant · Version 2.0.0")
st.info(
    "தமிழ் உரைத் திருத்தம் மற்றும் அலுவல் ஆவண உருவாக்கம் API இல்லாமலேயே இயங்கும். "
    "AI மேம்பாடு மட்டும் விருப்பத்தேர்வாக Gemini API மூலம் செயல்படும்."
)

with st.sidebar:
    st.subheader("அடிப்படை வசதிகள்")
    st.success("API தேவையில்லை – எப்போதும் கிடைக்கும்")
    st.caption(
        "தமிழ் உரைத் திருத்தம், அலுவல் மொழிநடை விதிகள், "
        "ஆவண உருவாக்கம் மற்றும் பதிவிறக்கம்."
    )

    st.divider()
    st.subheader("விருப்பத்தேர்வு AI இணைப்பு")
    if ai_is_configured():
        st.success("Gemini API அமைக்கப்பட்டுள்ளது")
        st.caption(f"மாதிரி: {get_ai_model()}")
    else:
        st.warning("Gemini API Key அமைக்கப்படவில்லை")
        st.caption(
            "AI பொத்தான் முடக்கப்பட்டிருக்கும். "
            "மற்ற அனைத்து அடிப்படை வசதிகளும் இயங்கும்."
        )
    st.caption(
        "ரகசிய அரசு ஆவணங்கள், தனிப்பட்ட மாணவர் விவரங்கள், "
        "கடவுச்சொற்கள் போன்றவற்றை வெளிப்புற AI சேவைக்கு அனுப்ப வேண்டாம்."
    )

tab_text, tab_docs, tab_guide = st.tabs(
    ["மொழித்திருத்தம்", "அலுவல் ஆவணம்", "வழிகாட்டி"]
)

with tab_text:
    st.subheader("தமிழ் உரையைத் திருத்துதல்")
    source = st.text_area(
        "திருத்த வேண்டிய உரை",
        height=200,
        placeholder="தமிழில் தட்டச்சு செய்யவும் அல்லது உரையை ஒட்டவும்...",
        key="source_input",
    )

    col1, col2, col3 = st.columns(3)
    basic_clicked = col1.button(
        "எழுத்து / சொற்றொடர் திருத்தம்",
        type="primary",
        use_container_width=True,
    )
    official_clicked = col2.button(
        "அலுவல் மொழிநடையாக மாற்று",
        use_container_width=True,
    )
    ai_clicked = col3.button(
        "Gemini AI மூலம் மேம்படுத்து",
        disabled=not ai_is_configured(),
        use_container_width=True,
    )

    if basic_clicked:
        if not source.strip():
            st.warning("முதலில் திருத்த வேண்டிய உரையை உள்ளிடவும்.")
        else:
            corrected, findings = correct_text(source)
            st.session_state["source"] = source
            st.session_state["corrected"] = corrected
            st.session_state["findings"] = findings
            st.session_state["official"] = None
            st.session_state["style_notes"] = []

    if official_clicked:
        if not source.strip():
            st.warning("முதலில் மாற்ற வேண்டிய உரையை உள்ளிடவும்.")
        else:
            corrected, findings = correct_text(source)
            formal, notes = convert_to_official_style(corrected)
            st.session_state.update(
                {
                    "source": source,
                    "corrected": corrected,
                    "findings": findings,
                    "official": formal,
                    "style_notes": notes,
                }
            )

    if ai_clicked:
        if not source.strip():
            st.warning("முதலில் மேம்படுத்த வேண்டிய உரையை உள்ளிடவும்.")
        else:
            try:
                with st.spinner("Gemini AI பரிந்துரை உருவாக்கப்படுகிறது..."):
                    improved = improve_with_ai(source)
                st.session_state.update(
                    {
                        "source": source,
                        "corrected": improved,
                        "findings": [
                            {
                                "category": "Gemini AI பரிந்துரை",
                                "original": "உள்ளீட்டு உரை",
                                "suggestion": "AI மூலம் மேம்படுத்தப்பட்டது",
                                "reason": (
                                    "AI பரிந்துரை மட்டுமே. பெயர்கள், எண்கள், "
                                    "தேதிகள் மற்றும் உண்மைகளை மனிதர் சரிபார்க்க வேண்டும்."
                                ),
                            }
                        ],
                        "official": None,
                        "style_notes": [],
                    }
                )
            except Exception as exc:
                st.error(f"AI சேவையை அணுக முடியவில்லை: {exc}")

    if "corrected" in st.session_state:
        st.divider()
        st.subheader("1. அசல் உரை")
        st.text_area(
            "அசல் உரை",
            st.session_state["source"],
            height=110,
            disabled=True,
            key="original_output",
        )

        st.subheader("2. திருத்தப்பட்ட உரை")
        corrected_edit = st.text_area(
            "திருத்தப்பட்ட உரையைச் சரிபார்த்து மாற்றலாம்",
            st.session_state["corrected"],
            height=160,
            key="corrected_edit",
        )
        st.download_button(
            "திருத்தப்பட்ட உரை – TXT",
            make_txt(corrected_edit),
            "inam-corrected-tamil.txt",
            "text/plain; charset=utf-8",
        )

        st.subheader("கண்டறியப்பட்ட மாற்றங்கள் / பரிந்துரைகள்")
        findings = st.session_state.get("findings", [])
        if findings:
            for index, finding in enumerate(findings, 1):
                with st.expander(f"{index}. {finding['category']}"):
                    st.write("**அசல்:** " + finding["original"])
                    st.write("**பரிந்துரை:** " + finding["suggestion"])
                    st.caption(finding["reason"])

        if st.session_state.get("official") is not None:
            st.subheader("3. அலுவல் மொழிநடை வரைவு")
            formal_edit = st.text_area(
                "அலுவல் மொழிநடையைச் சரிபார்க்கவும்",
                st.session_state["official"],
                height=160,
                key="formal_edit",
            )
            st.download_button(
                "அலுவல் மொழிநடை – TXT",
                make_txt(formal_edit),
                "inam-official-style.txt",
                "text/plain; charset=utf-8",
            )
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
    body = st.text_area("உள்ளடக்கம் / குறிப்புகள்", height=180)
    signatory = st.text_input("கையொப்பமிடுபவர் / பதவி")

    if st.button("ஆவண வரைவை உருவாக்கு", type="primary"):
        st.session_state["doc"] = build_document(
            kind,
            office,
            recipient,
            date,
            reference,
            subject,
            body,
            place,
            signatory,
        )

    if "doc" in st.session_state:
        document_edit = st.text_area(
            "உருவாக்கப்பட்ட வரைவைத் திருத்தவும்",
            st.session_state["doc"],
            height=300,
            key="doc_edit",
        )
        st.download_button(
            "Word (.docx)",
            make_docx(document_edit),
            "inam-official-document.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        st.download_button(
            "TXT",
            make_txt(document_edit),
            "inam-official-document.txt",
            "text/plain; charset=utf-8",
        )
        st.download_button(
            "HTML (PDF அச்சிடலுக்கு)",
            make_html(document_edit),
            "inam-official-document.html",
            "text/html; charset=utf-8",
        )
        st.caption(
            "HTML கோப்பை உலாவியில் திறந்து Print → Save as PDF தேர்வு செய்யலாம்."
        )

with tab_guide:
    st.subheader("பயன்பாட்டு வழிகாட்டி")
    st.markdown(
        """
- **எழுத்து / சொற்றொடர் திருத்தம்:** உள்ளமைக்கப்பட்ட தமிழ் விதிகள் மூலம் இயங்கும்; API தேவையில்லை.
- **அலுவல் மொழிநடை:** உள்ளமைக்கப்பட்ட அலுவல் மொழி விதிகள் மூலம் இயங்கும்; API தேவையில்லை.
- **Gemini AI மேம்பாடு:** Gemini API Key அமைக்கப்பட்டால் மட்டுமே செயல்படும்.
- **ஆவண உருவாக்கம்:** எட்டு வகையான அலுவல் ஆவணங்களுக்கான தொடக்க வரைவு வடிவங்கள்.
- **பதிவிறக்கம்:** Word, TXT மற்றும் HTML வடிவங்கள்; API தேவையில்லை.

### முக்கிய வரம்புகள்
- இந்த விதிமுறைத் திருத்தம் முழுமையான தமிழ் இலக்கணச் சரிபார்ப்பி அல்ல.
- ண/ந/ன, ல/ள/ழ, ர/ற போன்ற சூழல் சார்ந்த வேறுபாடுகளை ஊகித்து மாற்றாது.
- உருவாக்கப்படும் அலுவல் ஆவணங்கள் தொடக்க வரைவு மட்டுமே.
- பெயர்கள், எண்கள், தேதிகள், அரசாணை எண்கள் மற்றும் சட்டக் குறிப்புகளை மூல ஆவணத்துடன் சரிபார்க்க வேண்டும்.
- Gemini இலவச API பயன்பாட்டிற்கு Google விதிக்கும் மாதிரி சார்ந்த பயன்பாட்டு வரம்புகள் பொருந்தும்.
"""
    )
