from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    KeepTogether,
)


# Run this script from the estimator/ project directory.
OUTPUT_DIR = Path("test_data/pair_a")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FUND_NAME = "Northbridge Growth Fund I"
DISCLAIMER = "FICTIONAL TEST DATA - DO NOT USE FOR PAYMENT"


# --------------------------------------------------
# REFERENCE FORM - v1.0
# --------------------------------------------------

REFERENCE_SECTIONS = [
    (
        "1. Investor Information",
        [
            "This subscription form is intended for individual investors only.",
            (
                "The investor must provide full legal name, date of birth, "
                "residential address, email address, and phone number. "
                "All fields are required."
            ),
        ],
    ),
    (
        "2. Subscription Details",
        [
            (
                "The investor must enter the subscription amount in USD. "
                "The minimum subscription amount is USD 100,000."
            ),
        ],
    ),
    (
        "3. Tax Information",
        [
            (
                "The investor must provide country of tax residence and "
                "Tax Identification Number (TIN). Both fields are required."
            ),
        ],
    ),
    (
        "4. Supporting Documents",
        [
            (
                "The investor must submit a copy of a government-issued "
                "identification document."
            ),
        ],
    ),
    (
        "5. Declarations",
        [
            (
                "The investor must confirm that the information provided "
                "is accurate and complete."
            ),
        ],
    ),
    (
        "6. Signature",
        [
            (
                "The investor must sign the completed subscription form "
                "using a handwritten signature."
            ),
        ],
    ),
    (
        "7. Wire Instructions",
        [
            "Beneficiary Name: Northbridge Growth Fund I",
            "Bank Name: Example Bank (Fictional)",
            "Account Number: XXXX-XXXX-0001",
            "SWIFT/BIC: XXXXXXXX",
            "Currency: USD",
            "Payment Reference: Investor full legal name",
            (
                "The investor must transfer the subscription amount in USD "
                "to the fund's designated bank account using the wire "
                "instructions provided separately by the fund administrator."
            ),
            (
                "The investor must include their full legal name "
                "in the payment reference."
            ),
        ],
    ),
]


# --------------------------------------------------
# INCOMING FORM - v2.0
# --------------------------------------------------

INCOMING_SECTIONS = [
    (
        "1. Investor Information",
        [
            (
                "This subscription form is intended for individual "
                "investors and legal entities."
            ),
            (
                "Individual investors must provide full legal name, "
                "date of birth, residential address, email address, "
                "and phone number. All fields are required."
            ),
            (
                "Legal entity investors must provide registered entity "
                "name, country of incorporation, registration number, "
                "registered business address, and authorized "
                "representative details."
            ),
        ],
    ),
    (
        "2. Subscription Details",
        [
            (
                "The investor must enter the subscription amount in USD. "
                "The minimum subscription amount is USD 150,000."
            ),
        ],
    ),
    (
        "3. Tax Information",
        [
            (
                "The investor must provide country of tax residence. "
                "A Tax Identification Number (TIN) is optional."
            ),
            (
                "If the investor is a US person, the investor must "
                "also provide a completed IRS Form W-9."
            ),
        ],
    ),
    (
        "4. Supporting Documents",
        [
            (
                "Individual investors must submit a government-issued "
                "identification document and proof of residential address."
            ),
            (
                "Legal entity investors must submit a certificate "
                "of incorporation and identification for the "
                "authorized representative."
            ),
        ],
    ),
    (
        "5. Declarations",
        [
            (
                "The investor must confirm that the information provided "
                "is accurate and complete."
            ),
            (
                "The investor must also confirm that they have read "
                "and accepted the fund's privacy notice."
            ),
        ],
    ),
    (
        "6. Signature",
        [
            (
                "The investor may sign the completed subscription "
                "form electronically."
            ),
            (
                "For legal entity investors, the authorized "
                "representative must sign on behalf of the entity."
            ),
        ],
    ),
    (
        "7. Wire Instructions",
        [
            "Beneficiary Name: Northbridge Growth Fund I",
            "Bank Name: Example Bank (Fictional)",
            "Account Number: XXXX-XXXX-0001",
            "SWIFT/BIC: XXXXXXXX",
            "Currency: USD",
            (
                "Payment Reference: Investor full legal name "
                "and Subscription Reference Number"
            ),
            "Expected Wire Transfer Date: Required",
            (
                "The investor must transfer the subscription amount in USD "
                "to the fund's designated bank account using the wire "
                "instructions provided separately by the fund administrator."
            ),
            (
                "The investor must include their full legal name "
                "and subscription reference number in the payment reference."
            ),
            (
                "The investor must provide the expected wire "
                "transfer date in the subscription form."
            ),
        ],
    ),
]


# --------------------------------------------------
# PDF GENERATION
# --------------------------------------------------

def build_pdf(filename, version, sections):
    output_path = OUTPUT_DIR / filename

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title=f"{FUND_NAME} - Subscription Form {version}",
        author="Synthetic Test Data",
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="FormTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=21,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#183153"),
            spaceAfter=8,
        )
    )

    styles.add(
        ParagraphStyle(
            name="FormSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            alignment=TA_CENTER,
            spaceAfter=12,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionTitleCustom",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#183153"),
            spaceBefore=14,
            spaceAfter=7,
        )
    )

    styles.add(
        ParagraphStyle(
            name="BodyCustom",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=15,
            alignment=TA_LEFT,
            spaceAfter=7,
        )
    )

    styles.add(
        ParagraphStyle(
            name="DisclaimerCustom",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#A32626"),
            spaceAfter=15,
        )
    )

    story = [
        Paragraph(escape(FUND_NAME), styles["FormTitle"]),
        Paragraph(
            f"Subscription Form - {escape(version)}",
            styles["FormSubtitle"],
        ),
        Paragraph(DISCLAIMER, styles["DisclaimerCustom"]),
        Spacer(1, 6),
    ]

    for section_title, paragraphs in sections:
        block = [
            Paragraph(
                escape(section_title),
                styles["SectionTitleCustom"],
            )
        ]

        for paragraph in paragraphs:
            block.append(
                Paragraph(
                    escape(paragraph),
                    styles["BodyCustom"],
                )
            )

        story.append(KeepTogether(block))

    doc.build(story)
    print(f"Created: {output_path.resolve()}")


def main():
    build_pdf(
        "Pair_A_Reference_Form.pdf",
        "v1.0 - Reference",
        REFERENCE_SECTIONS,
    )

    build_pdf(
        "Pair_A_Incoming_Form.pdf",
        "v2.0 - Incoming",
        INCOMING_SECTIONS,
    )

    print("\nPair A PDF generation completed.")


if __name__ == "__main__":
    main()
