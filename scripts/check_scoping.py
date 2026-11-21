
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.findings import prepare_review_items, update_review_item
from core.scoping import (
    create_scope_item,
    add_scope_from_findings,
    finalize_scope,
)


def expect_value_error(action, expected_message):
    """Check that an invalid action raises ValueError."""
    try:
        action()
    except ValueError as error:
        assert expected_message in str(error), str(error)
    else:
        raise AssertionError(
            f"Expected ValueError containing: {expected_message}"
        )


def main():
    # STEP 1: Create synthetic findings for an isolated test.
    # These are NOT actual findings from Pair A/B/C.
    findings = [
        {
            "section": "Signatures",
            "change_type": "modified",
            "categories": ["signatures"],
            "reference_text": "One signer is required.",
            "incoming_text": "Two signers are required.",
        },
        {
            "section": "Signatures",
            "change_type": "modified",
            "categories": ["signatures"],
            "reference_text": "One signature is sufficient.",
            "incoming_text": "All required signers must sign.",
        },
        {
            "section": "Validation",
            "change_type": "modified",
            "categories": ["validation"],
            "reference_text": "Submission is allowed.",
            "incoming_text": "Submission requires a valid tax ID.",
        },
        {
            "section": "Supporting Documents",
            "change_type": "added",
            "categories": ["supporting_documents"],
            "reference_text": "",
            "incoming_text": "Upload a supporting document.",
        },
    ]

    review_items = prepare_review_items(findings)

    assert len(review_items) == 4
    assert all(
        item["review_status"] == "pending"
        for item in review_items
    )
    print("PASS: four pending review items initialized")

    # STEP 2: Simulate confirming F001, F002, F003.
    for finding_id in ("F001", "F002", "F003"):
        review_items = update_review_item(
            review_items,
            item_id=finding_id,
            review_status="confirmed",
        )

    # F004 remains pending initially.
    scope_items = []

    # STEP 3: Merge two confirmed findings into one scope item.
    scope_items = add_scope_from_findings(
        scope_items=scope_items,
        review_items=review_items,
        finding_ids=["F001", "F002"],
        title="Implement multi-signatory workflow",
        description=(
            "Support multiple required signers and "
            "validate their signatures."
        ),
    )

    assert len(scope_items) == 1
    assert scope_items[0]["id"] == "S001"
    assert scope_items[0]["source_finding_ids"] == [
        "F001", "F002"
    ]
    assert scope_items[0]["scope_status"] == "draft"

    print("PASS: two confirmed findings merged into S001")

    # STEP 4: Prevent linking the same finding twice.
    expect_value_error(
        lambda: add_scope_from_findings(
            scope_items,
            review_items,
            ["F002", "F003"],
            "Duplicate scope",
            "Should not be created",
        ),
        "already linked",
    )

    print("PASS: duplicate finding linkage prevented")

    # STEP 5: Prevent scoping pending findings.
    expect_value_error(
        lambda: add_scope_from_findings(
            scope_items,
            review_items,
            ["F004"],
            "Pending scope",
            "Should not be created",
        ),
        "not confirmed",
    )

    print("PASS: pending finding cannot be scoped")

    # STEP 6: Create a scope item for F003.
    scope_items = add_scope_from_findings(
        scope_items,
        review_items,
        ["F003"],
        "Add tax ID validation",
        "Validate tax ID before submission.",
    )

    assert scope_items[1]["id"] == "S002"
    print("PASS: standalone confirmed finding scoped")

    # STEP 7: Add a manual scope item with rationale.
    scope_items = create_scope_item(
        scope_items=scope_items,
        title="Update internal guidance",
        description="Document the new validation process.",
        rationale=(
            "Reviewer identified an operational task "
            "not explicitly captured by detection."
        ),
    )

    assert scope_items[2]["id"] == "S003"
    assert scope_items[2]["source_finding_ids"] == []

    print("PASS: manual scope item created with rationale")

    # STEP 8: Reject manual item without rationale.
    expect_value_error(
        lambda: create_scope_item(
            scope_items,
            title="Unexplained manual task",
            description="No rationale provided.",
        ),
        "require a rationale",
    )

    print("PASS: manual item without rationale rejected")

    # STEP 9: Cannot finalize while F004 is pending.
    expect_value_error(
        lambda: finalize_scope(scope_items, review_items),
        "still pending review",
    )

    print("PASS: finalize blocked while review is pending")

    # STEP 10: Reject F004, then finalize.
    review_items = update_review_item(
        review_items,
        item_id="F004",
        review_status="rejected",
        reviewer_notes="Not included in this simulated scope.",
    )

    finalized = finalize_scope(scope_items, review_items)

    assert len(finalized) == 3
    assert all(
        item["scope_status"] == "finalized"
        for item in finalized
    )

    # Original draft scope remains unchanged.
    assert all(
        item["scope_status"] == "draft"
        for item in scope_items
    )

    print("PASS: finalized scope contains three items")
    print("PASS: original draft scope remains unchanged")

    # STEP 11: Print the finalized scope.
    print("\nSIMULATED FINALIZED SCOPE")

    for item in finalized:
        print(f"\n{item['id']}: {item['title']}")
        print(f"  Sources: {item['source_finding_ids']}")
        print(f"  Status: {item['scope_status']}")

    print("\nPASS: all Scoping checks completed.")
    print("NOTE: No real review decisions were saved.")


if __name__ == "__main__":
    main()
