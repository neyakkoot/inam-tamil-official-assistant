import streamlit as st
import streamlit.components.v1 as components
from io import BytesIO

from inam.corrector import correct_text, convert_to_official_style
from inam.ai_assistant import (
    improve_with_ai_detailed,
    ai_is_configured,
    get_ai_model,
    generate_document_from_template,
    transcribe_tamil_audio,
    format_voice_to_document,
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
if "stt_result" not in st.session_state:
    st.session_state["stt_result"] = ""
if "voice_formatted_doc" not in st.session_state:
    st.session_state["voice_formatted_doc"] = ""


def _clear_text_results():
    for k in ("source", "corrected", "findings", "official", "style_notes"):
        st.session_state.pop(k, None)


def _render_live_voice_typing_board():
    """பேசும்போதே உடனுக்குடன் தட்டச்சாகும் நவீன குரல் தட்டச்சுப் பலகை."""
    html_code = """
    <!DOCTYPE html>
    <html lang="ta">
    <head>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; font-family: 'Marutham', 'Noto Sans Tamil', 'Latha', sans-serif; }
        body { margin: 0; padding: 4px; background: transparent; }
        .board-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 4px 16px rgba(15, 23, 42, 0.06);
        }
        .board-header {
            text-align: center;
            margin-bottom: 14px;
        }
        .board-title {
            font-size: 22px;
            font-weight: 700;
            color: #1e3a8a;
            margin: 0 0 4px 0;
        }
        .board-sub {
            font-size: 13.5px;
            color: #475569;
            margin: 0;
        }
        .toolbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 12px;
        }
        .lang-group {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            font-weight: 600;
            color: #1e293b;
        }
        select {
            padding: 6px 12px;
            border-radius: 8px;
            border: 1px solid #cbd5e1;
            font-size: 14px;
            background: #f8fafc;
            cursor: pointer;
        }
        .status-pill {
            padding: 6px 14px;
            border-radius: 999px;
            font-size: 13px;
            font-weight: 600;
            background: #f1f5f9;
            color: #475569;
            border: 1px solid #e2e8f0;
            transition: all 0.2s ease;
        }
        .status-pill.listening {
            background: #dcfce7;
            color: #15803d;
            border-color: #86efac;
        }
        .status-pill.error {
            background: #fee2e2;
            color: #b91c1c;
            border-color: #fca5a5;
        }
        .editor-wrap {
            position: relative;
            border: 1.5px solid #cbd5e1;
            border-radius: 12px;
            background: #ffffff;
            padding: 12px 12px 12px 64px;
            transition: border-color 0.2s;
        }
        .editor-wrap:focus-within {
            border-color: #2563eb;
        }
        .mic-btn {
            position: absolute;
            top: 14px;
            left: 12px;
            width: 42px;
            height: 42px;
            border-radius: 50%;
            border: none;
            background: #2563eb;
            color: #ffffff;
            font-size: 19px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 3px 10px rgba(37, 99, 235, 0.35);
            transition: all 0.2s ease;
        }
        .mic-btn:hover { transform: scale(1.05); }
        .mic-btn.recording {
            background: #dc2626;
            box-shadow: 0 0 0 6px rgba(220, 38, 38, 0.2);
            animation: pulse 1.3s infinite;
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.45); }
            70% { box-shadow: 0 0 0 10px rgba(220, 38, 38, 0); }
            100% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); }
        }
        textarea {
            width: 100%;
            min-height: 15px;
            border: none;
            outline: none;
            resize: vertical;
            font-size: 17px;
            line-height: 1.65;
            color: #0f172a;
            background: transparent;
        }
        .footer-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
            font-size: 13px;
        }
        .counters {
            color: #2563eb;
            font-weight: 600;
        }
        .actions {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .action-btn {
            border: 1px solid #cbd5e1;
            background: #f8fafc;
            color: #1e293b;
            padding: 5px 12px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
        }
        .action-btn:hover { background: #e2e8f0; }
        .action-btn.danger {
            color: #dc2626;
            border-color: #fecaca;
            background: #fef2f2;
        }
        .action-btn.danger:hover { background: #fee2e2; }
    </style>
    </head>
    <body>
    <div class="board-card">
        <div class="board-header">
            <h3 class="board-title">குரல் தட்டச்சுப் பலகை (Live Voice Typing)</h3>
            <p class="board-sub">பேசுங்கள்... உடனுக்குடன் துல்லியமான ஒருங்குறி (Unicode) உரையாக மாறும்</p>
        </div>

        <div class="toolbar">
            <div class="lang-group">
                <label for="langSelect">மொழி:</label>
                <select id="langSelect" onchange="changeLang()">
                    <option value="ta-IN" selected>தமிழ் (Tamil - India)</option>
                    <option value="ta-SG">தமிழ் (Singapore)</option>
                    <option value="ta-LK">தமிழ் (Sri Lanka)</option>
                    <option value="en-IN">English (India)</option>
                </select>
            </div>
            <div id="statusPill" class="status-pill">● தயார்</div>
        </div>

        <div class="editor-wrap">
            <button id="micBtn" class="mic-btn" onclick="toggleMic()" title="மைக் குறியீட்டை அழுத்திப் பேசத் தொடங்குங்கள்">🎙️</button>
            <textarea id="voiceText" oninput="syncManualEdit()" placeholder="இங்குள்ள மைக் குறியீட்டை அழுத்திப் பேசத் தொடங்குங்கள்..."></textarea>
        </div>

        <div class="footer-bar">
            <div class="counters">
                சொற்கள்: <span id="wordCount">0</span> &nbsp;|&nbsp; எழுத்துக்கள்: <span id="charCount">0</span>
            </div>
            <div class="actions">
                <button class="action-btn" onclick="copyText()">📋 நகலெடு (கீழே ஒட்ட)</button>
                <button class="action-btn" onclick="downloadTxt()">⬇️ TXT பதிவிறக்கு</button>
                <button class="action-btn danger" onclick="clearText()">🗑️ உரையை அழி</button>
            </div>
        </div>
    </div>

    <script>
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const micBtn = document.getElementById("micBtn");
        const statusPill = document.getElementById("statusPill");
        const voiceText = document.getElementById("voiceText");
        const langSelect = document.getElementById("langSelect");
        const wordCountEl = document.getElementById("wordCount");
        const charCountEl = document.getElementById("charCount");

        let recognition = null;
        let isListening = false;
        let committedText = "";

        function updateCounters() {
            const val = voiceText.value;
            charCountEl.innerText = val.length;
            const trimmed = val.trim();
            wordCountEl.innerText = trimmed ? trimmed.split(/\\s+/).length : 0;
        }

        function syncManualEdit() {
            committedText = voiceText.value;
            updateCounters();
        }

        function setStatus(text, mode) {
            statusPill.innerText = text;
            statusPill.className = "status-pill" + (mode ? " " + mode : "");
        }

        if (SpeechRecognition) {
            recognition = new SpeechRecognition();
            recognition.lang = "ta-IN";
            recognition.continuous = true;
            recognition.interimResults = true;

            recognition.onstart = () => {
                isListening = true;
                micBtn.classList.add("recording");
                setStatus("● கேட்கிறது... பேசுங்கள்", "listening");
            };

            recognition.onresult = (event) => {
                let interimTranscript = "";
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const piece = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        const needsSpace = committedText && !committedText.endsWith(" ") && !committedText.endsWith("\\n");
                        committedText += (needsSpace ? " " : "") + piece.trim();
                    } else {
                        interimTranscript += piece;
                    }
                }
                const spacer = (committedText && interimTranscript && !committedText.endsWith(" ")) ? " " : "";
                voiceText.value = committedText + spacer + interimTranscript;
                voiceText.scrollTop = voiceText.scrollHeight;
                updateCounters();
            };

            recognition.onerror = (event) => {
                if (event.error === "no-speech") {
                    return;
                }
                isListening = false;
                micBtn.classList.remove("recording");
                if (event.error === "not-allowed") {
                    setStatus("⚠️ மைக் அனுமதி மறுக்கப்பட்டது (Browser Settings-இல் அனுமதிக்கவும்)", "error");
                } else {
                    setStatus("⚠️ பிழை: " + event.error, "error");
                }
            };

            recognition.onend = () => {
                if (isListening) {
                    try {
                        recognition.start();
                    } catch (e) {}
                } else {
                    micBtn.classList.remove("recording");
                    setStatus("● தயார்", "");
                }
            };
        } else {
            micBtn.disabled = true;
            setStatus("⚠️ Chrome அல்லது Edge உலாவியைப் பயன்படுத்தவும்", "error");
        }

        function toggleMic() {
            if (!recognition) return;
            if (isListening) {
                isListening = false;
                recognition.stop();
                micBtn.classList.remove("recording");
                setStatus("● நிறுத்தப்பட்டது", "");
            } else {
                committedText = voiceText.value;
                recognition.lang = langSelect.value;
                try {
                    recognition.start();
                } catch (e) {}
            }
        }

        function changeLang() {
            if (recognition) {
                recognition.lang = langSelect.value;
                if (isListening) {
                    recognition.stop();
                }
            }
        }

        function copyText() {
            if (!voiceText.value) return;
            navigator.clipboard.writeText(voiceText.value).then(() => {
                setStatus("📋 உரை நகலெடுக்கப்பட்டது! கீழே உள்ள பெட்டியில் ஒட்டவும்", "listening");
                setTimeout(() => {
                    if (isListening) setStatus("● கேட்கிறது... பேசுங்கள்", "listening");
                    else setStatus("● தயார்", "");
                }, 2200);
            });
        }

        function downloadTxt() {
            if (!voiceText.value.trim()) return;
            const blob = new Blob([voiceText.value], { type: "text/plain;charset=utf-8" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "inam-voice-typing.txt";
            a.click();
            URL.revokeObjectURL(url);
        }

        function clearText() {
            committedText = "";
            voiceText.value = "";
            updateCounters();
            if (!isListening) setStatus("● தயார்", "");
        }
    </script>
    </body>
    </html>
    """
    components.html(html_code, height=)


st.title("📝 இனம் – தமிழ் அலுவல் உதவி")
st.caption("Inam – Tamil Official Assistant & Language Workbench · Version 3.4.0")
st.info(
    "பேசும்போதே உடனுக்குடன் தட்டச்சாகும் குரல் தட்டச்சுப் பலகை, குரல் செய்தியைச் சுற்றறிக்கை / பரப்புரை அறிக்கை / "
    "அரசு அறிக்கை வடிவங்களில் சொல்லாய்வி (Word .docx) ஆவணமாகப் பதிவிறக்கும் வசதி, குறியேற்ற மாற்றி, "
    "சொற்பிழை/சந்தித் திருத்தி, அகராதி, சொல்லடைவு, துணைநூற்பட்டியல், எண்-எழுத்து மாற்றி ஆகியவை ஒருங்கிணைக்கப்பட்டுள்ளன."
)

with st.sidebar:
    st.subheader("அடிப்படை வசதிகள் (Offline)")
    st.success("13+ தமிழ் மொழிக் கருவிகள் – API தேவையில்லை")
    st.markdown("""
- நேரடிக் குரல் தட்டச்சுப் பலகை (Live Voice Typing)
- தமிழ்த் தட்டச்சு விசைப்பலகை & ஒலிப்புத் தட்டச்சு
- ஒருங்குறி எழுத்துரு & குறியேற்ற மாற்றி
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
    "தட்டச்சு & குரல்",
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
        placeholder="தமிழில் தட்டச்சு செய்யவும் அல்லது குரல் தட்டச்சுப் பலகையிலிருந்து நகலெடுத்து ஒட்டவும்...",
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
# தாவல் 2: குரல்வழித் தட்டச்சு, குரல் -> Word ஆவணம், விசைப்பலகை, எழுத்துரு
# =========================================================
with tab_typing:
    t_sub_stt, t_sub1, t_sub2, t_sub3 = st.tabs([
        "🎙️ குரல் தட்டச்சு & ஆவண உருவாக்கம்",
        "⌨️ ஒலிப்பு & திரை விசைப்பலகை",
        "🔄 குறியேற்ற மாற்றி (Encoding)",
        "🔤 ஒருங்குறி எழுத்துருக்கள்",
    ])

    with t_sub_stt:
        _render_live_voice_typing_board()

        st.divider()
        st.subheader("📄 குரல் செய்தியை ஆவணமாக வடிவமைத்து சொல்லாய்வி (Word .docx) பதிவிறக்கம்")
        st.caption(
            "மேலே குரல் வழியாகத் தட்டச்சு செய்த உரையை '📋 நகலெடு' அழுத்தி இங்கு ஒட்டவும்; "
            "செய்தியின் தன்மைக்கு ஏற்பச் சுற்றறிக்கை, பரப்புரை அறிக்கை அல்லது அரசு அறிக்கை வடிவில் Word (.docx) கோப்பாகப் பெறலாம்."
        )

        voice_raw_input = st.text_area(
            "குரல் வழித் தட்டச்சு செய்த செய்தி / குறிப்புகள்",
            value=st.session_state["stt_result"],
            height=140,
            placeholder="மேலே பேசித் தட்டச்சு செய்த உரையை இங்கு ஒட்டவும் (Ctrl+V)...",
            key="voice_doc_source",
        )

        v_col1, v_col2, v_col3 = st.columns([1.2, 1, 1])
        voice_doc_style = v_col1.selectbox(
            "ஆவண வடிவம்",
            [
                "தானியங்கி (செய்தியின் தன்மைக்கு ஏற்ப)",
                "சுற்றறிக்கை (Circular)",
                "பரப்புரை / செய்தி அறிக்கை (Press / Publicity Report)",
                "அரசு அறிக்கை / அரசாணை (Government Report / Order)",
                "அலுவல் கடிதம் (Official Letter)",
                "குறிப்பாணை (Memorandum)",
                "கூட்டறிக்கை (Minutes of Meeting)",
            ],
        )
        voice_office = v_col2.text_input("அலுவலகம் / அமைப்பு (விருப்பம்)", placeholder="எ.கா: தமிழ்த்துறை / மாவட்ட ஆட்சியர் அலுவலகம்")
        voice_place_date = v_col3.text_input("இடம் & நாள் (விருப்பம்)", placeholder="எ.கா: கோயம்புத்தூர், 23.11.2026")

        if st.button(
            "✨ செய்திக்கு ஏற்ப வடிவமைத்து ஆவணம் உருவாக்கு",
            type="primary",
            disabled=(not ai_is_configured()),
        ):
            if voice_raw_input.strip():
                try:
                    with st.spinner("குரல் செய்தியைப் பகுப்பாய்ந்து அலுவல் ஆவணமாக வடிவமைக்கிறது..."):
                        st.session_state["voice_formatted_doc"] = format_voice_to_document(
                            spoken_text=voice_raw_input,
                            doc_style=voice_doc_style,
                            office_name=voice_office,
                            place_date=voice_place_date,
                        )
                    st.success("ஆவணம் வடிவமைக்கப்பட்டது! கீழே சரிபார்த்து Word (.docx) கோப்பாகப் பதிவிறக்கவும்.")
                except Exception as exc:
                    st.error(f"ஆவணத்தை வடிவமைக்க முடியவில்லை: {exc}")
            else:
                st.warning("முதலில் குரல் வழித் தட்டச்சு செய்த உரையைப் பெட்டியில் உள்ளிடவும்.")

        if st.session_state["voice_formatted_doc"]:
            formatted_voice_edit = st.text_area(
                "வடிவமைக்கப்பட்ட ஆவண வரைவு (தேவைப்படின் திருத்தலாம்)",
                value=st.session_state["voice_formatted_doc"],
                height=300,
                key="voice_formatted_editor",
            )
            dl1, dl2, dl3 = st.columns(3)
            dl1.download_button(
                "📥 சொல்லாய்வி ஆவணம் – Word (.docx)",
                make_docx(formatted_voice_edit),
                "inam-voice-official-document.docx",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True,
            )
            dl2.download_button(
                "📄 உரைக் கோப்பு – TXT",
                make_txt(formatted_voice_edit),
                "inam-voice-official-document.txt",
                "text/plain; charset=utf-8",
                use_container_width=True,
            )
            dl3.download_button(
                "🌐 அச்சு வடிவம் – HTML",
                make_html(formatted_voice_edit),
                "inam-voice-official-document.html",
                "text/html; charset=utf-8",
                use_container_width=True,
            )

        st.divider()
        with st.expander("பதிவுசெய்த ஒலிக்கோப்பை (.webm, .mp3, .wav, .m4a, .ogg) Gemini AI மூலம் உரையாக மாற்ற"):
            col_mic, col_up = st.columns(2)
            with col_mic:
                recorded_audio = st.audio_input("ஒலிவாங்கி வழி பதிவு செய்க")
            with col_up:
                uploaded_audio = st.file_uploader(
                    "அல்லது ஒலிக்கோப்பைப் பதிவேற்றவும்",
                    type=["webm", "wav", "mp3", "m4a", "ogg", "opus", "aac", "flac"],
                    key="stt_file_upload",
                )

            active_audio = recorded_audio or uploaded_audio
            if st.button(
                "ஒலிக்கோப்பைத் தமிழ் உரையாக மாற்று",
                disabled=(not ai_is_configured() or active_audio is None),
            ):
                try:
                    with st.spinner("ஒலிப்பதிவை Gemini AI தமிழ் எழுத்துகளாக மாற்றுகிறது..."):
                        mime = getattr(active_audio, "type", None) or "audio/wav"
                        fname = getattr(active_audio, "name", "") or ""
                        st.session_state["stt_result"] = transcribe_tamil_audio(
                            active_audio.getvalue(), mime_type=mime, filename=fname
                        )
                    st.success("ஒலிப்பதிவு உரையாக மாற்றப்பட்டு மேலே உள்ள ஆவண உருவாக்கிப் பெட்டியில் நிரப்பப்பட்டுள்ளது!")
                    st.rerun()
                except Exception as exc:
                    st.error(f"ஒலியை மாற்ற முடியவில்லை: {exc}")

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
        st.subheader("தமிழ்த் தட்டச்சு விசைப்பலகை (On-Screen Virtual Keyboard)")
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
    st.subheader("பயன்பாட்டு வழிகாட்டி – இனம் 3.4")
    st.markdown("""
- **மொழித்திருத்தம்:** சொற்பிழை, மயங்கொலிப் பிழை, வல்லினம் மிகும் சந்திப்பிழை ஆகியவற்றை API இல்லாமலேயே உடனடியாகத் திருத்தலாம்.
- **தட்டச்சு & குரல்:** பேசும்போதே உடனுக்குடன் ஒருங்குறியில் தட்டச்சாகும் **குரல் தட்டச்சுப் பலகை**, குரல் செய்தியைச் சுற்றறிக்கை / பரப்புரை அறிக்கை / அரசு அறிக்கை வடிவங்களில் **Word (.docx)** ஆவணமாக உருவாக்கும் வசதி, `.webm`/`.mp3`/`.wav` ஒலிக்கோப்பு மாற்றம், ஒலிப்புத் தட்டச்சு, திரை விசைப்பலகை, Bamini / TSCII / TAB / TAM ↔ Unicode குறியேற்ற மாற்றி ஆகியவற்றைப் பயன்படுத்தலாம்.
- **சொல் & அகராதி:** தமிழ்ச்சொல் சுட்டி, தமிழ்-ஆங்கில அலுவல் அகராதி, தமிழ் அகர வரிசைப்படுத்தம் ஆகியவை உள்ளடக்கப்பட்டுள்ளன.
- **ஆய்வு & எண் மாற்றி:** ஆய்வுக் கட்டுரைகளுக்கான சொல்லடைவு (Indexing), துணைநூற்பட்டியல் (Bibliography), எண் ↔ தமிழ் எழுத்து மாற்றி ஆகியவை இடம்பெற்றுள்ளன.
- **அலுவல் ஆவணம்:** மாதிரி DOCX/TXT/PDF கோப்புகளைப் பின்பற்றி Gemini AI மூலம் புதிய அலுவல் ஆவணங்களை உருவாக்கலாம்.
""")
