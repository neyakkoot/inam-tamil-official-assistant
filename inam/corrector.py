import re

# Conservative starter rules only. These do not attempt to infer every Tamil
# grammatical distinction; uncertain cases are deliberately left unchanged.
REPLACEMENTS = [
    ("கலந்து கொள்ள", "கலந்துகொள்ள"),
    ("செய்து தரவும்", "செய்து தருமாறு கேட்டுக்கொள்ளப்படுகிறது"),
    ("அனுப்பி வைக்கவும்", "அனுப்பி வைக்குமாறு கேட்டுக்கொள்ளப்படுகிறது"),
    ("தெரிவிக்கவும்", "தெரிவிக்குமாறு கேட்டுக்கொள்ளப்படுகிறது"),
    ("கலந்து கொள்ளுமாறு", "கலந்துகொள்ளுமாறு"),
    ("நடைபெற இருக்கின்ற", "நடைபெறவுள்ள"),
]

def correct_text(text: str):
    corrected = text
    notes = []
    for old, new in REPLACEMENTS:
        if old in corrected:
            corrected = corrected.replace(old, new)
            notes.append(f"“{old}” → “{new}” (தொடக்கநிலைச் சொற்றொடர் பரிந்துரை)")
    corrected = re.sub(r"[ \t]{2,}", " ", corrected)
    if corrected != text and not notes:
        notes.append("இடைவெளி சீரமைக்கப்பட்டது.")
    if not notes:
        notes.append("அறியப்பட்ட தொடக்கநிலை விதிகளில் மாற்றம் தேவைப்படும் இடம் கண்டறியப்படவில்லை. இது பிழையில்லை என்பதற்கான உறுதி அல்ல.")
    return corrected, notes
