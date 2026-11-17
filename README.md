
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
