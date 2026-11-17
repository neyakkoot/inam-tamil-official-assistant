import os

def ai_is_configured() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))

def improve_with_ai(text: str) -> str:
    """Optional AI enhancement. Requires OPENAI_API_KEY and the openai package."""
    if not ai_is_configured():
        raise RuntimeError("OPENAI_API_KEY சூழல் மாறி அமைக்கப்படவில்லை.")
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("openai package நிறுவப்படவில்லை. pip install openai") from exc

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("INAM_AI_MODEL", "gpt-4.1-mini")
    response = client.chat.completions.create(
        model=model,
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": (
                    "நீங்கள் தமிழ் அலுவல் மொழி திருத்த உதவியாளர். "
                    "பொருள், உண்மைகள், பெயர்கள், எண்கள், தேதிகள், அரசாணை எண்கள் "
                    "மற்றும் சட்டக் குறிப்புகளை மாற்றாதீர்கள்; இல்லாத தகவலைச் சேர்க்காதீர்கள். "
                    "எழுத்து, இலக்கணம், தெளிவு, மரியாதையான அலுவல் மொழிநடை ஆகியவற்றை மட்டும் "
                    "மேம்படுத்துங்கள். உறுதியில்லாத இடங்களை ஊகித்து மாற்றாமல் அப்படியே வையுங்கள். "
                    "திருத்தப்பட்ட உரையை மட்டும் வழங்குங்கள்."
                ),
            },
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content.strip()
