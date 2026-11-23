import streamlit as st
from io import BytesIO

from inam.corrector import correct_text, convert_to_official_style
from inam.ai_assistant import (
    improve_with_ai_detailed,
    ai_is_configured,
    get_ai_model,
    generate_document_from_template,
)
from inam.documents import DOCUMENT_TYPES, build_document
from inam.exporters import make_docx, make_txt, make_html
from inam.tamil_tools import (
    phonetic_to_tamil,
    convert_encoding,
    check_sandhi,
    suggest_tamil_words,
    lookup_dictionary,
    sort_tamil_lines,
    build_word_index,
    format_bibliography,
    number_to_tamil_words,
    tamil_words_to_number,
    TAMIL_DICTIONARY,
)

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
.tamil-kbd-btn button {
    font-size: 1.15rem !important;
    padding: 0.35rem 0.5rem !important;
}
</style>
""", unsafe_allow_html=True)

if "run_id" not in st.session_state:
    st.session_state["run_id"] = 0
if "doc_run_id" not in st.session_state:
    st.session_state["doc_run_id"] = 0
if "kbd_buffer" not in st.session_state:
    st.session_state["kbd_buffer"] = ""
if "bib_list" not in st.session_state:
    st.session_state["bib_list"] = []


def _clear_text_results():
    for k in ("source", "corrected", "findings", "official", "style_notes"):
        st.session_state.pop(k, None)


st.title("📝 இனம் – தமிழ் அலுவல் உதவி")
st.caption("Inam – Tamil Official Assistant & Language Workbench · Version 3.0.0")
st.info(
    "தமிழ்த் தட்டச்சு, குறியேற்ற மாற்றி (Bamini/TSCII/TAB/TAM), சொற்பிழை/சந்தித் திருத்தி, அகராதி, "
    "அகரவரிசைப்படுத்தல், சொல்லடைவு, துணைநூற்பட்டியல், எண்-எழுத்து மாற்றி ஆகியவை API இல்லாமல் நொடிப்பொழுதில் இயங்கும். "
    "ஆழமான இலக்கண ஆய்வுக்கும் மாதிரி ஆவண உருவாக்கத்திற்கும் Gemini AI பயன்படுத்தப்படும்."
)

with st.sidebar:
    st.subheader("அடிப்படை வசதிகள் (Offline)")
    st.success("12+ தமிழ் மொழிக் கருவிகள் – API தேவையில்லை")
    st.markdown("""
- தமிழ்த் தட்டச்சு விசைப்பலகை & ஒலிப்புத் தட்டச்சு
- ஒருங்குறி எழுத்துரு & குறியேற்ற மாற்றி (Bamini, TSCII, TAB, TAM)
- சொற்பிழை & சந்திப்பிழை திருத்தி
- தமிழ்ச்சொல் சுட்டி & தமிழ்-ஆங்கில அகராதி
- அகரவரிசைப்படுத்தம் & சொல்லடைவு
- துணைநூற்பட்டியல் & எண் ↔ எழுத்து மாற்றி
""")
    st.divider()
    st.subheader("விருப்பத்தேர்வு AI இணைப்பு")
    if ai_is_configured():
        st.success("Gemini API அமைக்கப்பட்டுள்ளது")
        st.caption(f"மாதிரி: {get_ai_model()}")
    else:
        st.warning("Gemini API Key அமைக்கப்படவில்லை")
    st.caption("ரகசிய ஆவணங்கள் மற்றும் தனிப்பட்ட விவரங்களை வெளிப்புற AI-க்கு அனுப்ப வேண்டாம்.")

tab_text, tab_typing, tab_lang_tools, tab_research, tab_docs, tab_guide = st.tabs([
    "மொழித்திருத்தம்",
    "தட்டச்சு & எழுத்துரு",
    "சொல் & அகராதி",
    "ஆய்வு & எண் மாற்றி",
    "அலுவல் ஆவணம்",
    "வழிகாட்டி",
])

# =========================================================
# தாவல் 1: மொழித்திருத்தம் (சொற்பிழை + சந்திப்பிழை + AI)
# =========================================================
with tab_text:
    st.subheader("தமிழ் உரையைத் திருத்துதல் (சொற்பிழை & சந்திப்பிழை)")
    source = st.text_area(
        "திருத்த வேண்டிய உரை",
        height=200,
        placeholder="தமிழில் தட்டச்சு செய்யவும்...",
        key="source_input",
        on_change=_clear_text_results,
    )
    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1.1, 0.6])
    basic_clicked = c1.button("எழுத்து / சொல் திருத்தம்", type="primary", use_container_width=True)
    sandhi_clicked = c2.button("சந்திப்பிழை திருத்தம்", use_container_width=True)
    official_clicked = c3.button("அலுவல் மொழிநடை", use_container_width=True)
    ai_clicked = c4.button("கலப்பின AI திருத்தம்", disabled=not ai_is_configured(), use_container_width=True)

    if c5.button("அழி", use_container_width=True):
        _clear_text_results()
        st.session_state["source_input"] = ""
        st.rerun()

    if basic_clicked:
        _clear_text_results()
        if source.strip():
            corrected, findings = correct_text(source)
            corrected, sandhi_notes = check_sandhi(corrected)
            for sn in sandhi_notes:
                findings.append({
                    "category": "சந்திப்பிழை",
                    "original": "நிலைமொழி + வருமொழி",
                    "suggestion": "வல்லினம் மிகுந்தது",
                    "reason": sn,
                })
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

    if sandhi_clicked:
        _clear_text_results()
        if source.strip():
            sandhi_fixed, sandhi_notes = check_sandhi(source)
            sandhi_findings = [
                {
                    "category": "சந்திப்பிழை திருத்தி",
                    "original": "வல்லினம் மிகா இடம்",
                    "suggestion": "வல்லினம் மிகுதல்",
                    "reason": note,
                }
                for note in sandhi_notes
            ]
            st.session_state["run_id"] += 1
            st.session_state.update(
                source=source,
                corrected=sandhi_fixed,
                findings=sandhi_findings,
                official=None,
                style_notes=[],
            )
        else:
            st.warning("முதலில் உரையை உள்ளிடவும்.")

    if official_clicked:
        _clear_text_results()
        if source.strip():
            corrected, findings = correct_text(source)
            corrected, _ = check_sandhi(corrected)
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
            rule_corrected, rule_findings = correct_text(source)
            rule_corrected, _ = check_sandhi(rule_corrected)
            try:
                with st.spinner("உருபனியல் ஆய்வு & Gemini AI பரிந்துரை உருவாக்கப்படுகிறது..."):
                    improved, ai_suggestions = improve_with_ai_detailed(rule_corrected, rule_findings)
                seen_originals = {r.get("original") for r in rule_findings}
                combined_findings = rule_findings + [
                    s for s in ai_suggestions if s.get("original") not in seen_originals
                ]
                if not combined_findings:
                    combined_findings = [{
                        "category": "Gemini AI ஆய்வு",
                        "original": "உள்ளீட்டு உரை",
                        "suggestion": "உரை செம்மைப்படுத்தப்பட்டது",
                        "reason": "எழுத்து, மயங்கொலி, சந்தி மற்றும் அலுவல் மொழிநடை சரிபார்க்கப்பட்டது.",
                    }]
                st.session_state["run_id"] += 1
                st.session_state.update(
                    source=source,
                    corrected=improved,
                    findings=combined_findings,
                    official=None,
                    style_notes=[],
                )
            except Exception:
                st.info("Gemini AI வழங்கி அதிகப் பயன்பாட்டில் உள்ளதால் உள்ளூர் திருத்த முடிவுகள் வழங்கப்பட்டுள்ளன.")
                st.session_state["run_id"] += 1
                st.session_state.update(
                    source=source,
                    corrected=rule_corrected,
                    findings=rule_findings,
                    official=None,
                    style_notes=[],
                )

    if "corrected" in st.session_state:
        rid = st.session_state["run_id"]
        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("1. அசல் உரை")
            st.text_area("அசல் உரை", value=st.session_state["source"], height=160, disabled=True, key=f"orig_{rid}")
        with col_b:
            st.subheader("2. திருத்தப்பட்ட உரை")
            corrected_edit = st.text_area("திருத்தப்பட்ட உரை", value=st.session_state["corrected"], height=160, key=f"corr_{rid}")
            st.download_button(
                "திருத்தப்பட்ட உரை – TXT",
                make_txt(corrected_edit),
                "inam-corrected-tamil.txt",
                "text/plain; charset=utf-8",
            )

        st.subheader("கண்டறியப்பட்ட மாற்றங்கள் / பரிந்துரைகள்")
        findings_list = st.session_state.get("findings", [])
        if not findings_list:
            st.info("எவ்வித எழுத்து / சந்திப் பிழையும் கண்டறியப்படவில்லை.")
        for i, item in enumerate(findings_list, 1):
            with st.expander(f"{i}. {item['category']} ({item['original']} → {item['suggestion']})", expanded=True):
                st.write("**அசல்:** " + item["original"])
                st.write("**பரிந்துரை:** " + item["suggestion"])
                st.caption(item["reason"])

        if st.session_state.get("official") is not None:
            st.subheader("3. அலுவல் மொழிநடை வரைவு")
            formal_edit = st.text_area("அலுவல் மொழிநடை", value=st.session_state["official"], height=160, key=f"form_{rid}")
            st.download_button(
                "அலுவல் மொழிநடை – TXT",
                make_txt(formal_edit),
                "inam-official-style.txt",
                "text/plain; charset=utf-8",
            )
            for note in st.session_state.get("style_notes", []):
                st.caption("• " + note)

# =========================================================
# தாவல் 2: தமிழ்த் தட்டச்சு, ஒலிப்புத் தட்டச்சு, எழுத்துரு, குறியேற்ற மாற்றி
# =========================================================
with tab_typing:
    t_sub1, t_sub2, t_sub3 = st.tabs([
        "ஒலிப்புத் தட்டச்சு & திரை விசைப்பலகை",
        "குறியேற்ற மாற்றி (Encoding)",
        "ஒருங்குறி எழுத்துருக்கள் (Unicode Fonts)",
    ])

    with t_sub1:
        st.subheader("ஒலிப்புத் தட்டச்சுக் கருவி (Phonetic Transliteration)")
        phonetic_in = st.text_input(
            "ஆங்கில எழுத்துகளில் தட்டச்சு செய்க (எ.கா: thamizh aluval uthavi)",
            placeholder="vanakkam thamizh...",
        )
        if phonetic_in:
            converted_tamil = phonetic_to_tamil(phonetic_in)
            st.success(f"**தமிழ் வெளியீடு:** {converted_tamil}")

        st.divider()
        st.subheader("தமிழ்த் தட்டச்சு விசைப்பலகை (On-Screen Tamil99 / Virtual Keyboard)")
        vowels = ["அ", "ஆ", "இ", "ஈ", "உ", "ஊ", "எ", "ஏ", "ஐ", "ஒ", "ஓ", "ஔ", "ஃ"]
        consonants = ["க", "ங", "ச", "ஞ", "ட", "ண", "த", "ந", "ப", "ம", "ய", "ர", "ல", "வ", "ழ", "ள", "ற", "ன"]
        signs = ["ா", "ி", "ீ", "ு", "ூ", "ெ", "ே", "ை", "ொ", "ோ", "ௌ", "்"]

        st.caption("உயிரெழுத்துகள்")
        v_cols = st.columns(len(vowels))
        for idx, ch in enumerate(vowels):
            if v_cols[idx].button(ch, key=f"v_{idx}"):
                st.session_state["kbd_buffer"] += ch

        st.caption("மெய்யெழுத்துகள்")
        c_cols = st.columns(9)
        for idx, ch in enumerate(consonants):
            if c_cols[idx % 9].button(ch, key=f"c_{idx}"):
                st.session_state["kbd_buffer"] += ch

        st.caption("உயிர்மெய்க் குறியீடுகள் & புள்ளி")
        s_cols = st.columns(len(signs))
        for idx, ch in enumerate(signs):
            if s_cols[idx].button(ch, key=f"s_{idx}"):
                st.session_state["kbd_buffer"] += ch

        k1, k2, k3 = st.columns([1, 1, 1])
        if k1.button("இடைவெளி (Space)", use_container_width=True):
            st.session_state["kbd_buffer"] += " "
        if k2.button("பின்னழி (Backspace)", use_container_width=True):
            st.session_state["kbd_buffer"] = st.session_state["kbd_buffer"][:-1]
        if k3.button("முழுவதும் அழி", use_container_width=True):
            st.session_state["kbd_buffer"] = ""

        kbd_text = st.text_area("விசைப்பலகை உரைப் பெட்டி", value=st.session_state["kbd_buffer"], height=120)
        st.session_state["kbd_buffer"] = kbd_text

    with t_sub2:
        st.subheader("குறியேற்ற மாற்றி (Encoding Converter)")
        enc_mode = st.selectbox(
            "மாற்றும் வகை",
            [
                "Bamini (பாமினி) -> Unicode (ஒருங்குறி)",
                "Unicode -> Bamini (பாமினி)",
                "TSCII -> Unicode (ஒருங்குறி)",
                "Unicode -> TSCII",
                "TAB -> Unicode (ஒருங்குறி)",
                "Unicode -> TAB",
                "TAM -> Unicode (ஒருங்குறி)",
                "Unicode -> TAM",
            ],
        )
        enc_input = st.text_area("மாற்ற வேண்டிய உரையை ஒட்டவும்", height=140, key="enc_in")
        if st.button("குறியேற்றம் மாற்று", type="primary"):
            if enc_input.strip():
                enc_out = convert_encoding(enc_input, enc_mode)
                st.text_area("மாற்றப்பட்ட உரை", value=enc_out, height=140)
            else:
                st.warning("உரையை உள்ளிடவும்.")

    with t_sub3:
        st.subheader("ஒருங்குறி எழுத்துருக்கள் (Unicode Fonts Preview & Guide)")
        selected_font = st.selectbox(
            "எழுத்துருவைத் தேர்ந்தெடுக்கவும்",
            ["Marutham", "Noto Sans Tamil", "Noto Serif Tamil", "Latha", "Vijaya", "Kavivanar"],
        )
        preview_sample = st.text_input(
            "மாதிரி உரை",
            value="யாதும் ஊரே யாவரும் கேளிர் – தமிழ் இணையக் கல்விக் கழகம்",
        )
        st.markdown(
            f'<div style="font-family: \'{selected_font}\', sans-serif; font-size: 24px; '
            f'padding: 16px; border: 1px solid #ddd; border-radius: 8px;">{preview_sample}</div>',
            unsafe_allow_html=True,
        )
        st.caption("அரசு மற்றும் கல்வி நிறுவன அலுவல் ஆவணங்களுக்குத் தமிழ்நாடு அரசின் 'Marutham' அல்லது 'Noto Sans Tamil' ஒருங்குறி எழுத்துருக்களைப் பயன்படுத்துவது சிறந்தது.")

# =========================================================
# தாவல் 3: தமிழ்ச்சொல் சுட்டி, அகராதி, அகரவரிசைப்படுத்தல்
# =========================================================
with tab_lang_tools:
    col_l1, col_l2 = st.columns(2)

    with col_l1:
        st.subheader("தமிழ்ச்சொல் சுட்டி (Tamil Word Suggester)")
        prefix_query = st.text_input("தொடக்க எழுத்துகளை உள்ளிடவும் (எ.கா: அலு, சுற், ஆவ)")
        if prefix_query:
            suggestions = suggest_tamil_words(prefix_query)
            if suggestions:
                for w in suggestions:
                    st.write(f"• **{w}** — {TAMIL_DICTIONARY[w]['meaning']}")
            else:
                st.info("பொருந்தும் சொற்கள் கிடைக்கவில்லை.")

        st.divider()
        st.subheader("தமிழ் - ஆங்கில அலுவல் அகராதி (Dictionary)")
        dict_query = st.text_input("தமிழ் அல்லது ஆங்கிலச் சொல்லை உள்ளிடவும் (எ.கா: அரசாணை, Circular)", key="dict_q")
        if dict_query:
            res = lookup_dictionary(dict_query)
            if isinstance(res, dict) and "meaning" in res:
                st.success(f"**பொருள்:** {res['meaning']}")
                st.write("**ஆங்கிலம்:** " + res.get("english", ""))
                st.write("**இணைச்சொற்கள்:** " + ", ".join(res["synonyms"]))
            elif isinstance(res, dict):
                for k, v in res.items():
                    st.write(
                        f"**{k}** ({v.get('english', '')}): {v['meaning']} "
                        f"*(இணைச்சொற்கள்: {', '.join(v['synonyms'])})*"
                    )
            else:
                st.warning("இச்சொல் உள்ளூர் அகராதியில் இல்லை.")

    with col_l2:
        st.subheader("அகரவரிசைப்படுத்தம் (Tamil Alphabetical Sorting)")
        sort_input = st.text_area(
            "வரிசைப்படுத்த வேண்டிய சொற்கள் / பெயர்களை வரிக்கு ஒன்றாக உள்ளிடவும்",
            height=220,
            placeholder="கபிலர்\nஅவ்வையார்\nதிருவள்ளுவர்\nஇளங்கோவடிகள்",
        )
        sort_order = st.radio("வரிசை முறை", ["அ → ன (ஏறுவரிசை)", "ன → அ (இறங்குவரிசை)"], horizontal=True)
        if st.button("அகரவரிசைப்படுத்து", type="primary"):
            if sort_input.strip():
                sorted_lines = sort_tamil_lines(
                    sort_input.splitlines(),
                    reverse=(sort_order == "ன → அ (இறங்குவரிசை)"),
                )
                st.text_area("அகரவரிசைப்படுத்தப்பட்ட பட்டியல்", value="\n".join(sorted_lines), height=200)
            else:
                st.warning("வரிசைப்படுத்த வேண்டிய வரிகளை உள்ளிடவும்.")

# =========================================================
# தாவல் 4: சொல்லடைவு, துணைநூற்பட்டியல், எண் <-> எழுத்து மாற்றி
# =========================================================
with tab_research:
    r_sub1, r_sub2, r_sub3 = st.tabs([
        "சொல்லடைவு (Indexing)",
        "துணைநூற்பட்டியல் கருவி (Bibliography)",
        "எண் ↔ எழுத்து மாற்றி",
    ])

    with r_sub1:
        st.subheader("சொல்லடைவு உருவாக்கி (Word Indexer / Concordance)")
        idx_text = st.text_area("சொல்லடைவு உருவாக்க வேண்டிய உரையை உள்ளிடவும்", height=180, key="idx_text")
        min_len = st.slider("குறைந்தபட்ச எழுத்து எண்ணிக்கை", 1, 6, 2)
        if st.button("சொல்லடைவு உருவாக்கு", type="primary"):
            if idx_text.strip():
                rows = build_word_index(idx_text, min_length=min_len)
                st.write(f"**மொத்தத் தனித்த தமிழ்ச் சொற்கள்:** {len(rows)}")
                st.dataframe(rows, use_container_width=True)
            else:
                st.warning("உரையை உள்ளிடவும்.")

    with r_sub2:
        st.subheader("துணைநூற்பட்டியல் கருவி (Bibliography Generator)")
        b_col1, b_col2 = st.columns(2)
        bib_author = b_col1.text_input("ஆசிரியர் பெயர் (எ.கா: முனைவர் த. சத்தியராஜ்)")
        bib_title = b_col1.text_input("நூல் / கட்டுரைத் தலைப்பு")
        bib_publisher = b_col2.text_input("பதிப்பகம் / ஆய்விதழ் (எ.கா: இனம் பதிப்பகம்)")
        bib_place = b_col2.text_input("வெளியீட்டு இடம் (எ.கா: கோயம்புத்தூர்)")
        bib_year = b_col1.text_input("ஆண்டு (எ.கா: 2026)")
        bib_style = b_col2.selectbox(
            "மேற்கோள் நடை",
            ["தமிழ் ஆய்வு நடை (Inam Style)", "APA 7th Style", "MLA 9th Style"],
        )
        if st.button("பட்டியலில் சேர்", type="primary"):
            if bib_author and bib_title and bib_year:
                entry = format_bibliography(bib_author, bib_year, bib_title, bib_publisher, bib_place, bib_style)
                st.session_state["bib_list"].append(entry)
            else:
                st.warning("ஆசிரியர், தலைப்பு, ஆண்டு ஆகியவற்றைக் கட்டாயம் உள்ளிடவும்.")

        if st.session_state["bib_list"]:
            st.divider()
            st.subheader("உருவாக்கப்பட்ட துணைநூற்பட்டியல்")
            sorted_bib = sort_tamil_lines(st.session_state["bib_list"])
            for idx, item in enumerate(sorted_bib, 1):
                st.markdown(f"{idx}. {item}")
            st.download_button(
                "துணைநூற்பட்டியல் – TXT",
                make_txt("\n".join(sorted_bib)),
                "inam-bibliography.txt",
                "text/plain; charset=utf-8",
            )
            if st.button("பட்டியலை அழி"):
                st.session_state["bib_list"] = []
                st.rerun()

    with r_sub3:
        st.subheader("எண் ↔ எழுத்து மாற்றி (Number ↔ Tamil Words)")
        n_col1, n_col2 = st.columns(2)
        with n_col1:
            num_val = st.number_input("எண்ணை உள்ளிடவும்", min_value=0, max_value=999_999_999, value=2026, step=1)
            st.success(f"**தமிழ் எழுத்தில்:** {number_to_tamil_words(int(num_val))}")

        with n_col2:
            word_val = st.text_input(
                "தமிழ் எண்ணுப் பெயரை உள்ளிடவும்",
                value="இரண்டு ஆயிரத்து இருபத்து ஆறு",
            )
            if word_val.strip():
                parsed_num = tamil_words_to_number(word_val)
                st.info(f"**எண் வடிவில்:** {parsed_num:,}")

# =========================================================
# தாவல் 5: அலுவல் ஆவணம்
# =========================================================
with tab_docs:
    st.subheader("மாதிரி அலுவல் கோப்பைப் பின்பற்றி புதிய ஆவணம்")
    st.write(
        "சுற்றறிக்கை, அலுவல் கடிதம், குறிப்பாணை, அரசாணை, பாராட்டுக் கடிதம் போன்ற மாதிரி "
        "DOCX, PDF அல்லது TXT கோப்பைப் பதிவேற்றுங்கள்."
    )

    kind = st.selectbox("புதிய ஆவண வகை", list(DOCUMENT_TYPES.keys()))
    sample_file = st.file_uploader(
        "மாதிரி அலுவல் கோப்பைப் பதிவேற்றவும்",
        type=["docx", "pdf", "txt"],
        key="official_template_upload",
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

    if st.button(
        "பதிவேற்றிய மாதிரியைப் பின்பற்றி Gemini AI மூலம் உருவாக்கு",
        type="primary",
        disabled=(not ai_is_configured() or sample_file is None),
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

    st.divider()
    st.subheader("AI இல்லாத அடிப்படை ஆவண உருவாக்கம்")
    with st.expander("விவரங்களை நிரப்பி அடிப்படை வரைவை உருவாக்க"):
        basic_kind = st.selectbox("அடிப்படை ஆவண வகை", list(DOCUMENT_TYPES.keys()), key="basic_kind")
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
                basic_ref, basic_subject, basic_body, basic_place, basic_sign,
            )
            st.session_state["doc_run_id"] += 1

    if "doc" in st.session_state:
        drid = st.session_state["doc_run_id"]
        st.subheader("உருவாக்கப்பட்ட ஆவணம்")
        document_edit = st.text_area("வரைவைத் திருத்தவும்", value=st.session_state["doc"], height=320, key=f"doc_edit_{drid}")
        st.download_button(
            "Word (.docx)",
            make_docx(document_edit),
            "inam-official-document.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        st.download_button("TXT", make_txt(document_edit), "inam-official-document.txt", "text/plain; charset=utf-8")
        st.download_button("HTML (PDF அச்சிடலுக்கு)", make_html(document_edit), "inam-official-document.html", "text/html; charset=utf-8")

# =========================================================
# தாவல் 6: வழிகாட்டி
# =========================================================
with tab_guide:
    st.subheader("பயன்பாட்டு வழிகாட்டி – இனம் 3.0")
    st.markdown("""
- **மொழித்திருத்தம்:** சொற்பிழை, மயங்கொலிப் பிழை, வல்லினம் மிகும் சந்திப்பிழை ஆகியவற்றை API இல்லாமலேயே உடனடியாகத் திருத்தலாம்.
- **தட்டச்சு & எழுத்துரு:** ஒலிப்புத் தட்டச்சு (Phonetic), திரைத் தமிழ் விசைப்பலகை, Bamini / TSCII / TAB / TAM ↔ Unicode குறியேற்ற மாற்றி மற்றும் ஒருங்குறி எழுத்துரு மாதிரிகளைப் பயன்படுத்தலாம்.
- **சொல் & அகராதி:** தமிழ்ச்சொல் சுட்டி, தமிழ்-ஆங்கில அலுவல் அகராதி, தமிழ் அகர வரிசைப்படுத்தம் ஆகியவை உள்ளடக்கப்பட்டுள்ளன.
- **ஆய்வு & எண் மாற்றி:** ஆய்வுக் கட்டுரைகளுக்கான சொல்லடைவு (Indexing), துணைநூற்பட்டியல் (Bibliography), எண் ↔ தமிழ் எழுத்து மாற்றி ஆகியவை இடம்பெற்றுள்ளன.
- **அலுவல் ஆவணம்:** மாதிரி DOCX/TXT/PDF கோப்புகளைப் பின்பற்றி Gemini AI மூலம் புதிய அலுவல் ஆவணங்களை உருவாக்கலாம்.
""")
