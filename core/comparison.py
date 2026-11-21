import re
from difflib import SequenceMatcher


def split_into_sentences(text: str) -> list[str]:
    """
    Reconstruct wrapped PDF lines before splitting sentences.

    Designed for our controlled synthetic PDFs.
    """
    if not text:
        return []

    # Join PDF line wraps into continuous text.
    text = re.sub(r"\s+", " ", text).strip()

    # Split at sentence-ending punctuation.
    sentences = re.split(r"(?<=[.!?])\s+", text)

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def normalize_text(text: str) -> str:
    """Normalize whitespace and case without removing negation."""
    return re.sub(r"\s+", " ", text).strip().casefold()


def similarity(a: str, b: str) -> float:
    """Surface-level similarity, not semantic equivalence."""
    return SequenceMatcher(
        None,
        normalize_text(a),
        normalize_text(b),
    ).ratio()


def compare_units(
    reference_units: list[str],
    incoming_units: list[str],
    threshold: float = 0.55,
) -> list[dict]:
    """
    Align similar text units, then identify additions and removals.

    Important:
    A 'modified' result only means similar text with different
    wording. It does not establish a business requirement change.
    """
    results = []
    used_incoming = set()

    for reference in reference_units:
        best_index = None
        best_score = 0.0

        for index, incoming in enumerate(incoming_units):
            if index in used_incoming:
                continue

            score = similarity(reference, incoming)

            if score > best_score:
                best_score = score
                best_index = index

        if best_index is not None and best_score >= threshold:
            incoming = incoming_units[best_index]
            used_incoming.add(best_index)

            status = (
                "unchanged"
                if normalize_text(reference) == normalize_text(incoming)
                else "modified"
            )

            results.append({
                "status": status,
                "reference_text": reference,
                "incoming_text": incoming,
                "similarity": round(best_score, 3),
            })

        else:
            results.append({
                "status": "removed",
                "reference_text": reference,
                "incoming_text": None,
                "similarity": None,
            })

    for index, incoming in enumerate(incoming_units):
        if index not in used_incoming:
            results.append({
                "status": "added",
                "reference_text": None,
                "incoming_text": incoming,
                "similarity": None,
            })

    return results


def compare_sections(matched_sections: list[dict]) -> list[dict]:
    """Compare all matched sections and attach their source heading."""
    comparisons = []

    for section in matched_sections:
        reference_units = split_into_sentences(
            section["reference_text"] or ""
        )
        incoming_units = split_into_sentences(
            section["incoming_text"] or ""
        )

        differences = compare_units(
            reference_units,
            incoming_units,
        )

        comparisons.append({
            "section_key": section["section_key"],
            "section_status": section["status"],
            "differences": differences,
        })

    return comparisons
