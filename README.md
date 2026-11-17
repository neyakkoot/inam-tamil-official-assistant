
# இனம் – தமிழ் அலுவல் உதவி

**Inam – Tamil Official Assistant**

தமிழ் மொழித்திருத்தம், அலுவல் மொழிநடை மேம்பாடு மற்றும் தமிழ் அலுவலக ஆவணங்களை உருவாக்குவதற்கான கட்டற்ற இணையச் செயலி.

## பதிப்பு 1.1 – முக்கிய அம்சங்கள்

- அடிப்படைத் தமிழ் சொற்றொடர் மற்றும் இடைவெளித் திருத்தம்.
- அலுவல் மொழிநடையாக மாற்றும் வசதி.
- பரிந்துரைக்கப்படும் திருத்தங்களுக்கான காரண விளக்கம்.
- எட்டு வகையான அலுவல் ஆவணங்களை உருவாக்குதல்.
- Word (DOCX), TXT மற்றும் HTML கோப்புகளாகப் பதிவிறக்குதல்.
- விருப்பத்தேர்வாக AI மூலம் மொழிநடை மேம்பாடு.

## ஆதரிக்கப்படும் ஆவண வகைகள்

1. அலுவல் கடிதம்
2. அலுவலகக் குறிப்பு
3. அறிக்கை
4. சுற்றறிக்கை
5. குறிப்பாணை
6. அரசாணை வரைவு
7. கூட்ட நடவடிக்கைக் குறிப்புகள்
8. நினைவூட்டல் கடிதம்

## தொழில்நுட்பக் கட்டமைப்பு

- Python
- Streamlit
- Python-docx
- OpenAI API (விருப்பத்தேர்வு)

## நிறுவுதல் மற்றும் இயக்குதல்

```bash
pip install -r requirements.txt
streamlit run app.py
```

## இணையத்தில் வெளியிடுதல்

Streamlit Community Cloud மூலம் வெளியிடப்பட்டுள்ளது.

செயலியின் இணைய முகவரி:

https://inam-tamil-official-assistant.streamlit.app/

## தற்போதைய வரம்புகள்

இது தொடக்கநிலைத் திட்ட மாதிரி மட்டுமே. முழுமையான தமிழ் இலக்கணச் சரிபார்ப்பி அல்ல.

ண/ந/ன, ல/ள/ழ, ர/ற போன்ற சூழல் சார்ந்த எழுத்து வேறுபாடுகளைத் தானாக மாற்றாது.

அனைத்து அலுவல் ஆவணங்களும் அதிகாரப்பூர்வப் பயன்பாட்டிற்கு முன்பு உரிய அலுவலரால் சரிபார்க்கப்பட வேண்டும்.

## தனியுரிமை

உரிய அனுமதியின்றி ரகசிய அரசு ஆவணங்களை வெளிப்புற AI சேவைகளுக்கு அனுப்ப வேண்டாம்.

## உரிமம்

இந்தக் களஞ்சியத்தில் புதிதாக உருவாக்கப்பட்ட நிரல் குறியீட்டிற்கு மட்டுமே MIT உரிமம் பொருந்தும். மூன்றாம் தரப்பு மென்பொருள்கள், எழுத்துருக்கள், தரவுத்தொகுப்புகள் மற்றும் அரசு வளங்களுக்கு அவற்றின் தனிப்பட்ட உரிம நிபந்தனைகளே பொருந்தும்.

## நன்றியுரை

தமிழ் மொழியை அரசு நிர்வாகம், கல்வி, பொதுத் தொடர்புகளில் மேம்படுத்தும் நோக்கில் இத்திட்டம் உருவாக்கப்பட்டுள்ளது.

# Inam – Tamil Official Assistant

An open-source web application for Tamil language correction, official language refinement and Tamil government document drafting.

https://inam-tamil-official-assistant.streamlit.app/

## Features – Version 1.1

- Basic Tamil phrase and spacing corrections.
- Optional official-style language transformation.
- Explanation of suggested corrections.
- Eight types of official document drafts.
- Word (DOCX), TXT and HTML export.
- Optional AI-powered language improvement.

## Supported Document Types

1. Official Letter
2. Office Note
3. Report
4. Circular
5. Memorandum
6. Government Order Draft
7. Meeting Minutes
8. Reminder Letter

## Technology Stack

- Python
- Streamlit
- Python-docx
- OpenAI API (optional)

## Installation

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment

Deployed using Streamlit Community Cloud.

## Limitations

This is an early-stage prototype, not a complete Tamil grammar checker.

Context-sensitive Tamil letters such as ண/ந/ன, ல/ள/ழ and ர/ற are not automatically modified.

All official documents must be reviewed by an authorized person before use.

## Privacy

Do not submit confidential government documents to external AI services without authorization.

## License

The MIT License applies only to the original software code in this repository. Third-party libraries, fonts, datasets and government materials retain their respective licenses.

## Acknowledgement

Developed to support Tamil language use in official administration, education and public communication.
