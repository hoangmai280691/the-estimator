
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.document import extract_pdf_text, extract_sections
from core.matching import match_sections
from core.comparison import compare_sections
from core.detection import detect_all_findings
from core.findings import prepare_review_items, update_review_item


def main():
    # STEP 1: Run the existing detection pipeline on Pair A.
    folder = ROOT / "test_data" / "pair_a"

    reference = extract_sections(
        extract_pdf_text(folder / "Pair_A_Reference_Form.pdf")
    )

    incoming = extract_sections(
        extract_pdf_text(folder / "Pair_A_Incoming_Form.pdf")
    )

    matched = match_sections(reference, incoming)
    comparisons = compare_sections(matched)
    findings = detect_all_findings(comparisons)

    print(f"Detected findings: {len(findings)}")
    assert findings, "Expected at least one finding"

    # STEP 2: Prepare review items.
    review_items = prepare_review_items(findings)

    assert len(review_items) == len(findings)
    assert all(
        item["review_status"] == "pending"
        for item in review_items
    )

    assert all(
        item["suggested_categories"] == item["final_categories"]
        for item in review_items
    )

    print("PASS: review items initialized correctly")

    # STEP 3: Confirm the first finding.
    first_id = review_items[0]["id"]

    confirmed_items = update_review_item(
        review_items,
        item_id=first_id,
        review_status="confirmed",
        reviewer_notes="Confirmed after checking source evidence.",
    )

    assert confirmed_items[0]["review_status"] == "confirmed"
    assert confirmed_items[0]["reviewer_notes"] != ""

    # Original input must remain unchanged.
    assert review_items[0]["review_status"] == "pending"

    print("PASS: confirm and notes work")

    # STEP 4: Reject the second finding.
    assert len(confirmed_items) >= 2, (
        "Expected at least two findings for this test"
    )

    second_id = confirmed_items[1]["id"]

    rejected_items = update_review_item(
        confirmed_items,
        item_id=second_id,
        review_status="rejected",
        reviewer_notes="Not relevant to implementation scope.",
    )

    assert rejected_items[1]["review_status"] == "rejected"
    assert rejected_items[0]["review_status"] == "confirmed"

    print("PASS: reject works independently")

    # STEP 5: Change the final category.
    original_suggestion = rejected_items[0][
        "suggested_categories"
    ].copy()

    edited_items = update_review_item(
        rejected_items,
        item_id=first_id,
        final_categories=["conditional_logic"],
    )

    assert edited_items[0]["final_categories"] == [
        "conditional_logic"
    ]
    assert edited_items[0]["suggested_categories"] == (
        original_suggestion
    )

    print("PASS: category edits preserve original suggestion")

    # STEP 6: Invalid review status must fail.
    try:
        update_review_item(
            edited_items,
            item_id=first_id,
            review_status="approved_without_review",
        )
    except ValueError:
        print("PASS: invalid status rejected")
    else:
        raise AssertionError("Invalid status was accepted")

    # STEP 7: Unknown finding ID must fail.
    try:
        update_review_item(
            edited_items,
            item_id="F999999",
            review_status="confirmed",
        )
    except ValueError:
        print("PASS: unknown finding ID rejected")
    else:
        raise AssertionError("Unknown finding ID was accepted")

    # STEP 8: Evidence must remain unchanged.
    for original, reviewed in zip(findings, edited_items):
        assert reviewed["section"] == original["section"]
        assert reviewed["change_type"] == original["change_type"]
        assert (
            reviewed["reference_text"]
            == original["reference_text"]
        )
        assert (
            reviewed["incoming_text"]
            == original["incoming_text"]
        )

    print("PASS: original evidence preserved")

    # STEP 9: Display review summary.
    statuses = [
        item["review_status"]
        for item in edited_items
    ]

    print("\nREVIEW SUMMARY")
    print(f"Total: {len(edited_items)}")
    print(f"Confirmed: {statuses.count('confirmed')}")
    print(f"Rejected: {statuses.count('rejected')}")
    print(f"Pending: {statuses.count('pending')}")

    print("\nPASS: all Human Review checks completed.")


if __name__ == "__main__":
    main()