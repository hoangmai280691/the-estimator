from pathlib import Path
import json
import sys

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
TEST_DATA = ROOT / "test_data"

SECTION_NAMES = [
    "Investor Information",
    "Subscription Details",
    "Tax Information",
    "Supporting Documents",
    "Declarations",
    "Signature",
    "Wire Instructions",
]

COMMON_WIRE = (
    "Beneficiary: Fictional Fund Account. "
    "Bank: Example Bank (Fictional). "
    "Account: XXXX-XXXX-0001. Currency: USD. "
    "Payment reference: Investor full legal name."
)


PAIR_B_REFERENCE = [
    [
        "This form is available to individual investors and legal entities.",
        "Individuals provide legal name, date of birth, address and email.",
        "Entities provide registered name, incorporation country and registration number."
    ],
    [
        "The minimum subscription amount is USD 150,000."
    ],
    [
        "All investors provide country of tax residence.",
        "All investors must provide a Tax Identification Number (TIN).",
        "US persons must provide a completed IRS Form W-9."
    ],
    [
        "Individuals provide government-issued identification.",
        "Entities provide a certificate of incorporation."
    ],
    [
        "All investors confirm that the information is accurate."
    ],
    [
        "Individuals sign electronically.",
        "An authorized representative signs for legal entities."
    ],
    [COMMON_WIRE]
]

PAIR_B_INCOMING = [
    [
        "This form is available to individual investors and legal entities.",
        "Individuals provide legal name, date of birth, address and email.",
        "Entities provide registered name, incorporation country and registration number.",
        "Entity investors must identify their beneficial owners."
    ],
    [
        "The minimum subscription amount is USD 150,000.",
        "If the subscription exceeds USD 500,000, an additional approval is required."
    ],
    [
        "All investors provide country of tax residence.",
        "All investors must provide a Tax Identification Number (TIN).",
        "US Person Status: Yes or No. This declaration is required.",
        "If US Person Status is Yes, the investor must upload a completed IRS Form W-9.",
        "If US Person Status is No, the investor must upload a completed IRS Form W-8BEN or W-8BEN-E, as applicable."
    ],
    [
        "Individuals provide government-issued identification.",
        "Entities provide a certificate of incorporation.",
        "If the entity has more than one beneficial owner, identification must be provided for each beneficial owner."
    ],
    [
        "All investors confirm that the information is accurate.",
        "Entity investors must confirm that their authorized representative has signing authority."
    ],
    [
        "Individuals sign electronically.",
        "An authorized representative signs for legal entities.",
        "If an entity has multiple required signatories, each required signatory must sign."
    ],
    [COMMON_WIRE]
]

PAIR_B_FINDINGS = [
    ("B01", "investor_types", "Beneficial owner information added"),
    ("B02", "conditional_logic", "Additional approval above USD 500,000"),
    ("B03", "required_optional", "Required US Person Status Yes/No declaration added"),
    ("B04", "conditional_logic", "Explicit Yes branch for W-9 upload added"),
    ("B05", "conditional_logic", "Non-US branch for W-8BEN or W-8BEN-E added"),
    ("B06", "supporting_documents", "Identification for multiple beneficial owners added"),
    ("B07", "other", "Signing authority declaration added"),
    ("B08", "signatures", "Multiple required signatories supported"),
]


PAIR_C_REFERENCE = [
    [
        "Individual investors must provide legal name, date of birth and residential address.",
        "A phone number is required."
    ],
    [
        "Minimum subscription: USD 100,000.",
        "Subscription amount must be entered in USD."
    ],
    [
        "Country of tax residence is required.",
        "A Tax Identification Number (TIN) is required.",
        "If the investor is a US person, IRS Form W-9 is required."
    ],
    [
        "A government-issued identification document is required.",
        "Proof of address is required."
    ],
    [
        "The investor must acknowledge the privacy notice."
    ],
    [
        "The investor must provide an electronic signature."
    ],
    [COMMON_WIRE]
]

PAIR_C_INCOMING = [
    [
        "Individual investors must provide legal name, date of birth and residential address.",
        "A phone number is not required."
    ],
    [
        "Minimum subscription: USD 100,000.",
        "Subscription amount must be entered in USD."
    ],
    [
        "Country of tax residence is required.",
        "A Tax Identification Number (TIN) is not required.",
        "If the investor is NOT a US person, IRS Form W-9 is required."
    ],
    [
        "A government-issued identification document is required.",
        "Proof of address is optional."
    ],
    [
        "The investor must acknowledge the privacy notice.",
        "A separate marketing consent checkbox is optional."
    ],
    [
        "The investor must provide an electronic signature.",
        "The signature date must not be earlier than the submission date."
    ],
    [
        COMMON_WIRE,
        "The expected wire transfer date is required."
    ]
]

PAIR_C_FINDINGS = [
    ("C01", "required_optional", "Phone number no longer required"),
    ("C02", "required_optional", "TIN no longer required"),
    ("C03", "conditional_logic", "W-9 condition reversed"),
    ("C04", "required_optional", "Proof of address changed to optional"),
    ("C05", "other", "Optional marketing consent added"),
    ("C06", "validation_rules", "Signature date validation added"),
    ("C07", "other", "Expected wire transfer date added"),
]


def build_pdf(path, pair_name, version, sections):
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="CustomHeading",
            parent=styles["Heading2"],
            textColor=colors.HexColor("#183153"),
            spaceBefore=12,
            spaceAfter=6,
        )
    )

    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    story = [
        Paragraph(
            f"{escape(pair_name)} - Subscription Form ({version})",
            styles["Title"]
        ),
        Paragraph(
            "FICTIONAL TEST DATA - DO NOT USE FOR PAYMENT",
            styles["Normal"]
        ),
        Spacer(1, 12),
    ]

    for index, (name, paragraphs) in enumerate(
        zip(SECTION_NAMES, sections), start=1
    ):
        story.append(
            Paragraph(
                f"{index}. {escape(name)}",
                styles["CustomHeading"]
            )
        )
        for text in paragraphs:
            story.append(Paragraph(escape(text), styles["BodyText"]))
            story.append(Spacer(1, 5))

    doc.build(story)


def generate_pair(pair_id, reference, incoming, findings):
    folder = TEST_DATA / pair_id
    folder.mkdir(parents=True, exist_ok=True)

    build_pdf(
        folder / f"Pair_{pair_id[-1].upper()}_Reference_Form.pdf",
        pair_id.upper(),
        "Reference",
        reference,
    )
    build_pdf(
        folder / f"Pair_{pair_id[-1].upper()}_Incoming_Form.pdf",
        pair_id.upper(),
        "Incoming",
        incoming,
    )

    expected = {
        "pair_id": pair_id,
        "expected_findings": [
            {
                "id": finding_id,
                "category": category,
                "title": title
            }
            for finding_id, category, title in findings
        ],
    }

    (folder / "expected_findings.json").write_text(
        json.dumps(expected, indent=2),
        encoding="utf-8",
    )

    print(f"Created {pair_id}: 2 PDFs + expected_findings.json")


def main():
    generate_pair(
        "pair_b",
        PAIR_B_REFERENCE,
        PAIR_B_INCOMING,
        PAIR_B_FINDINGS,
    )
    generate_pair(
        "pair_c",
        PAIR_C_REFERENCE,
        PAIR_C_INCOMING,
        PAIR_C_FINDINGS,
    )


if __name__ == "__main__":
    main()
