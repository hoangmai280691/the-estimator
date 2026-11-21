from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.document import extract_pdf_text, extract_sections
from core.matching import match_sections
from core.comparison import compare_sections
from core.detection import detect_supporting_document_changes


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
    findings = detect_supporting_document_changes(comparisons)

    print(f"\nPAIR {pair.upper()}: {len(findings)} findings")

    for finding in findings:
        print(f"  SECTION: {finding['section']}")
        print(f"  CHANGE TYPE: {finding['change_type']}")
        print(f"  REF: {finding['reference_text']}")
        print(f"  NEW: {finding['incoming_text']}")
        print()

print("\nPASS: Supporting documents detection script completed.")