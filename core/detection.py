import re


def get_requiredness(text: str | None) -> str | None:
    """Identify simple required/optional language."""
    if not text:
        return None

    text = text.casefold()

    if re.search(r"\b(not required|optional)\b", text):
        return "optional"

    if re.search(r"\brequired\b", text):
        return "required"

    return None

#requiredness
def detect_requiredness_changes(comparisons: list[dict]) -> list[dict]:
    findings = []

    for section in comparisons:
        for difference in section["differences"]:
            change_type = difference["status"]

            if change_type not in {"modified", "added", "removed"}:
                continue

            reference = difference["reference_text"]
            incoming = difference["incoming_text"]

            old_state = get_requiredness(reference)
            new_state = get_requiredness(incoming)

            # Case 1: Modified — confirmed keyword-level state change
            if change_type == "modified":
                if (
                    old_state is not None
                    and new_state is not None
                    and old_state != new_state
                ):
                    findings.append({
                        "category": "required_optional",
                        "section": section["section_key"],
                        "change_type": "modified",
                        "reference_text": reference,
                        "incoming_text": incoming,
                        "old_state": old_state,
                        "new_state": new_state,
                        "status": "needs_review",
                    })

            # Case 2: Added — new statement about requiredness
            elif change_type == "added" and new_state is not None:
                findings.append({
                    "category": "required_optional",
                    "section": section["section_key"],
                    "change_type": "added",
                    "reference_text": None,
                    "incoming_text": incoming,
                    "old_state": None,
                    "new_state": new_state,
                    "status": "needs_review",
                })

            # Case 3: Removed — deleted statement about requiredness
            elif change_type == "removed" and old_state is not None:
                findings.append({
                    "category": "required_optional",
                    "section": section["section_key"],
                    "change_type": "removed",
                    "reference_text": reference,
                    "incoming_text": None,
                    "old_state": old_state,
                    "new_state": None,
                    "status": "needs_review",
                })

    return findings

INVESTOR_TYPE_KEYWORDS = {
    "individual": [
        "individual investor",
        "individual investors",
    ],
    "legal_entity": [
        "legal entity",
        "legal entities",
        "entity investors",
    ],
}


def get_investor_types(text: str | None) -> set[str]:
    if not text:
        return set()

    text = text.casefold()
    detected = set()

    for investor_type, keywords in INVESTOR_TYPE_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            detected.add(investor_type)

    return detected

#investor_type
def detect_investor_type_changes(comparisons: list[dict]) -> list[dict]:
    findings = []

    for section in comparisons:
        if section["section_key"] != "investor information":
            continue
        for difference in section["differences"]:
            change_type = difference["status"]

            if change_type not in {"modified", "added", "removed"}:
                continue

            reference = difference["reference_text"]
            incoming = difference["incoming_text"]

            # Only detect statements defining who the form is intended for.
            scope_phrases = (
                "intended for",
                "open to",
                "available to",
                "eligible investors",
            )

            combined_text = f"{reference or ''} {incoming or ''}".casefold()

            if not any(phrase in combined_text for phrase in scope_phrases):
                continue

            old_types = get_investor_types(reference)
            new_types = get_investor_types(incoming)

            # A modified sentence introduces or removes an investor type.
            if change_type == "modified":
                added_types = new_types - old_types
                removed_types = old_types - new_types

                if not added_types and not removed_types:
                    continue

            # An added/removed sentence mentions an investor type.
            # Do not assume this changes the form's supported investor types.
            elif change_type == "added":
                if not new_types:
                    continue
                added_types = set()
                removed_types = set()

            else:
                if not old_types:
                    continue
                added_types = set()
                removed_types = set()

            findings.append({
                "category": "investor_types",
                "section": section["section_key"],
                "change_type": change_type,
                "reference_text": reference,
                "incoming_text": incoming,
                "added_types": sorted(added_types),
                "removed_types": sorted(removed_types),
                "status": "needs_review",
            })

    return findings


def has_conditional_logic(text: str | None) -> bool:
    if not text:
        return False

    text = text.casefold()

    conditional_phrases = (
        "if ",
        "when ",
        "depending on ",
        "based on ",
        "only if ",
        "unless ",
    )

    return any(
        phrase in text
        for phrase in conditional_phrases
    )


def detect_conditional_logic_changes(comparisons: list[dict]) -> list[dict]:
    findings = []

    for section in comparisons:
        for difference in section["differences"]:
            change_type = difference["status"]

            if change_type not in {"modified", "added", "removed"}:
                continue

            reference = difference["reference_text"]
            incoming = difference["incoming_text"]

            old_conditional = has_conditional_logic(reference)
            new_conditional = has_conditional_logic(incoming)

            if change_type == "modified":
                # A new condition appeared or an existing one changed.
                if not new_conditional and not old_conditional:
                    continue

                # Ignore identical statements.
                if reference == incoming:
                    continue

            elif change_type == "added":
                if not new_conditional:
                    continue

            elif change_type == "removed":
                if not old_conditional:
                    continue

            findings.append({
                "category": "conditional_logic",
                "section": section["section_key"],
                "change_type": change_type,
                "reference_text": reference,
                "incoming_text": incoming,
                "status": "needs_review",
            })

    return findings


SUPPORTING_DOCUMENT_KEYWORDS = (
    "government-issued identification",
    "proof of address",
    "proof of residential address",
    "certificate of incorporation",
    "irs form w-9",
    "form w-9",
    "form w-8ben",
    "w-8ben-e",
    "identification document",
    "identification for",
    "must upload",
)


def has_supporting_document(text: str | None) -> bool:
    if not text:
        return False

    text = text.casefold()

    return any(
        keyword in text
        for keyword in SUPPORTING_DOCUMENT_KEYWORDS
    )


def detect_supporting_document_changes(comparisons: list[dict]) -> list[dict]:
    findings = []

    for section in comparisons:
        for difference in section["differences"]:
            change_type = difference["status"]

            if change_type not in {"modified", "added", "removed"}:
                continue

            reference = difference["reference_text"]
            incoming = difference["incoming_text"]

            if not (
                has_supporting_document(reference)
                or has_supporting_document(incoming)
            ):
                continue

            findings.append({
                "category": "supporting_documents",
                "section": section["section_key"],
                "change_type": change_type,
                "reference_text": reference,
                "incoming_text": incoming,
                "status": "needs_review",
            })

    return findings


import re


VALIDATION_PATTERNS = (
    r"\bminimum\b",
    r"\bmaximum\b",
    r"\bat least\b",
    r"\bat most\b",
    r"\bmust not be earlier than\b",
    r"\bmust not be later than\b",
    r"\bcannot exceed\b",
    r"\bmust be greater than\b",
    r"\bmust be less than\b",
)


def has_validation_rule(text: str | None) -> bool:
    if not text:
        return False

    return any(
        re.search(pattern, text, flags=re.IGNORECASE)
        for pattern in VALIDATION_PATTERNS
    )


def detect_validation_changes(comparisons: list[dict]) -> list[dict]:
    findings = []

    for section in comparisons:
        for difference in section["differences"]:
            change_type = difference["status"]

            if change_type not in {"modified", "added", "removed"}:
                continue

            reference = difference["reference_text"]
            incoming = difference["incoming_text"]

            if not (
                has_validation_rule(reference)
                or has_validation_rule(incoming)
            ):
                continue

            findings.append({
                "category": "validation",
                "section": section["section_key"],
                "change_type": change_type,
                "reference_text": reference,
                "incoming_text": incoming,
                "status": "needs_review",
            })

    return findings


SIGNATURE_KEYWORDS = (
    "handwritten signature",
    "electronically",
    "electronic signature",
    "e-signature",
    "signatory",
    "signatories",
    "must sign",
    "may sign",
    "sign on behalf",
    "signing authority",
)


def has_signature_requirement(text: str | None) -> bool:
    if not text:
        return False

    text = text.casefold()

    return any(
        keyword in text
        for keyword in SIGNATURE_KEYWORDS
    )


def detect_signature_changes(comparisons: list[dict]) -> list[dict]:
    findings = []

    for section in comparisons:
        for difference in section["differences"]:
            change_type = difference["status"]

            if change_type not in {"modified", "added", "removed"}:
                continue

            reference = difference["reference_text"]
            incoming = difference["incoming_text"]

            if not (
                has_signature_requirement(reference)
                or has_signature_requirement(incoming)
            ):
                continue

            findings.append({
                "category": "signatures",
                "section": section["section_key"],
                "change_type": change_type,
                "reference_text": reference,
                "incoming_text": incoming,
                "status": "needs_review",
            })

    return findings


def detect_all_findings(comparisons: list[dict]) -> list[dict]:
    detectors = [
        detect_requiredness_changes,
        detect_investor_type_changes,
        detect_conditional_logic_changes,
        detect_supporting_document_changes,
        detect_validation_changes,
        detect_signature_changes,
    ]

    combined = {}

    for detector in detectors:
        for finding in detector(comparisons):
            key = (
                finding["section"],
                finding["change_type"],
                finding["reference_text"],
                finding["incoming_text"],
            )

            if key not in combined:
                combined[key] = {
                    "section": finding["section"],
                    "change_type": finding["change_type"],
                    "reference_text": finding["reference_text"],
                    "incoming_text": finding["incoming_text"],
                    "categories": [],
                    "status": "needs_review",
                }

            category = finding["category"]

            if category not in combined[key]["categories"]:
                combined[key]["categories"].append(category)
        
    # Fallback: surface differences not covered by the six detectors
    for section in comparisons:
        for difference in section["differences"]:
            change_type = difference["status"]

            if change_type not in {"modified", "added", "removed"}:
                continue

            key = (
                section["section_key"],
                change_type,
                difference["reference_text"],
                difference["incoming_text"],
            )

            if key in combined:
                continue

            combined[key] = {
                "section": section["section_key"],
                "change_type": change_type,
                "reference_text": difference["reference_text"],
                "incoming_text": difference["incoming_text"],
                "categories": ["others"],
                "status": "needs_review",
            }

    return list(combined.values())