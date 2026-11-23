"""
Ultra-fast Gemini & Fallback Audio Transcription for Inam Tamil Official Assistant.
"""
import os
import re
import time
import json
from io import BytesIO


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


def get_groq_api_key() -> str:
    return _secret("GROQ_API_KEY")


def get_ai_model() -> str:
    return _secret("GEMINI_MODEL", "gemini-3.8-flash-lite")


def ai_is_configured() -> bool:
    return bool(get_gemini_api_key() or get_groq_api_key())


def _new_client():
    key = get_gemini_api_key()
    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY அமைக்கப்படவில்லை. Streamlit Secrets-இல் API Key-ஐ அமைக்கவும்."
        )
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise RuntimeError(
            "google-genai தொகுப்பு நிறுவப்படவில்லை. pip install -U google-genai என இயக்கவும்."
        ) from exc

    try:
        return genai.Client(
            api_key=key,
            http_options=types.HttpOptions(timeout=20_000),
        )
    except Exception:
        return genai.Client(api_key=key)


def _fast_config():
    try:
        from google.genai import types
        return types.GenerateContentConfig(
            temperature=0.1,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )
    except Exception:
        return None


def _call_gemini(contents, fast_mode: bool = True, preferred_models: tuple = None):
    """Fast execution with targeted retry on 503 high-demand spikes."""
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

    # முதல் சுற்றில் உடனடியாகவும், 503 நெரிசல் வந்தால் சிறிய இடைவெளியுடனும் முயற்சித்தல்
    schedule = [(m, 0.0) for m in unique_models] + [
        (unique_models[0], 0.8),
        (unique_models[-1], 1.5),
    ]

    config = _fast_config() if fast_mode else None
    last_error = None
    client = _new_client()

    try:
        for model_name, delay in schedule:
            if delay > 0:
                time.sleep(delay)
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
                # 404 அல்லது 400 போன்ற நிரந்தரப் பிழை எனில் மீண்டும் அதே மாதிரியை முயற்சிக்கத் தேவையில்லை
                if "404" in err_str or "NOT_FOUND" in err_str:
                    continue
                continue
    finally:
        try:
            client.close()
        except Exception:
            pass

    raise RuntimeError(f"Gemini வழங்கி தற்போது அதிக நெரிசலில் உள்ளது: {last_error}")


def _transcribe_with_groq_fallback(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """GROQ_API_KEY இருந்தால், Gemini 503 நெரிசலின் போது 1 வினாடியில் Whisper மூலம் மாற்றும்."""
    groq_key = get_groq_api_key()
    if not groq_key:
        raise RuntimeError("GROQ_API_KEY அமைக்கப்படவில்லை.")

    import urllib.request
    import uuid

    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    safe_name = filename if filename else "audio.webm"

    body = bytearray()
    # model field
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(b'Content-Disposition: form-data; name="model"\r\n\r\nwhisper-large-v3\r\n')
    # language field
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(b'Content-Disposition: form-data; name="language"\r\n\r\nta\r\n')
    # file field
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(
        f'Content-Disposition: form-data; name="file"; filename="{safe_name}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n".encode("utf-8")
    )
    body.extend(audio_bytes)
    body.extend(f"\r\n--{boundary}--\r\n".encode())

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/audio/transcriptions",
        data=bytes(body),
        headers={
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return (data.get("text") or "").strip()


def improve_with_ai(text: str) -> str:
    prompt = (
        "தமிழ் எழுத்துப் பிழை, மயங்கொலிப் பிழை (ண/ந/ன, ல/ள/ழ, ர/ற), சந்திப் பிழை நீக்கி "
        "தூய அலுவல் தமிழில் திருத்தப்பட்ட உரையை மட்டும் உடனே தரவும்:\n\n"
        f"{text}"
    )
    return _call_gemini(prompt, fast_mode=True)


def improve_with_ai_detailed(text: str, rule_findings: list) -> tuple[str, list]:
    """நொடிப்பொழுதில் எழுத்து, மயங்கொலி, சந்திப் பிழைகளைத் திருத்தி JSON தருதல்."""
    prompt = f"""தமிழ் இலக்கணப் பிழைதிருத்தி. கீழுள்ள உரையில் உள்ள எழுத்து, மயங்கொலி (ண/ந/ன, ல/ள/ழ, ர/ற), சந்திப் பிழைகளைத் திருத்தி JSON மட்டும் தரவும்.
வடிவம்:
{{"corrected_text":"திருத்தப்பட்ட உரை","suggestions":[{{"category":"பிழை வகை","original":"பிழை","suggestion":"திருத்தம்","reason":"சுருக்கக் காரணம்"}}]}}

உரை:
{text}"""
    raw = _call_gemini(prompt, fast_mode=True)
    cleaned = re.sub(
        r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE
    ).strip()
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
    """தமிழ் ஒலிப்பதிவை (.webm, .wav, .mp3, .m4a, .ogg) அதிவேகமாகத் தமிழ் ஒருங்குறி உரையாக மாற்றும்."""
    if not audio_bytes:
        raise ValueError("ஒலிப்பதிவுத் தரவு காலியாக உள்ளது.")

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

    gemini_err = None
    if get_gemini_api_key():
        try:
            from google.genai import types
            prompt = (
                "இந்த ஒலிப்பதிவில் பேசப்பட்டுள்ள தமிழ் உரையைத் துல்லியமாகத் தமிழ் ஒருங்குறி (Unicode) "
                "எழுத்துகளில் மட்டும் எழுதித் தரவும். முன்னுரை அல்லது விளக்கம் வேண்டாம்."
            )
            audio_part = types.Part.from_bytes(
                data=audio_bytes,
                mime_type=clean_mime,
            )
            return _call_gemini(
                [prompt, audio_part],
                fast_mode=True,
                preferred_models=("gemini-3.8-flash-lite", "gemini-3.8-flash"),
            )
        except Exception as exc:
            gemini_err = exc

    # Gemini 503 நெரிசலில் இருந்தால் Groq Whisper-க்கு தானாக மாறுதல்
    if get_groq_api_key():
        try:
            return _transcribe_with_groq_fallback(audio_bytes, filename or "audio.webm")
        except Exception as groq_exc:
            raise RuntimeError(f"Gemini ({gemini_err}) & Groq ({groq_exc})")

    raise RuntimeError(
        "Google Gemini வழங்கி தற்போது அதிக நெரிசலில் (503) உள்ளது. சில வினாடிகள் கழித்து மீண்டும் முயற்சிக்கவும்."
    )


def _document_prompt(doc_type: str, details: dict) -> str:
    return f"""
நீங்கள் தமிழ்நாடு அரசு மற்றும் கல்வி நிறுவனங்களின் அலுவல் ஆவணங்களைப் பிழையின்றி உருவாக்கும் வல்லுநர்.

தேர்ந்தெடுக்கப்பட்ட ஆவண வகை: **{doc_type}**
பயனர் வழங்கிய விவரங்கள்:
{json.dumps(details, ensure_ascii=False, indent=2)}

விதிகள்:
1. மாதிரி கோப்பில் பல ஆவணங்கள் இருந்தால் **"{doc_type}"** வகைக்குப் பொருத்தமான வடிவமைப்பை மட்டுமே பின்பற்றவும்.
2. இல்லையெனில் நிலையான தமிழ்நாடு அரசு / கல்வி நிறுவன **"{doc_type}"** வடிவமைப்பில் (சுற்றறிக்கை / அரசாணை / குறிப்பாணை / பாராட்டுக் கடிதம் / அலுவல் கடிதம்) உருவாக்கவும்.
3. சந்திப் பிழை, எழுத்துப் பிழை இன்றித் தூய செந்தமிழில் எழுதவும்.
4. மாதிரியில் உள்ள பழைய பெயர், தேதி, எண்களை நகலெடுக்க வேண்டாம்; தரப்படாத விவரங்களுக்கு `[விவரம் நிரப்பப்பட வேண்டும்]` என இடவும்.
5. இறுதி ஆவண உரையை மட்டும் வழங்கவும்.
"""


def _generate_from_text(sample_text: str, doc_type: str, details: dict) -> str:
    prompt = (
        _document_prompt(doc_type, details)
        + "\n\nமாதிரி ஆவணத்தின் உரை:\n"
        + sample_text[:25000]
    )
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
        try:
            from docx import Document
            doc = Document(BytesIO(sample_bytes))
            chunks = [p.text for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    chunks.append(" | ".join(cell.text for cell in row.cells))
            sample_text = "\n".join
