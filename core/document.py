from pathlib import Path
import pymupdf


def extract_pdf_text(pdf_path: str | Path) -> str:
    """Extract selectable text from a PDF, preserving page order."""
    pdf_path = Path(pdf_path)

    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages = []

    with pymupdf.open(pdf_path) as document:
        for page in document:
            pages.append(page.get_text("text"))

    return "\n".join(pages)


def extract_sections(text: str) -> dict[str, str]:
    """Split Pair A text into its seven numbered sections."""
    sections = {}
    current_section = None
    current_lines = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if line[:2] in [f"{i}." for i in range(1, 8)]:
            if current_section is not None:
                sections[current_section] = "\n".join(current_lines)

            current_section = line
            current_lines = []
        elif current_section is not None:
            current_lines.append(line)

    if current_section is not None:
        sections[current_section] = "\n".join(current_lines)

    return sections
