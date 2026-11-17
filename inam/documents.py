DOCUMENT_TYPES = {
    "அலுவல் கடிதம்": "letter",
    "அலுவலகக் குறிப்பு": "office_note",
    "அறிக்கை": "report",
    "சுற்றறிக்கை": "circular",
    "குறிப்பாணை": "memorandum",
    "அரசாணை வரைவு": "go_draft",
    "கூட்ட நடவடிக்கைக் குறிப்புகள்": "minutes",
    "நினைவூட்டல் கடிதம்": "reminder",
}

def build_document(doc_type, office, recipient, date, reference, subject, body, place, signatory):
    lines = []
    if office.strip():
        lines.append(office.strip())
        lines.append("")
    if reference.strip():
        lines.append(f"ந.க.எண்: {reference.strip()}")
    if date.strip():
        lines.append(f"நாள்: {date.strip()}")
    if recipient.strip():
        lines.extend(["", f"பெறுநர்:", recipient.strip()])
    if subject.strip():
        lines.extend(["", f"பொருள்: {subject.strip()}"])
    if doc_type == "கூட்ட நடவடிக்கைக் குறிப்புகள்":
        lines.extend(["", "கூட்ட நடவடிக்கைக் குறிப்புகள்", "", "கூட்டத்தின் விவரங்கள்:", body.strip()])
    elif doc_type == "அரசாணை வரைவு":
        lines.extend(["", "வரைவு – சரிபார்ப்பிற்காக மட்டும்", "", "ஆணை:", body.strip()])
        lines.append("")
        lines.append("குறிப்பு: இது வரைவு மட்டுமே; உரிய அதிகாரியின் பரிசீலனை மற்றும் ஒப்புதல் அவசியம்.")
    elif doc_type == "அலுவலகக் குறிப்பு":
        lines.extend(["", "அலுவலகக் குறிப்பு", "", "குறிப்பு:", body.strip(), "", "மேற்கண்ட விவகாரம் பரிசீலனைக்காக சமர்ப்பிக்கப்படுகிறது."])
    elif doc_type == "அறிக்கை":
        lines.extend(["", "அறிக்கை", "", body.strip()])
    elif doc_type == "சுற்றறிக்கை":
        lines.extend(["", "சுற்றறிக்கை", "", body.strip()])
    elif doc_type == "குறிப்பாணை":
        lines.extend(["", "குறிப்பாணை", "", body.strip()])
    elif doc_type == "நினைவூட்டல் கடிதம்":
        lines.extend(["", "நினைவூட்டல்", "", body.strip()])
    else:
        lines.extend(["", "அலுவல் கடிதம்", "", body.strip()])
    if place.strip():
        lines.extend(["", f"இடம்: {place.strip()}"])
    if signatory.strip():
        lines.extend(["", "", signatory.strip()])
    return "\n".join(lines).strip() + "\n"
