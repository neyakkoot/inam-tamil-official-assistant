import streamlit as st
from inam.corrector import correct_text, convert_to_official_style
from inam.ai_assistant import improve_with_ai, ai_is_configured
from inam.documents import DOCUMENT_TYPES, build_document
from inam.exporters import make_docx, make_txt, make_html

st.set_page_config(page_title="இனம் – தமிழ் அலுவல் உதவி", page_icon="📝", layout="wide")
st.markdown("""<style>html,body,[class*="css"]{font-family:"Noto Sans Tamil","Latha",sans-serif}.block-container{max-width:1200px;padding-top:1.5rem}</style>""", unsafe_allow_html=True)
st.title("📝 இனம் – தமிழ் அலுவல் உதவி")
st.caption("Inam – Tamil Official Assistant · Version 1.1.0")
st.info("தொடக்கநிலை மொழித்திருத்த மாதிரி. பரிந்துரைகளைச் சரிபார்த்த பிறகே பயன்படுத்தவும்; இது முழுமையான தமிழ் இலக்கணச் சரிபார்ப்பி அல்ல.")

with st.sidebar:
    st.subheader("AI இணைப்பு")
    if ai_is_configured():
        st.success("AI API அமைக்கப்பட்டுள்ளது")
    else:
        st.warning("AI API அமைக்கப்படவில்லை. அடிப்படை விதிமுறைத் திருத்தம் இயங்கும்.")
    st.caption("ரகசிய அரசு ஆவணங்களை வெளிப்புற AI சேவைக்கு அனுப்ப வேண்டாம்.")

t1,t2,t3=st.tabs(["மொழித்திருத்தம்","அலுவல் ஆவணம்","வழிகாட்டி"])
with t1:
    source=st.text_area("திருத்த வேண்டிய உரை",height=200,placeholder="தமிழில் தட்டச்சு செய்யவும் அல்லது உரையை ஒட்டவும்...")
    a,b,c=st.columns(3)
    basic=a.button("எழுத்து / சொற்றொடர் திருத்தம்",type="primary",use_container_width=True)
    official=b.button("அலுவல் மொழிநடையாக மாற்று",use_container_width=True)
    ai=c.button("AI மூலம் மேம்படுத்து",disabled=not ai_is_configured(),use_container_width=True)
    if basic and source.strip():
        corrected, findings=correct_text(source)
        st.session_state["source"]=source
        st.session_state["corrected"]=corrected
        st.session_state["findings"]=findings
        st.session_state["official"]=None
    if official and source.strip():
        corrected, findings=correct_text(source)
        formal, notes=convert_to_official_style(corrected)
        st.session_state.update({"source":source,"corrected":corrected,"findings":findings,"official":formal,"style_notes":notes})
    if ai and source.strip():
        try:
            with st.spinner("AI பரிந்துரை உருவாக்கப்படுகிறது..."):
                corrected=improve_with_ai(source)
            st.session_state.update({"source":source,"corrected":corrected,"findings":[{"category":"AI பரிந்துரை","original":"முழு உரை","suggestion":"AI மூலம் மேம்படுத்தப்பட்டது","reason":"AI பரிந்துரை; உண்மைகள் மற்றும் பொருளை மனிதர் சரிபார்க்க வேண்டும்."}],"official":None})
        except Exception as e:
            st.error(f"AI சேவையை அணுக முடியவில்லை: {e}")
    if "corrected" in st.session_state:
        st.subheader("1. அசல் உரை")
        st.text_area("அசல் உரை",st.session_state["source"],height=110,disabled=True)
        st.subheader("2. திருத்தப்பட்ட உரை")
        corrected_edit=st.text_area("திருத்தப்பட்ட உரையைச் சரிபார்த்து மாற்றலாம்",st.session_state["corrected"],height=150,key="corrected_edit")
        st.download_button("திருத்தப்பட்ட உரை – TXT",make_txt(corrected_edit),"inam-corrected-tamil.txt","text/plain; charset=utf-8")
        st.subheader("கண்டறியப்பட்ட மாற்றங்கள் / பரிந்துரைகள்")
        for i,f in enumerate(st.session_state.get("findings",[]),1):
            with st.expander(f"{i}. {f['category']}"):
                st.write("**அசல்:** "+f["original"])
                st.write("**பரிந்துரை:** "+f["suggestion"])
                st.caption(f["reason"])
        if st.session_state.get("official") is not None:
            st.subheader("3. அலுவல் மொழிநடை வரைவு")
            formal_edit=st.text_area("அலுவல் மொழிநடையைச் சரிபார்க்கவும்",st.session_state["official"],height=150,key="formal_edit")
            st.download_button("அலுவல் மொழிநடை – TXT",make_txt(formal_edit),"inam-official-style.txt","text/plain; charset=utf-8")
            for n in st.session_state.get("style_notes",[]): st.caption("• "+n)

with t2:
    st.subheader("அலுவல் ஆவணம் உருவாக்குதல்")
    kind=st.selectbox("ஆவண வகை",list(DOCUMENT_TYPES.keys()))
    c1,c2=st.columns(2)
    office=c1.text_input("அலுவலகம் / துறை")
    recipient=c1.text_input("பெறுநர்")
    date=c1.text_input("நாள்")
    ref=c2.text_input("ந.க.எண் / குறிப்பு எண்")
    subject=c2.text_input("பொருள்")
    place=c2.text_input("இடம்")
    body=st.text_area("உள்ளடக்கம் / குறிப்புகள்",height=180)
    signer=st.text_input("கையொப்பமிடுபவர் / பதவி")
    if st.button("ஆவண வரைவை உருவாக்கு",type="primary"):
        st.session_state["doc"]=build_document(kind,office,recipient,date,ref,subject,body,place,signer)
    if "doc" in st.session_state:
        d=st.text_area("உருவாக்கப்பட்ட வரைவைத் திருத்தவும்",st.session_state["doc"],height=300,key="doc_edit")
        st.download_button("Word (.docx)",make_docx(d),"inam-official-document.docx","application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        st.download_button("TXT",make_txt(d),"inam-official-document.txt","text/plain; charset=utf-8")
        st.download_button("HTML (PDF அச்சிடலுக்கு)",make_html(d),"inam-official-document.html","text/html; charset=utf-8")
        st.caption("HTML கோப்பை உலாவியில் திறந்து Print → Save as PDF தேர்வு செய்யலாம்.")

with t3:
    st.markdown("""
- **எழுத்து / சொற்றொடர் திருத்தம்:** குறைந்த எண்ணிக்கையிலான நம்பகமான விதிகள் மட்டுமே.
- **அலுவல் மொழிநடை:** சில பொதுவான கோரிக்கைச் சொற்றொடர்களை மாற்றும் விருப்ப வசதி.
- **AI மேம்பாடு:** API Key அமைக்கப்பட்டால் மட்டும்.
- **ஆவண உருவாக்கம்:** எட்டு வகையான தொடக்க வரைவு வடிவங்கள்.
- **மனிதர் சரிபார்ப்பு:** பெயர்கள், எண்கள், தேதிகள், அரசாணை எண்கள், சட்டக் குறிப்புகள் ஆகியவற்றை மூலத்துடன் சரிபார்க்கவும்.

**வரம்பு:** ண/ந/ன, ல/ள/ழ, ர/ற போன்ற சூழல் சார்ந்த வேறுபாடுகளை இந்தப் பதிப்பு ஊகித்து தானாக மாற்றாது. தவறான தானியங்கி மாற்றத்தைத் தவிர்க்க அவை மாற்றமின்றி வைக்கப்படுகின்றன.
""")
