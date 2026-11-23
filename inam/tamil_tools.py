import json
import re
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------
# 0. அகராதித் தரவுத்தளம் ஏற்றுதல் (JSON Dictionary Loader)
# ---------------------------------------------------------
DICT_PATH = Path(__file__).parent / "dictionary_data.json"


def load_dictionary() -> dict:
    if DICT_PATH.exists():
        try:
            with open(DICT_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "அலுவல்": {
            "meaning": "அரசு அல்லது நிறுவனப் பணி, கடமை (Official duty)",
            "synonyms": ["பணி", "கடமை", "வினை"],
            "english": "Official",
        }
    }


TAMIL_DICTIONARY = load_dictionary()

# ---------------------------------------------------------
# 1. ஒலிப்புத் தட்டச்சு (Phonetic Transliteration)
# ---------------------------------------------------------
VOWELS = {
    "aa": "ஆ", "A": "ஆ", "a": "அ",
    "ii": "ஈ", "ee": "ஈ", "I": "ஈ", "i": "இ",
    "uu": "ஊ", "oo": "ஊ", "U": "ஊ", "u": "உ",
    "ae": "ஏ", "E": "ஏ", "e": "எ",
    "ai": "ஐ",
    "oa": "ஓ", "O": "ஓ", "o": "ஒ",
    "au": "ஔ", "ou": "ஔ",
}

VOWEL_SIGNS = {
    "aa": "ா", "A": "ா", "a": "",
    "ii": "ீ", "ee": "ீ", "I": "ீ", "i": "ி",
    "uu": "ூ", "oo": "ூ", "U": "ூ", "u": "ு",
    "ae": "ே", "E": "ே", "e": "ெ",
    "ai": "ை",
    "oa": "ோ", "O": "ோ", "o": "ொ",
    "au": "ௌ", "ou": "ௌ",
}

CONSONANTS = {
    "ng": "ங்", "nj": "ஞ்", "ndh": "ந்", "nth": "ந்", "zh": "ழ்",
    "sh": "ஷ்", "ch": "ச்", "th": "த்", "dh": "த்",
    "k": "க்", "g": "க்", "c": "ச்", "s": "ச்", "j": "ஜ்",
    "T": "ட்", "D": "ட்", "N": "ண்", "t": "த்", "d": "த்",
    "n": "ந்", "p": "ப்", "b": "ப்", "m": "ம்", "y": "ய்",
    "r": "ர்", "R": "ற்", "l": "ல்", "L": "ள்", "v": "வ்",
    "w": "வ்", "S": "ஸ்", "h": "ஹ்",
}


def phonetic_to_tamil(text: str) -> str:
    result = []
    i = 0
    n = len(text)
    cons_keys = sorted(CONSONANTS.keys(), key=len, reverse=True)
    vowel_keys = sorted(VOWELS.keys(), key=len, reverse=True)

    while i < n:
        if text[i].isspace() or not text[i].isalpha():
            result.append(text[i])
            i += 1
            continue

        matched_cons = next((ck for ck in cons_keys if text[i:].startswith(ck)), None)
        if matched_cons:
            base_char = CONSONANTS[matched_cons][0]
            i += len(matched_cons)
            matched_vowel = next((vk for vk in vowel_keys if text[i:].startswith(vk)), None)
            if matched_vowel:
                result.append(base_char + VOWEL_SIGNS[matched_vowel])
                i += len(matched_vowel)
            else:
                result.append(base_char + "்")
        else:
            matched_vowel = next((vk for vk in vowel_keys if text[i:].startswith(vk)), None)
            if matched_vowel:
                result.append(VOWELS[matched_vowel])
                i += len(matched_vowel)
            else:
                result.append(text[i])
                i += 1
    return "".join(result)


# ---------------------------------------------------------
# 2. குறியேற்ற மாற்றி (TSCII / Bamini / TAB / TAM <-> Unicode)
# ---------------------------------------------------------
TSCII_MAP = {
    "þ": "இ", "ÿ": "ஈ", "«": "அ", "¬": "ஆ", "­": "உ", "®": "ஊ",
    "¯": "எ", "°": "ஏ", "±": "ஐ", "²": "ஒ", "³": "ஓ", "´": "ஔ",
    "¸": "க", "¹": "ங", "º": "ச", "»": "ஞ", "¼": "ட", "½": "ண",
    "¾": "த", "¿": "ந", "À": "ப", "Á": "ம", "Â": "ய", "Ã": "ர",
    "Ä": "ல", "Å": "வ", "Æ": "ழ", "Ç": "ள", "È": "ற", "É": "ன",
    "¡": "ா", "¢": "ி", "£": "ீ", "¤": "ு", "¥": "ூ",
    "¦": "ெ", "§": "ே", "¨": "ை", "ì": "்",
}

BAMINI_MAP = {
    "m": "அ", "M": "ஆ", ",": "இ", "<": "ஈ", "c": "உ", "C": "ஊ",
    "v": "எ", "V": "ஏ", "I": "ஐ", "x": "ஒ", "X": "ஓ", "xs": "ஔ",
    "f": "க", "q": "ங", "r": "ச", "Q": "ஞ", "l": "ட", "z": "ண",
    "j": "த", "e": "ந", "g": "ப", "k": "ம", "a": "ய", "u": "ர",
    "y": "ல", "t": "வ", "o": "ழ", "s": "ள", "w": "ற", "d": "ன",
    "h": "ா", "p": "ி", "P": "ீ", "F": "கு", "R": "சு", "L": "டு",
    "Z": "ணு", "J": "து", "E": "நு", "G": "பு", "K": "மு", "A": "யு",
    "U": "ரு", "Y": "லு", "T": "வு", "O": "ழு", "S": "ளு", "W": "று",
    "D": "னு", "n": "ெ", "N": "ே", "i": "ை", ";": "்",
}

TAB_MAP = {
    "Ü": "அ", "Ý": "ஆ", "Þ": "இ", "ß": "ஈ", "à": "உ", "á": "ஊ",
    "â": "எ", "ã": "ஏ", "ä": "ஐ", "å": "ஒ", "æ": "ஓ", "ç": "ஔ",
    "è": "க", "é": "ங", "ê": "ச", "ë": "ஞ", "ì": "ட", "í": "ண",
    "î": "த", "ï": "ந", "ð": "ப", "ñ": "ம", "ò": "ய", "ó": "ர",
    "ô": "ல", "õ": "வ", "ö": "ழ", "÷": "ள", "ø": "ற", "ù": "ன",
    "¡": "ா", "¢": "ி", "£": "ீ", "¤": "ு", "¥": "ூ",
    "¦": "ெ", "§": "ே", "¨": "ை", "¬": "்",
}

TAM_MAP = {
    "¡": "அ", "¢": "ஆ", "£": "இ", "¤": "ஈ", "¥": "உ", "¦": "ஊ",
    "§": "எ", "¨": "ஏ", "©": "ஐ", "ª": "ஒ", "«": "ஓ", "¬": "ஔ",
    "­": "க", "®": "ங", "¯": "ச", "°": "ஞ", "±": "ட", "²": "ண",
    "³": "த", "´": "ந", "µ": "ப", "¶": "ம", "·": "ய", "¸": "ர",
    "¹": "ல", "º": "வ", "»": "ழ", "¼": "ள", "½": "ற", "¾": "ன",
    "¿": "ா", "À": "ி", "Á": "ீ", "Â": "ு", "Ã": "ூ",
    "Ä": "ெ", "Å": "ே", "Æ": "ை", "Ç": "்",
}


def _apply_legacy_to_unicode(text: str, mapping: dict) -> str:
    out = text
    # நீளமான குறியீடுகளை முதலில் மாற்றல்
    for k in sorted(mapping.keys(), key=len, reverse=True):
        out = out.replace(k, mapping[k])
    # கொம்பு எழுத்துகளை (ெ, ே, ை) உயிர்மெய் ஒழுங்கிற்கு மாற்றல்
    out = re.sub(r"([ெேை])([க-ஹ])", r"\2\1", out)
    # ொ, ோ, ௌ இணைப்புச் சீரமைப்பு
    out = out.replace("ொ", "ொ").replace("ோ", "ோ").replace("ெள", "ௌ")
    return out


def _apply_unicode_to_legacy(text: str, mapping: dict) -> str:
    rev_map = {v: k for k, v in mapping.items()}
    out = text.replace("ொ", "ொ").replace("ோ", "ோ").replace("ௌ", "ெள")
    out = re.sub(r"([க-ஹ])([ெேை])", r"\2\1", out)
    for k in sorted(rev_map.keys(), key=len, reverse=True):
        out = out.replace(k, rev_map[k])
    return out


def convert_encoding(text: str, mode: str) -> str:
    """TSCII, Bamini, TAB, TAM மற்றும் Unicode இடையே மாற்றும்."""
    if mode == "TSCII -> Unicode (ஒருங்குறி)":
        return _apply_legacy_to_unicode(text, TSCII_MAP)
    elif mode == "Unicode -> TSCII":
        return _apply_unicode_to_legacy(text, TSCII_MAP)
    elif mode == "Bamini (பாமினி) -> Unicode (ஒருங்குறி)":
        return _apply_legacy_to_unicode(text, BAMINI_MAP)
    elif mode == "Unicode -> Bamini (பாமினி)":
        return _apply_unicode_to_legacy(text, BAMINI_MAP)
    elif mode == "TAB -> Unicode (ஒருங்குறி)":
        return _apply_legacy_to_unicode(text, TAB_MAP)
    elif mode == "Unicode -> TAB":
        return _apply_unicode_to_legacy(text, TAB_MAP)
    elif mode == "TAM -> Unicode (ஒருங்குறி)":
        return _apply_legacy_to_unicode(text, TAM_MAP)
    elif mode == "Unicode -> TAM":
        return _apply_unicode_to_legacy(text, TAM_MAP)
    return text


# ---------------------------------------------------------
# 3. சந்திப்பிழை திருத்தி (Sandhi Checker)
# ---------------------------------------------------------
SANDHI_RULES = [
    (r"\b(அந்த|இந்த|எந்த)\s+([கசதப])", r"\1 \2்\2", "சுட்டெழுத்துப் பின் வல்லினம் மிகும் (எ.கா: அந்தக் கடிதம்)"),
    (r"\b(மிக|மிகவும்)\s+([கசதப])", r"\1 \2்\2", "'மிக' என்னும் உரிச்சொல் பின் வல்லினம் மிகும்"),
    (r"\b(தனி|புது|பொது)\s+([கசதப])", r"\1 \2்\2", "பண்புத்தொகை/நிலைமொழிப் பின் வல்லினம் மிகும்"),
    (r"([அ-ஔக-ஹா-ௌ])க்கு\s+([கசதப])", r"\1க்கு \2்\2", "நான்காம் வேற்றுமை உருபு ('கு') பின் வல்லினம் மிகும்"),
    (r"([அ-ஔக-ஹா-ௌ])ஐ\s+([கசதப])", r"\1ஐ \2்\2", "இரண்டாம் வேற்றுமை விரி ('ஐ') பின் வல்லினம் மிகும்"),
    (r"\b(இங்கு|அங்கு|எங்கு|இனி)\s+([கசதப])", r"\1 \2்\2", "இடப்பெயர்/இடைச்சொல் பின் வல்லினம் மிகும்"),
]


def check_sandhi(text: str):
    corrected = text
    notes = []
    for pattern, repl, desc in SANDHI_RULES:
        if re.search(pattern, corrected):
            corrected = re.sub(pattern, repl, corrected)
            notes.append(desc)
    return corrected, list(dict.fromkeys(notes))


# ---------------------------------------------------------
# 4. தமிழ்ச்சொல் சுட்டி & அகராதி (Word Suggester & Dictionary)
# ---------------------------------------------------------
def suggest_tamil_words(prefix: str):
    prefix = prefix.strip()
    if not prefix:
        return []
    return [w for w in TAMIL_DICTIONARY if w.startswith(prefix) or prefix in w]


def lookup_dictionary(query: str):
    query = query.strip()
    if not query:
        return None
    if query in TAMIL_DICTIONARY:
        return TAMIL_DICTIONARY[query]
    matches = {}
    q_lower = query.lower()
    for k, v in TAMIL_DICTIONARY.items():
        if (
            query in k
            or query in v.get("meaning", "")
            or any(query in s for s in v.get("synonyms", []))
            or q_lower in v.get("english", "").lower()
        ):
            matches[k] = v
    return matches if matches else None


# ---------------------------------------------------------
# 5. தமிழ் அகரவரிசைப்படுத்தம் (Tamil Alphabetical Sorting)
# ---------------------------------------------------------
TAMIL_ORDER = (
    "அஆஇஈஉஊஎஏஐஒஓஔஃ"
    "கஙசஞடணதநபமயரலவழளறன"
    "ாிீுூெேைொோௌ்"
)
ORDER_MAP = {ch: idx for idx, ch in enumerate(TAMIL_ORDER)}


def _tamil_sort_key(word: str):
    return [ORDER_MAP.get(ch, 1000 + ord(ch)) for ch in word.strip()]


def sort_tamil_lines(lines: list[str], reverse: bool = False) -> list[str]:
    cleaned = [line.strip() for line in lines if line.strip()]
    return sorted(cleaned, key=_tamil_sort_key, reverse=reverse)


# ---------------------------------------------------------
# 6. சொல்லடைவு உருவாக்கி (Word Indexing / Concordance)
# ---------------------------------------------------------
def build_word_index(text: str, min_length: int = 2):
    lines = text.splitlines()
    word_lines = {}
    counter = Counter()

    for line_no, line in enumerate(lines, 1):
        tokens = re.findall(r"[\u0B80-\u0BFF]+", line)
        for tok in tokens:
            if len(tok) >= min_length:
                counter[tok] += 1
                word_lines.setdefault(tok, set()).add(line_no)

    index_rows = []
    for word in sort_tamil_lines(list(counter.keys())):
        index_rows.append({
            "சொல்": word,
            "எண்ணிக்கை": counter[word],
            "வரி எண்கள்": ", ".join(map(str, sorted(word_lines[word]))),
        })
    return index_rows


# ---------------------------------------------------------
# 7. துணைநூற்பட்டியல் உருவாக்கி (Bibliography Formatter)
# ---------------------------------------------------------
def format_bibliography(
    author: str,
    year: str,
    title: str,
    publisher: str,
    place: str = "",
    style: str = "தமிழ் ஆய்வு நடை (Inam Style)",
) -> str:
    author = author.strip()
    year = year.strip()
    title = title.strip()
    publisher = publisher.strip()
    place = place.strip()

    if style == "APA 7th Style":
        loc = f"{place}: " if place else ""
        return f"{author} ({year}). *{title}*. {loc}{publisher}."
    elif style == "MLA 9th Style":
        return f"{author}. *{title}*. {publisher}, {year}."
    else:
        loc = f", {place}" if place else ""
        return f"{author}, **{title}**, {publisher}{loc}, {year}."


# ---------------------------------------------------------
# 8. எண் <-> எழுத்து மாற்றி (Number to Tamil Words Converter)
# ---------------------------------------------------------
ONES = ["", "ஒன்று", "இரண்டு", "மூன்று", "நான்கு", "ஐந்து", "ஆறு", "ஏழு", "எட்டு", "ஒன்பது"]
TENS_PREFIX = [
    "", "பத்து", "இருபத்து", "முப்பத்து", "நாற்பத்து",
    "ஐம்பத்து", "அறுபத்து", "எழுபத்து", "எண்பத்து", "தொண்ணூற்று",
]
TENS_EXACT = [
    "", "பத்து", "இருபது", "முப்பது", "நாற்பது",
    "ஐம்பது", "அறுபது", "எழுபது", "எண்பது", "தொண்ணூறு",
]
TEENS = {
    10: "பத்து", 11: "பதினொன்று", 12: "பன்னிரண்டு", 13: "பதின்மூன்று",
    14: "பதினான்கு", 15: "பதினைந்து", 16: "பதினாறு", 17: "பதினேழு",
    18: "பதினெட்டு", 19: "பத்தொன்பது",
}
HUNDREDS_PREFIX = [
    "", "நூற்று", "இருநூற்று", "முந்நூற்று", "நானூற்று",
    "ஐந்நூற்று", "அறுநூற்று", "எழுநூற்று", "எண்ணூற்று", "தொள்ளாயிரத்து",
]
HUNDREDS_EXACT = [
    "", "நூறு", "இருநூறு", "முந்நூறு", "நானூறு",
    "ஐந்நூறு", "அறுநூறு", "எழுநூறு", "எண்ணூறு", "தொள்ளாயிரம்",
]


def _two_digits(n: int) -> str:
    if n == 0:
        return ""
    if n < 10:
        return ONES[n]
    if 10 <= n <= 19:
        return TEENS[n]
    t, o = divmod(n, 10)
    return TENS_EXACT[t] if o == 0 else f"{TENS_PREFIX[t]} {ONES[o]}"


def _three_digits(n: int) -> str:
    if n == 0:
        return ""
    if n < 100:
        return _two_digits(n)
    h, rem = divmod(n, 100)
    return HUNDREDS_EXACT[h] if rem == 0 else f"{HUNDREDS_PREFIX[h]} {_two_digits(rem)}"


def number_to_tamil_words(num: int) -> str:
    if num == 0:
        return "சுழியம்"
    if num < 0:
        return "கழித்தல் " + number_to_tamil_words(abs(num))

    parts = []
    crore, rem = divmod(num, 10_000_000)
    lakh, rem = divmod(rem, 100_000)
    thousand, rem = divmod(rem, 1_000)

    if crore:
        parts.append("ஒரு கோடி" if crore == 1 else f"{_three_digits(crore)} கோடி")
    if lakh:
        parts.append("ஒரு இலட்சம்" if lakh == 1 else f"{_two_digits(lakh)} இலட்சம்")
    if thousand:
        if thousand == 1:
            parts.append("ஆயிரம்" if rem == 0 else "ஆயிரத்து")
        else:
            t_str = _two_digits(thousand)
            parts.append(f"{t_str} ஆயிரம்" if rem == 0 else f"{t_str} ஆயிரத்து")
    if rem:
        parts.append(_three_digits(rem))

    return " ".join(parts).strip()


TAMIL_WORD_TO_NUM = {
    "சுழியம்": 0, "பூஜ்ஜியம்": 0,
    "ஒன்று": 1, "ஒரு": 1, "இரண்டு": 2, "இரு": 2, "மூன்று": 3, "நான்கு": 4,
    "ஐந்து": 5, "ஆறு": 6, "ஏழு": 7, "எட்டு": 8, "ஒன்பது": 9,
    "பத்து": 10, "பதினொன்று": 11, "பன்னிரண்டு": 12, "பதின்மூன்று": 13,
    "பதினான்கு": 14, "பதினைந்து": 15, "பதினாறு": 16, "பதினேழு": 17,
    "பதினெட்டு": 18, "பத்தொன்பது": 19,
    "இருபது": 20, "இருபத்து": 20, "முப்பது": 30, "முப்பத்து": 30,
    "நாற்பது": 40, "நாற்பத்து": 40, "ஐம்பது": 50, "ஐம்பத்து": 50,
    "அறுபது": 60, "அறுபத்து": 60, "எழுபது": 70, "எழுபத்து": 70,
    "எண்பது": 80, "எண்பத்து": 80, "தொண்ணூறு": 90, "தொண்ணூற்று": 90,
    "நூறு": 100, "நூற்று": 100, "இருநூறு": 200, "இருநூற்று": 200,
    "முந்நூறு": 300, "முந்நூற்று": 300, "நானூறு": 400, "நானூற்று": 400,
    "ஐந்நூறு": 500, "ஐந்நூற்று": 500, "அறுநூறு": 600, "அறுநூற்று": 600,
    "எழுநூறு": 700, "எழுநூற்று": 700, "எண்ணூறு": 800, "எண்ணூற்று": 800,
    "தொள்ளாயிரம்": 900, "தொள்ளாயிரத்து": 900,
}

MULTIPLIERS = {
    "ஆயிரம்": 1_000, "ஆயிரத்து": 1_000,
    "இலட்சம்": 100_000, "லட்சம்": 100_000,
    "கோடி": 10_000_000,
}


def tamil_words_to_number(phrase: str) -> int:
    tokens = phrase.strip().split()
    total = 0
    current = 0
    for tok in tokens:
        if tok in MULTIPLIERS:
            mult = MULTIPLIERS[tok]
            current = (current if current > 0 else 1) * mult
            total += current
            current = 0
        elif tok in TAMIL_WORD_TO_NUM:
            current += TAMIL_WORD_TO_NUM[tok]
    return total + current
