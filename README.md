# இனம் – தமிழ் அலுவல் உதவி
**Inam – Tamil Official Assistant**

AI-assisted Tamil writing, proofreading and official document drafting for public-sector and general office workflows.

## Features in V1
- Tamil text input and editing
- Conservative starter phrase corrections (rule-based)
- Optional AI-assisted language refinement
- Draft templates for:
  - Official letter (அலுவல் கடிதம்)
  - Office note (அலுவலகக் குறிப்பு)
  - Report (அறிக்கை)
  - Circular (சுற்றறிக்கை)
  - Memorandum (குறிப்பாணை)
  - Government Order draft (அரசாணை வரைவு)
  - Meeting minutes (கூட்ட நடவடிக்கைக் குறிப்புகள்)
  - Reminder letter (நினைவூட்டல் கடிதம்)
- DOCX, TXT and HTML export (HTML can be printed to PDF)

## Run locally
1. Install Python 3.10 or later.
2. Open a terminal in this project folder.
3. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
   # macOS/Linux
   source .venv/bin/activate
   ```
4. Install packages:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the app:
   ```bash
   streamlit run app.py
   ```

## Optional AI setup
Set `OPENAI_API_KEY` and optionally `INAM_AI_MODEL` in your environment before starting the app. Do not commit API keys to GitHub. AI processing sends the entered text to the configured API provider. Do not submit confidential, personal, classified or otherwise sensitive government records unless the relevant authority has approved that processing and the provider's terms have been reviewed.

## Important limitations
- V1 rule-based corrections are only a small demonstration set, not a complete Tamil spellchecker or grammar checker.
- AI suggestions can be wrong. Always review the output.
- Names, dates, amounts, file numbers, legal references, government orders and factual details must be checked against source records.
- The Government Order draft is only a drafting scaffold, not an official or legally valid order.
- DOCX font rendering depends on fonts installed on the user's computer. Noto Sans Tamil or another suitable Tamil Unicode font is recommended.
- HTML export can be opened in a browser and printed to PDF. Check Tamil shaping and page layout before official use.

## Privacy and security
This prototype does not save submitted text to a project database. Streamlit hosting, server logs, browser state, and any configured AI provider may still process data. Deploy only after a privacy and security review. For sensitive workflows, prefer an approved, access-controlled local or government-hosted deployment.

## Suggested repository structure
```text
inam-tamil-official-assistant/
├── app.py
├── inam/
│   ├── __init__.py
│   ├── corrector.py
│   ├── ai_assistant.py
│   ├── documents.py
│   └── exporters.py
├── tests/
│   └── test_corrector.py
├── .env.example
├── .gitignore
├── LICENSE
├── requirements.txt
└── README.md
```

## License
The MIT License in this repository applies to the original source code authored for this project. It does not automatically apply to third-party packages, fonts, datasets, government documents or other external resources. Their respective licenses and terms remain applicable.
