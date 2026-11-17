from inam.corrector import correct_text

def test_known_phrase_replacement():
    result, notes = correct_text("கூட்டத்தில் கலந்து கொள்ள வேண்டும்.")
    assert "கலந்துகொள்ள" in result
    assert notes

def test_unknown_text_is_not_changed():
    text = "இது ஒரு சோதனை வாக்கியம்."
    result, _ = correct_text(text)
    assert result == text
