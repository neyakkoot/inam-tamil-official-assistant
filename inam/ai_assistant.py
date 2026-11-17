def improve_with_ai_detailed(text: str, rule_findings: list) -> tuple[str, list]:
    """
    உள்ளூர் பிழைதிருத்தி கண்டறிந்த முடிவுகளுடன், Gemini AI மூலம்
    எழுத்துப் பிழை, மயங்கொலிப் பிழை (ண/ந/ன, ல/ள/ழ, ர/ற), சந்திப் பிழை மற்றும்
    அலுவல் மொழிநடைப் பரிந்துரைகளைப் பெறுதல்.
    """
    rule_summary = json.dumps(rule_findings, ensure_ascii=False)
    prompt = f"""
நீங்கள் கணித்தமிழ் உருபனியல் மற்றும் தமிழ் இலக்கணப் பிழைதிருத்த வல்லுநர்.
கீழுள்ள உரையை ஆராய்ந்து:
1. எழுத்துப் பிழைகள், மயங்கொலி எழுத்துப் பிழைகள் (ண/ந/ன, ல/ள/ழ, ர/ற),
2. உருபனியல் விகுதிப் பிழைகள் மற்றும் சந்திப் பிழைகள் (வல்லினம் மிகும்/மிகா இடங்கள்),
3. வாக்கிய அமைப்பு மற்றும் அலுவல் மொழிநடை ஆகியவற்றை முழுமையாகத் திருத்துங்கள்.

உள்ளூர் விதித்தொகுப்பு ஏற்கெனவே கண்டறிந்தவை: {rule_summary}

பொருள், பெயர்கள், எண்கள், தேதிகள், அரசாணை எண்கள் ஆகியவற்றை மாற்றாதீர்கள்.
பதிலைக் கீழ்க்காணும் JSON வடிவத்தில் மட்டுமே (வேறு உரையின்றி) வழங்குங்கள்:
{{
  "corrected_text": "முழுமையாகத் திருத்தப்பட்ட தமிழ் உரை",
  "suggestions": [
    {{
      "category": "பிழை வகை (எ.கா: மயங்கொலிப் பிழை / சந்திப் பிழை / உருபனியல் / அலுவல் நடை)",
      "original": "பிழையான சொல் அல்லது தொடர்",
      "suggestion": "சரியான பரிந்துரை",
      "reason": "இலக்கண விளக்கம்"
    }}
  ]
}}

ஆராய வேண்டிய உரை:
{text}
"""
    raw = _call_gemini(prompt)
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        data = json.loads(cleaned)
        corrected_text = (data.get("corrected_text") or text).strip()
        suggestions = data.get("suggestions") or []
        if not isinstance(suggestions, list):
            suggestions = []
        return corrected_text, suggestions
    except Exception:
        return raw.strip(), [
            {
                "category": "Gemini AI திருத்தம்",
                "original": "முழு உரை",
                "suggestion": "AI மூலம் திருத்தப்பட்டது",
                "reason": "எழுத்து, சந்தி மற்றும் அலுவல் மொழிநடைச் சீரமைப்பு.",
            }
        ]
