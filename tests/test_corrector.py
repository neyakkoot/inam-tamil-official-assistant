from inam.corrector import correct_text, convert_to_official_style


def test_phrase_correction():
    result, findings = correct_text("மாணவர்கள் கலந்து கொள்ள வேண்டும்.")
    assert "கலந்துகொள்ள" in result
    assert findings


def test_unknown_text_is_preserved():
    text = "இது ஒரு சோதனை வாக்கியம்."
    result, _ = correct_text(text)
    assert result == text


def test_official_style_conversion():
    result, notes = convert_to_official_style("விவரங்களை அனுப்பி வைக்கவும்.")
    assert "கேட்டுக்கொள்ளப்படுகிறது" in result
    assert notes
