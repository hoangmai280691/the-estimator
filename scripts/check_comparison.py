from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.document import extract_pdf_text, extract_sections
from core.matching import match_sections
from core.comparison import compare_sections


for pair in ("a", "b", "c"):
    folder = ROOT / "test_data" / f"pair_{pair}"

    reference = extract_sections(
        extract_pdf_text(
            folder / f"Pair_{pair.upper()}_Reference_Form.pdf"
        )
    )

    incoming = extract_sections(
        extract_pdf_text(
            folder / f"Pair_{pair.upper()}_Incoming_Form.pdf"
        )
    )

    matched = match_sections(reference, incoming)
    comparisons = compare_sections(matched)

    print(f"\n{'=' * 55}")
    print(f"PAIR {pair.upper()}")
    print(f"{'=' * 55}")

    counts = {
        "unchanged": 0,
        "modified": 0,
        "added": 0,
        "removed": 0,
    }

    for section in comparisons:
        print(f"\nSECTION: {section['section_key']}")

        for difference in section["differences"]:
            status = difference["status"]
            counts[status] += 1

            if status == "unchanged":
                continue

            print(f"  [{status.upper()}]")
            print(f"    REF: {difference['reference_text']}")
            print(f"    NEW: {difference['incoming_text']}")

    print(f"\nSUMMARY PAIR {pair.upper()}: {counts}")

    assert len(comparisons) == 7

print("\nPASS: Comparison pipeline ran on all 3 pairs.")
