import re


def normalize_section_name(title: str) -> str:
    """Remove numbering and normalize a section heading."""
    title = re.sub(r"^\s*\d+\.\s*", "", title)
    title = re.sub(r"\s+", " ", title)
    return title.strip().casefold()


def match_sections(
    reference_sections: dict[str, str],
    incoming_sections: dict[str, str],
) -> list[dict]:
    """Match reference and incoming sections by normalized heading."""

    reference_lookup = {
        normalize_section_name(title): (title, text)
        for title, text in reference_sections.items()
    }

    incoming_lookup = {
        normalize_section_name(title): (title, text)
        for title, text in incoming_sections.items()
    }

    results = []

    # Preserve reference document order.
    for key, (reference_title, reference_text) in reference_lookup.items():
        if key in incoming_lookup:
            incoming_title, incoming_text = incoming_lookup[key]
            status = "matched"
        else:
            incoming_title, incoming_text = None, None
            status = "removed"

        results.append({
            "section_key": key,
            "status": status,
            "reference_title": reference_title,
            "incoming_title": incoming_title,
            "reference_text": reference_text,
            "incoming_text": incoming_text,
        })

    # Add sections present only in the incoming document.
    for key, (incoming_title, incoming_text) in incoming_lookup.items():
        if key not in reference_lookup:
            results.append({
                "section_key": key,
                "status": "added",
                "reference_title": None,
                "incoming_title": incoming_title,
                "reference_text": None,
                "incoming_text": incoming_text,
            })

    return results
