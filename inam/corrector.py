import re

# Conservative starter rules only. No guessed substitutions for context-sensitive
# Tamil distinctions: ண/ந/ன, ல/ள/ழ, ர/ற.
PHRASE_RULES = [
    ("சொல் இணைப்பு","கலந்து கொள்ளுமாறு","கலந்துகொள்ளுமாறு","இந்த வினையெச்சத் தொடர் இணைத்து எழுதும் பரிந்துரை."),
    ("சொல் இணைப்பு","கலந்து கொள்ள","கலந்துகொள்ள","இந்தச் சூழலில் பொதுவாக இணைத்து எழுதப்படும் வினையெச்சத் தொடர்."),
    ("சொற்றொடர்","நடைபெற இருக்கின்ற","நடைபெறவுள்ள","அலுவல் மொழியில் சுருக்கமான எதிர்காலக் குறிப்பு."),
]
OFFICIAL_STYLE_RULES = [
    ("அனுப்பி வைக்கவும்","அனுப்பி வைக்குமாறு கேட்டுக்கொள்ளப்படுகிறது","கோரிக்கைத் தன்மையுள்ள அலுவல் மொழிநடை."),
    ("தெரிவிக்கவும்","தெரிவிக்குமாறு கேட்டுக்கொள்ளப்படுகிறது","மரியாதையான அலுவல் மொழிநடை."),
    ("செய்து தரவும்","செய்து தருமாறு கேட்டுக்கொள்ளப்படுகிறது","கோரிக்கையை அலுவல் மொழியில் அமைத்தல்."),
    ("கலந்து கொள்ள வேண்டும்","கலந்துகொள்ளுமாறு அறிவுறுத்தப்படுகிறது","அறிவுறுத்தல் சார்ந்த அலுவல் மொழிநடை."),
]
def _apply(text,rules,category):
    result=text; findings=[]
    for old,new,reason in rules:
        if old in result:
            result=result.replace(old,new)
            findings.append({"category":category,"original":old,"suggestion":new,"reason":reason})
    return result,findings

def correct_text(text:str):
    result,findings=_apply(text,[(a,b,d) for _,a,b,d in PHRASE_RULES],"சொற்றொடர் / சொல் இணைப்பு")
    normalized=re.sub(r"[ \t]{2,}"," ",result)
    if normalized!=result:
        findings.append({"category":"இடைவெளி","original":"இரட்டை / பல இடைவெளிகள்","suggestion":"ஒற்றை இடைவெளி","reason":"அடுத்தடுத்த தேவையற்ற இடைவெளிகள் சீரமைக்கப்பட்டன."})
        result=normalized
    if not findings:
        findings=[{"category":"குறிப்பு","original":"மாற்றம் கண்டறியப்படவில்லை","suggestion":"மனிதர் சரிபார்க்கவும்","reason":"இந்தப் பதிப்பின் விதிகளில் மாற்றம் கிடைக்கவில்லை; உரை பிழையற்றது என்று இதனால் உறுதி செய்ய முடியாது."}]
    return result,findings

def convert_to_official_style(text:str):
    result,findings=_apply(text,OFFICIAL_STYLE_RULES,"அலுவல் மொழிநடை")
    if not findings:
        findings=[{"category":"அலுவல் மொழிநடை","original":"குறிப்பிட்ட மாற்றம் இல்லை","suggestion":"மனிதர் பரிசீலிக்கவும்","reason":"தானியங்கி அலுவல் மொழிநடை விதி பொருந்தவில்லை."}]
    notes=[f"{f['original']} → {f['suggestion']}: {f['reason']}" for f in findings]
    return result,notes
