DOCUMENT_TYPES = {
    "அலுவல் கடிதம்": "letter",
    "அலுவலகக் குறிப்பு": "office_note",
    "அறிக்கை": "report",
    "சுற்றறிக்கை": "circular",
    "குறிப்பாணை": "memorandum",
    "அரசாணை": "government_order",
    "அரசாணை வரைவு": "go_draft",
    "பாராட்டுக் கடிதம்": "appreciation_letter",
    "கூட்ட நடவடிக்கைக் குறிப்புகள்": "minutes",
    "நினைவூட்டல் கடிதம்": "reminder",
    "அழைப்பிதழ்": "invitation",
    "பணிச்சான்றிதழ்": "service_certificate",
}


def build_document(
    doc_type,
    office,
    recipient,
    date,
    reference,
    subject,
    body,
    place,
    signatory,
):
    lines = []

    if office.strip():
        lines.extend([office.strip(), ""])

    if doc_type in ("அரசாணை", "அரசாணை வரைவு"):
        if subject.strip():
            lines.extend([f"சுருக்கம்: {subject.strip()}", ""])
        if reference.strip():
            lines.append(f"அரசாணை எண்: {reference.strip()}")
        if date.strip():
            lines.append(f"நாள்: {date.strip()}")
        if doc_type == "அரசாணை வரைவு":
            lines.extend(["", "வரைவு – சரிபார்ப்பிற்காக மட்டும்"])
        lines.extend(["", "ஆணை:", "", body.strip()])
        if doc_type == "அரசாணை":
            lines.extend(["", "(ஆளுநரின் ஆணைப்படி)"])
        else:
            lines.extend(
                [
                    "",
                    "குறிப்பு: இது வரைவு மட்டுமே; உரிய அதிகாரியின் "
                    "பரிசீலனை மற்றும் ஒப்புதல் அவசியம்.",
                ]
            )
        if signatory.strip():
            lines.extend(["", signatory.strip()])
        if recipient.strip():
            lines.extend(["", "பெறுநர்:", recipient.strip()])
        return "\n".join(lines).strip() + "\n"

    if reference.strip():
        lines.append(f"ந.க.எண்: {reference.strip()}")

    if date.strip():
        lines.append(f"நாள்: {date.strip()}")

    if doc_type == "சுற்றறிக்கை":
        lines.extend(["", "சுற்றறிக்கை"])
        if subject.strip():
            lines.extend(["", f"பொருள்: {subject.strip()}"])
        lines.extend(["", body.strip()])
        if place.strip():
            lines.extend(["", f"இடம்: {place.strip()}"])
        if signatory.strip():
            lines.extend(["", "", signatory.strip()])
        if recipient.strip():
            lines.extend(["", "பெறுநர் / நகல்:", recipient.strip()])
        return "\n".join(lines).strip() + "\n"

    if doc_type == "குறிப்பாணை":
        lines.extend(["", "குறிப்பாணை"])
        if subject.strip():
            lines.extend(["", f"பொருள்: {subject.strip()}"])
        lines.extend(["", body.strip()])
        if place.strip():
            lines.extend(["", f"இடம்: {place.strip()}"])
        if signatory.strip():
            lines.extend(["", "", signatory.strip()])
        if recipient.strip():
            lines.extend(["", "பெறுநர்:", recipient.strip()])
        return "\n".join(lines).strip() + "\n"

    if doc_type == "பாராட்டுக் கடிதம்":
        lines.extend(["", "பாராட்டுக் கடிதம்"])
        if recipient.strip():
            lines.extend(["", "பெறுநர்:", recipient.strip()])
        if subject.strip():
            lines.extend(["", f"பொருள்: {subject.strip()}"])
        lines.extend(["", "அன்புடையீர் / மதிப்பிற்குரியீர்,", "", body.strip()])
        if place.strip():
            lines.extend(["", f"இடம்: {place.strip()}"])
        if signatory.strip():
            lines.extend(["", "", signatory.strip()])
        return "\n".join(lines).strip() + "\n"

    if recipient.strip():
        lines.extend(["", "பெறுநர்:", recipient.strip()])

    if subject.strip():
        lines.extend(["", f"பொருள்: {subject.strip()}"])

    if doc_type == "கூட்ட நடவடிக்கைக் குறிப்புகள்":
        lines.extend(
            ["", "கூட்ட நடவடிக்கைக் குறிப்புகள்", "", "கூட்டத்தின் விவரங்கள்:", body.strip()]
        )
    elif doc_type == "அலுவலகக் குறிப்பு":
        lines.extend(
            [
                "",
                "அலுவலகக் குறிப்பு",
                "",
                "குறிப்பு:",
                body.strip(),
                "",
                "மேற்கண்ட விவகாரம் பரிசீலனைக்காக சமர்ப்பிக்கப்படுகிறது.",
            ]
        )
    elif doc_type == "அறிக்கை":
        lines.extend(["", "அறிக்கை", "", body.strip()])
    elif doc_type == "நினைவூட்டல் கடிதம்":
        lines.extend(["", "நினைவூட்டல் கடிதம்", "", "ஐயா / அம்மையீர்,", "", body.strip()])
    elif doc_type == "அழைப்பிதழ்":
        lines.extend(["", "அழைப்பிதழ்", "", "அன்புடையீர்,", "", body.strip()])
    elif doc_type == "பணிச்சான்றிதழ்":
        lines.extend(["", "பணிச்சான்றிதழ்", "", body.strip()])
    else:
        lines.extend(["", "அலுவல் கடிதம்", "", "ஐயா / அம்மையீர்,", "", body.strip()])

    if place.strip():
        lines.extend(["", f"இடம்: {place.strip()}"])

    if signatory.strip():
        lines.extend(["", "", signatory.strip()])

    return "\n".join(lines).strip() + "\n"
