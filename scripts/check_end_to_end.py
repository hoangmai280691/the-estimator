
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.document import extract_pdf_text, extract_sections
from core.matching import match_sections
from core.comparison import compare_sections
from core.detection import detect_all_findings
from core.findings import prepare_review_items, update_review_item
from core.scoping import add_scope_from_findings, finalize_scope
from core.estimation import (
    prepare_estimation_items,
    update_estimation_item,
    finalize_estimation,
)


def main():
    print("\n=== THE ESTIMATOR: END-TO-END TEST ===")

    # STEP 1: Load real test PDFs.
    folder = ROOT / "test_data" / "pair_a"

    reference_path = folder / "Pair_A_Reference_Form.pdf"
    incoming_path = folder / "Pair_A_Incoming_Form.pdf"

    assert reference_path.exists(), reference_path
    assert incoming_path.exists(), incoming_path

    reference = extract_sections(
        extract_pdf_text(reference_path)
    )
    incoming = extract_sections(
        extract_pdf_text(incoming_path)
    )

    matched = match_sections(reference, incoming)
    comparisons = compare_sections(matched)
    findings = detect_all_findings(comparisons)

    assert len(findings) >= 2, (
        "This integration test requires at least two findings"
    )

    print(f"PASS: detected {len(findings)} findings from Pair A")

    # STEP 2: Prepare Human Review.
    review_items = prepare_review_items(findings)

    assert len(review_items) == len(findings)
    assert all(
        item["review_status"] == "pending"
        for item in review_items
    )

    print("PASS: findings transferred into Human Review")

    # STEP 3: Simulate review decisions.
    # Confirm F001 and F002, reject the remaining findings.
    # These are test decisions, NOT expert judgments.
    confirmed_ids = {"F001", "F002"}

    for item in review_items:
        status = (
            "confirmed"
            if item["id"] in confirmed_ids
            else "rejected"
        )

        review_items = update_review_item(
            review_items,
            item_id=item["id"],
            review_status=status,
            reviewer_notes="Simulated integration test decision.",
        )

    assert sum(
        item["review_status"] == "confirmed"
        for item in review_items
    ) == 2

    assert not any(
        item["review_status"] == "pending"
        for item in review_items
    )

    print("PASS: simulated review decisions completed")

    # STEP 4: Merge two confirmed findings into one scope item.
    scope_items = add_scope_from_findings(
        scope_items=[],
        review_items=review_items,
        finding_ids=["F001", "F002"],
        title="Integration test implementation scope",
        description=(
            "Synthetic scope grouping two detected findings "
            "to validate the workflow."
        ),
    )

    finalized_scope = finalize_scope(
        scope_items,
        review_items,
    )

    assert len(finalized_scope) == 1
    assert finalized_scope[0]["source_finding_ids"] == [
        "F001", "F002"
    ]

    assert finalized_scope[0]["scope_status"] == "finalized"

    print("PASS: confirmed findings merged and scope finalized")

    # STEP 5: Prepare Estimation.
    estimation_items = prepare_estimation_items(
        finalized_scope
    )

    assert len(estimation_items) == 1
    assert estimation_items[0]["estimated_hours"] is None
    assert estimation_items[0]["actual_hours"] is None

    print("PASS: finalized scope transferred into Estimation")

    # STEP 6: Simulate expert estimation.
    estimation_items = update_estimation_item(
        estimation_items,
        item_id="S001",
        complexity="M",
        estimated_hours=8,
        estimation_rationale=(
            "Synthetic estimate for integration testing only."
        ),
    )

    result = finalize_estimation(estimation_items)

    assert result["item_count"] == 1
    assert result["total_estimated_hours"] == 8.0

    print("PASS: estimation finalized and total calculated")

    # STEP 7: Verify traceability to original evidence.
    final_item = result["items"][0]

    linked_findings = [
        item for item in review_items
        if item["id"] in final_item["source_finding_ids"]
    ]

    assert len(linked_findings) == 2

    for finding in linked_findings:
        original = next(
            item for item in findings
            if (
                item["section"] == finding["section"]
                and item["reference_text"]
                == finding["reference_text"]
                and item["incoming_text"]
                == finding["incoming_text"]
            )
        )

        assert original["section"] == finding["section"]
        assert (
            original["reference_text"]
            == finding["reference_text"]
        )
        assert (
            original["incoming_text"]
            == finding["incoming_text"]
        )

    print("PASS: scope remains traceable to source evidence")

    # STEP 8: Summary.
    print("\n=== INTEGRATION TEST SUMMARY ===")
    print(f"Detected findings: {len(findings)}")
    print("Simulated confirmed findings: 2")
    print(f"Simulated rejected findings: {len(findings) - 2}")
    print(f"Finalized scope items: {len(finalized_scope)}")
    print(f"Estimation items: {result['item_count']}")
    print(
        f"Total estimated hours: "
        f"{result['total_estimated_hours']}h"
    )

    print("\nPASS: end-to-end integration test completed.")
    print(
        "NOTE: Review decisions, scope grouping, and "
        "estimated hours are simulated."
    )


if __name__ == "__main__":
    main()
