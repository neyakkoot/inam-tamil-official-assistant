
from inam.corrector import correct_text, convert_to_official_style


def test_phrase_correction():
    result, findings = correct_text(
        "கூட்டத்தில் கலந்து கொள்ள வேண்டும்."
    )
    assert "கலந்துகொள்ள" in result
    assert findings


def test_unknown_text_unchanged():
    text = "இது ஒரு சோதனை வாக்கியம்."
    result, findings = correct_text(text)
    assert result == text
    assert findings


def test_official_style():
    result, notes = convert_to_official_style(
        "விவரங்களை அனுப்பி வைக்கவும்."
    )
    assert "கேட்டுக்கொள்ளப்படுகிறது" in result
    assert notes


def test_no_guessing_tamil_letter_variants():
    text = "அவன் பள்ளிக்கு சென்றான்."
    result, findings = correct_text(text)
    assert result == text
