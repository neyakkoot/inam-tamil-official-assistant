import os


def _read_secret(name: str) -> str:
    """Read a Streamlit secret first, then an environment variable."""
    try:
        import streamlit as st

        value = st.secrets.get(name, "")
        if value:
            return str(value).strip()
    except Exception:
        # Streamlit secrets may not exist during local tests.
        pass

    return os.getenv(name, "").strip()


def get_gemini_api_key() -> str:
    return _read_secret("GEMINI_API_KEY")


def get_ai_model() -> str:
    return _read_secret("GEMINI_MODEL") or "gemini-3.8-flash"


def ai_is_configured() -> bool:
    return bool(get_gemini_api_key())


def improve_with_ai(text: str) -> str:
    """
    Optional Gemini enhancement.
    No API request is made unless GEMINI_API_KEY is configured.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY அமைக்கப்படவில்லை. அடிப்படைத் திருத்த வசதிகளை "
            "API இல்லாமல் தொடர்ந்து பயன்படுத்தலாம்."
        )

    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError(
            "google-genai தொகுப்பு நிறுவப்படவில்லை. "
            "requirements.txt-இல் உள்ள தொகுப்புகளை நிறுவவும்."
        ) from exc

    client = genai.Client(api_key=api_key)
    model = get_ai_model()

    system_instruction = (
        "நீங்கள் தமிழ் அலுவல் மொழி திருத்த உதவியாளர். "
        "கொடுக்கப்பட்ட உரையைத் தெளிவான, இயல்பான, மரியாதையான தமிழ் "
        "அலுவல் மொழிநடையில் மேம்படுத்துங்கள். "
        "பொருள், உண்மைகள், பெயர்கள், எண்கள், தேதிகள், அரசாணை எண்கள், "
        "சட்டக் குறிப்புகள் மற்றும் மேற்கோள்களை மாற்றாதீர்கள். "
        "இல்லாத தகவலைச் சேர்க்காதீர்கள். "
        "உறுதியில்லாத இடங்களை ஊகித்து மாற்றாமல் அப்படியே வையுங்கள். "
        "பத்தி அமைப்பு மற்றும் பட்டியல்களை இயன்றவரை பாதுகாக்கவும். "
        "விளக்க உரை அல்லது முன்னுரை இல்லாமல் திருத்தப்பட்ட உரையை மட்டும் வழங்குங்கள்."
    )

    response = client.models.generate_content(
        model=model,
        contents=(
            system_instruction
            + "\n\nதிருத்த வேண்டிய உரை:\n"
            + text
        ),
    )

    result = (response.text or "").strip()
    if not result:
        raise RuntimeError(
            "Gemini பதில் கிடைக்கவில்லை. மீண்டும் முயற்சிக்கவும்."
        )

    return result
