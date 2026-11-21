from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.document import extract_pdf_text, extract_sections
from core.matching import match_sections


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

    matches = match_sections(reference, incoming)

    print(f"\nPAIR {pair.upper()}")
    for item in matches:
        print(f"  {item['status'].upper():8} {item['section_key']}")

    assert len(matches) == 7
    assert all(item["status"] == "matched" for item in matches)

print("\nPASS: All 3 pairs have 7 matched sections.")
