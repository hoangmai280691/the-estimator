from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from core.document import extract_pdf_text, extract_sections


PAIR_DIR = PROJECT_ROOT / "test_data" / "pair_a"

files = [
    PAIR_DIR / "Pair_A_Reference_Form.pdf",
    PAIR_DIR / "Pair_A_Incoming_Form.pdf",
]

for pdf_file in files:
    text = extract_pdf_text(pdf_file)
    sections = extract_sections(text)

    print(f"\nFILE: {pdf_file.name}")
    print(f"Extracted characters: {len(text)}")
    print(f"Sections found: {len(sections)}")

    for section_title in sections:
        print(f"  - {section_title}")

    assert len(sections) == 7, (
        f"Expected 7 sections, found {len(sections)}"
    )

print("\nPASS: Both PDFs contain 7 extractable sections.")
