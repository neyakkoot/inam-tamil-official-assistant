"""
Ultra-fast Gemini integration with Smart Offline Document Formatting Fallback.
"""
import os
import re
import time
import json
from io import BytesIO
from datetime import datetime


def _secret(name: str, default: str = "") -> str:
    try:
        import streamlit as st
        value = st.secrets.get(name, "")
        if value:
            return str(value).strip()
    except Exception:
        pass
    return os.getenv(name, default).strip()


def get_gemini_api_key() -> str:
    return _secret("GEMINI_API_KEY")


def get_ai_model() -> str:
    return _secret("GEMINI_MODEL", "gemini-3.8-flash-lite")


def ai_is_configured() -> bool:
    return bool(get_gemini_api_key())


def _new_client():
    key = get_gemini_api_key()
    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY அமைக்கப்படவில்லை. Streamlit Secrets-இல் API Key-ஐ அமைக்கவும்."
        )
    from google import genai
    from google.genai import types
    try:
        return genai.Client(
            api_key=key,
            http_options=types.HttpOptions(timeout=20000),
        )
    except Exception:
        return genai.Client(api_key=key)


def _fast_config():
    try:
        from google.genai import types
        return types.GenerateContentConfig(
            temperature=0.15,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )
    except Exception:
        return None


def _call_gemini(contents, fast_mode: bool = True, preferred_models=None):
    """Gemini 3.8 மாதிரிகளில் அதிவேக இயக்கம்; 429 வரம்பு முடிந்தால் உடனடி மாற்று."""
    primary_model = get_ai_model()
    default_chain = (
        primary_model,
        "gemini-3.8-flash-lite",
        "gemini-3.8-flash",
    )
    models_to_try = preferred_models if preferred_models else default_chain

    unique_models = []
    for m in models_to_try:
        if m and m not in unique_models:
            unique_models.append(m)

    config = _fast_config() if fast_mode else None
    last_error = None
    client = _new_client()

    try:
        for model_name in unique_models:
            for attempt in range(2):
                if attempt > 0:
                    time.sleep(0.8)
                try:
                    kwargs = {"model": model_name, "contents": contents}
                    if config is not None:
                        kwargs["config"] = config
                    response = client.models.generate_content(**kwargs)
                    answer = (getattr(response, "text", None) or "").strip()
                    if answer:
                        return answer
                except Exception as exc:
                    last_error = exc
                    err_str = str(exc)
                    # 429 (தினசரி வரம்பு முடிவு) அல்லது 404 எனில் அதே மாதிரியை மீண்டும் முயலாமல் அடுத்த மாதிரிக்குச் செல்லவும்
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "404" in err_str:
                        break
                    continue
    finally:
        try:
            client.close()
        except Exception:
            pass

    raise RuntimeError(f"QUOTA_OR_BUSY: {last_error}")


def _offline_format_voice_document(
    spoken_text: str,
    doc_style: str,
    office_name: str = "",
    place_date: str = "",
) -> str:
    """Gemini தினசரி வரம்பு (429) முடிந்தாலும் உள்ளூர் இலக்கண விதிகளுடன் அலுவல் ஆவணமாக வடிவமைக்கும்."""
    from inam.corrector import correct_text, convert_to_official_style
    from inam.tamil_tools import check_sandhi

    cleaned, _ = correct_text(spoken_text.strip())
    cleaned, _ = check_sandhi(cleaned)
    formal_body, _ = convert_to_official_style(cleaned)

    # தானியங்கி வகை கண்டறிதல்
    resolved_style = doc_style
    if "தானியங்கி" in doc_style:
        if any(k in formal_body for k in ("செய்தியாளர்", "விழா", "நிகழ்வு", "பத்திரிகை", "பொதுமக்கள்", "அழைப்பு")):
            resolved_style = "பரப்புரை / செய்தி அறிக்கை"
        elif any(k in formal_body for k in ("அரசாணை", "அரசு", "ஆணை", "மாவட்ட ஆட்சியர்", "துறைச் செயலாளர்")):
            resolved_style = "அரசு அறிக்கை / ஆணை"
        elif any(k in formal_body for k in ("கூட்டம்", "தீர்மானம்", "உறுப்பினர்கள்", "தலைமையில்")):
            resolved_style = "கூட்டறிக்கை"
        elif any(k in formal_body for k in ("அனுப்புநர்", "பெறுநர்", "ஐயா", "வேண்டுகோள்")):
            resolved_style = "அலுவல் கடிதம்"
        else:
            resolved_style = "சுற்றறிக்கை"

    today_str = place_date.strip() if place_date.strip() else datetime.now().strftime("%d.%m.%Y")
    org_header = office_name.strip() if office_name.strip() else "[அலுவலகம் / நிறுவனத்தின் பெயர்]"
    first_line = formal_body.splitlines()[0][:65].rstrip(".,")

    if "பரப்புரை" in resolved_style or "செய்தி" in resolved_style:
        return (
            f"{org_header}\n"
            f"செய்தி / பரப்புரை அறிக்கை\n"
            f"இடம் & நாள்: {today_str}\n"
            f"{'-' * 55}\n\n"
            f"தலைப்பு: {first_line}\n\n"
            f"{formal_body}\n\n"
            f"வெளியீடு:\n"
            f"மக்கள் தொடர்பு / ஒருங்கிணைப்பாளர்\n"
            f"{org_header}"
        )

    if "அரசு" in resolved_style:
        return (
            f"தமிழ்நாடு அரசு\n"
            f"{org_header}\n\n"
            f"அரசு அறிக்கை / செயல்முறை ஆணை\n"
            f"ந.க.எண்: [எண் நிரப்பப்பட வேண்டும்]                நாள்: {today_str}\n"
            f"{'-' * 55}\n"
            f"பொருள்: {first_line} – தொடர்பாக.\n\n"
            f"ஆணை:\n"
            f"    {formal_body}\n\n"
            f"                              அலுவலகத் தலைவர் / செயலாளர்\n"
            f"                              {org_header}"
        )

    if "கூட்டறிக்கை" in resolved_style:
        return (
            f"{org_header}\n"
            f"கூட்டறிக்கை (Minutes of Meeting)\n"
            f"இடம் & நாள்: {today_str}\n"
            f"{'-' * 55}\n"
            f"பொருள்: {first_line}\n\n"
            f"கூட்டத்தில் விவாதிக்கப்பட்டு எடுக்கப்பட்ட முடிவுகள்:\n"
            f"1. {formal_body}\n\n"
            f"ஒருங்கிணைப்பாளர்                                  தலைவர்"
        )

    if "அலுவல் கடிதம்" in resolved_style:
        return (
            f"அனுப்புநர்\n"
            f"    {org_header}\n\n"
            f"பெறுநர்\n"
            f"    [பெறுநர் பதவி மற்றும் முகவரி]\n\n"
            f"ந.க.எண்: [எண்]                                  நாள்: {today_str}\n\n"
            f"ஐயா / அம்மையீர்,\n"
            f"    பொருள்: {first_line} – சார்பு.\n\n"
            f"    {formal_body}\n\n"
            f"                                        தங்கள் உண்மையுள்ள,\n"
            f"                                        [கையொப்பம் / பதவி]"
        )

    # இயல்புநிலை: சுற்றறிக்கை (Circular)
    return (
        f"{org_header}\n"
        f"சுற்றறிக்கை\n"
        f"ந.க.எண்: [எண் நிரப்பப்பட வேண்டும்]                நாள்: {today_str}\n"
        f"{'-' * 55}\n"
        f"பொருள்: {first_line} – தொடர்பாக.\n\n"
        f"    {formal_body}\n\n"
        f"    அனைவரும் இதனைக் கவனத்தில் கொண்டு உரிய நடவடிக்கை மேற்கொள்ளுமாறு "
        f"கேட்டுக்கொள்ளப்படுகிறார்கள்.\n\n"
        f"                                        முதல்வர் / அலுவலகத் தலைவர்\n"
        f"                                        {org_header}"
    )


def format_voice_to_document(
    spoken_text: str,
    doc_style: str = "தானியங்கி (செய்தியின் தன்மைக்கு ஏற்ப)",
    office_name: str = "",
    place_date: str = "",
) -> tuple[str, bool]:
    """(வடிவமைக்கப்பட்ட_ஆவணம், AI_பயன்படுத்தப்பட்டதா) எனத் திருப்பித் தரும்."""
    if not spoken_text.strip():
        raise ValueError("உரை காலியாக உள்ளது.")

    if get_gemini_api_key():
        prompt = f"""
நீங்கள் தமிழ்நாடு அரசு, பல்கலைக்கழகம் மற்றும் மக்கள் தொடர்புத் துறையின் மூத்த தமிழ் ஆவண வடிவமைப்பாளர்.

பயனர் குரல் வழியாகப் பேசித் தட்டச்சு செய்த மூல உரை கீழே கொடுக்கப்பட்டுள்ளது.
தேர்ந்தெடுக்கப்பட்ட ஆவண வடிவம்: **{doc_style}**
அலுவலகம் / அமைப்பு: {office_name or "செய்திக்கு ஏற்ப அமைக்கவும்"}
இடம் / நாள்: {place_date or "செய்திக்கு ஏற்ப அமைக்கவும்"}

கட்டாய விதிகள்:
1. **"தானியங்கி (செய்தியின் தன்மைக்கு ஏற்ப)"** எனத் தேர்ந்தெடுக்கப்பட்டிருந்தால், உள்ளீட்டுச் செய்தி எதைப் பற்றியது என்பதைப் பகுப்பாய்ந்து—அது **சுற்றறிக்கை**, **பரப்புரை / செய்தி அறிக்கை**, **அரசு அறிக்கை / ஆணை**, **அலுவல் கடிதம்**, அல்லது **கூட்டறிக்கை** ஆகியவற்றில் எதற்குப் பொருந்துமோ அந்தத் துல்லியமான வடிவமைப்பைத் தேர்ந்தெடுத்து உருவாக்கவும்.
2. குரல் தட்டச்சில் ஏற்படும் ஒலிப்புப் பிழைகள், மயங்கொலிப் பிழைகள் (ண/ந/ன, ல/ள/ழ, ர/ற), சந்திப் பிழைகள் மற்றும் பேச்சுவழக்குச் சொற்களைக் களைந்து **தூய செந்தமிழ் அலுவல் நடையில்** எழுதவும்.
3. தலைப்பு, ந.க.எண் / அறிக்கை எண், நாள், பொருள், தெளிவான பத்திகள், மற்றும் கையொப்பம் / வெளியீட்டாளர் பகுதியை முறையாக அமைக்கவும்.
4. முன்னுரை அல்லது விளக்கம் எதுவுமின்றி, நேரடியாக Word ஆவணத்தில் அச்சிடத் தகுந்த இறுதி ஆவண உரையை மட்டும் வழங்கவும்.

குரல் வழித் தட்டச்சு செய்த செய்தி:
{spoken_text}
"""
        try:
            ai_doc = _call_gemini(prompt, fast_mode=True)
            return ai_doc, True
        except Exception:
            pass

    # Gemini வரம்பு (429) முடிந்திருந்தால் உடனடியாக உள்ளூர் ஆவண வடிவமைப்பை வழங்குதல்
    offline_doc = _offline_format_voice_document(spoken_text, doc_style, office_name, place_date)
    return offline_doc, False


def improve_with_ai(text: str) -> str:
    prompt = (
        "தமிழ் எழுத்துப் பிழை, மயங்கொலிப் பிழை (ண/ந/ன, ல/ள/ழ, ர/ற), சந்திப் பிழை நீக்கி "
        "தூய அலுவல் தமிழில் திருத்தப்பட்ட உரையை மட்டும் உடனே தரவும்:\n\n"
        + text
    )
    return _call_gemini(prompt, fast_mode=True)


def improve_with_ai_detailed(text: str, rule_findings: list) -> tuple:
    prompt = (
        "தமிழ் இலக்கணப் பிழைதிருத்தி. கீழுள்ள உரையில் உள்ள எழுத்து, மயங்கொலி (ண/ந/ன, ல/ள/ழ, ர/ற), "
        "சந்திப் பிழைகளைத் திருத்தி JSON மட்டும் தரவும்.\n"
        'வடிவம்: {"corrected_text":"திருத்தப்பட்ட உரை","suggestions":[{"category":"பிழை வகை","original":"பிழை","suggestion":"திருத்தம்","reason":"சுருக்கக் காரணம்"}]}\n\n'
        "உரை:\n" + text
    )
    raw = _call_gemini(prompt, fast_mode=True)
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        data = json.loads(cleaned)
        corrected_text = (data.get("corrected_text") or text).strip()
        suggestions = data.get("suggestions") or []
        if not isinstance(suggestions, list):
            suggestions = []
        return corrected_text, suggestions
    except Exception:
        return raw.strip(), []


def transcribe_tamil_audio(
    audio_bytes: bytes, mime_type: str = "audio/wav", filename: str = ""
) -> str:
    if not audio_bytes:
        raise ValueError("ஒலிப்பதிவுத் தரவு காலியாக உள்ளது.")

    from google.genai import types

    ext_mime_map = {
        ".webm": "audio/webm",
        ".wav": "audio/wav",
        ".mp3": "audio/mp3",
        ".m4a": "audio/mp4",
        ".mp4": "audio/mp4",
        ".ogg": "audio/ogg",
        ".opus": "audio/ogg",
        ".aac": "audio/aac",
        ".flac": "audio/flac",
    }

    clean_mime = ""
    fname_lower = (filename or "").lower()
    for ext, mapped_mime in ext_mime_map.items():
        if fname_lower.endswith(ext):
            clean_mime = mapped_mime
            break

    if not clean_mime:
        if mime_type and (mime_type.startswith("audio/") or mime_type == "video/webm"):
            clean_mime = "audio/webm" if mime_type == "video/webm" else mime_type
        else:
            clean_mime = "audio/wav"

    prompt = (
        "இந்த ஒலிப்பதிவில் பேசப்பட்டுள்ள தமிழ் உரையைத் துல்லியமாகத் தமிழ் ஒருங்குறி (Unicode) "
        "எழுத்துகளில் மட்டும் எழுதித் தரவும். முன்னுரை அல்லது விளக்கம் வேண்டாம்."
    )
    audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=clean_mime)

    return _call_gemini(
        [prompt, audio_part],
        fast_mode=True,
        preferred_models=("gemini-3.8-flash-lite", "gemini-3.8-flash"),
    )


def _document_prompt(doc_type: str, details: dict) -> str:
    details_json = json.dumps(details, ensure_ascii=False, indent=2)
    return (
        "நீங்கள் தமிழ்நாடு அரசு மற்றும் கல்வி நிறுவனங்களின் அலுவல் ஆவணங்களைப் பிழையின்றி உருவாக்கும் வல்லுநர்.\n\n"
        f"தேர்ந்தெடுக்கப்பட்ட ஆவண வகை: **{doc_type}**\n"
        f"பயனர் வழங்கிய விவரங்கள்:\n{details_json}\n\n"
        "விதிகள்:\n"
        f'1. மாதிரி கோப்பில் பல ஆவணங்கள் இருந்தால் **"{doc_type}"** வகைக்குப் பொருத்தமான வடிவமைப்பை மட்டுமே பின்பற்றவும்.\n'
        f'2. இல்லையெனில் நிலையான தமிழ்நாடு அரசு / கல்வி நிறுவன **"{doc_type}"** வடிவமைப்பில் உருவாக்கவும்.\n'
        "3. சந்திப் பிழை, எழுத்துப் பிழை இன்றித் தூய செந்தமிழில் எழுதவும்.\n"
        "4. மாதிரியில் உள்ள பழைய பெயர், தேதி, எண்களை நகலெடுக்க வேண்டாம்; தரப்படாத விவரங்களுக்கு `[விவரம் நிரப்பப்பட வேண்டும்]` என இடவும்.\n"
        "5. இறுதி ஆவண உரையை மட்டும் வழங்கவும்.\n"
    )


def _generate_from_text(sample_text: str, doc_type: str, details: dict) -> str:
    prompt = _document_prompt(doc_type, details) + "\n\nமாதிரி ஆவணத்தின் உரை:\n" + sample_text[:25000]
    return _call_gemini(prompt, fast_mode=True)


def generate_document_from_template(
    sample_bytes: bytes,
    filename: str,
    doc_type: str,
    details: dict,
) -> str:
    if not sample_bytes:
        raise ValueError("மாதிரி கோப்பு காலியாக உள்ளது.")

    name = (filename or "").lower()

    if name.endswith(".docx"):
        from docx import Document
        doc = Document(BytesIO(sample_bytes))
        chunks = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                chunks.append(" | ".join(cell.text for cell in row.cells))
        sample_text = "\n".join(chunks)
        if not sample_text.strip():
            raise ValueError("DOCX கோப்பில் வாசிக்கக்கூடிய உரை இல்லை.")
        return _generate_from_text(sample_text, doc_type, details)

    if name.endswith(".txt"):
        sample_text = sample_bytes.decode("utf-8-sig", errors="replace")
        if not sample_text.strip():
            raise ValueError("TXT கோப்பில் உரை இல்லை.")
        return _generate_from_text(sample_text, doc_type, details)

    if name.endswith(".pdf"):
        from google.genai import types
        pdf_part = types.Part.from_bytes(data=sample_bytes, mime_type="application/pdf")
        prompt = _document_prompt(doc_type, details) + "\nஇந்த PDF-ஐப் படித்து புதிய ஆவணத்தை உருவாக்கவும்."
        return _call_gemini([prompt, pdf_part], fast_mode=True)

    raise ValueError("DOCX, PDF அல்லது TXT கோப்பை மட்டும் பதிவேற்றவும்.")
