
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.estimation import (
    prepare_estimation_items,
    update_estimation_item,
    finalize_estimation,
)


def expect_value_error(action, expected_message):
    try:
        action()
    except ValueError as error:
        assert expected_message in str(error), str(error)
    else:
        raise AssertionError(
            f"Expected ValueError containing: {expected_message}"
        )


def main():
    # Simulated output from finalize_scope().
    # No real reviewer decisions are involved.
    finalized_scope = [
        {
            "id": "S001",
            "title": "Implement multi-signatory workflow",
            "description": "Support multiple required signers.",
            "source_finding_ids": ["F001", "F002"],
            "rationale": "",
            "scope_status": "finalized",
        },
        {
            "id": "S002",
            "title": "Add tax ID validation",
            "description": "Validate tax ID before submission.",
            "source_finding_ids": ["F003"],
            "rationale": "",
            "scope_status": "finalized",
        },
        {
            "id": "S003",
            "title": "Update internal guidance",
            "description": "Document the new process.",
            "source_finding_ids": [],
            "rationale": "Manual operational task.",
            "scope_status": "finalized",
        },
    ]

    # STEP 1: Prepare estimation items.
    items = prepare_estimation_items(finalized_scope)

    assert len(items) == 3
    assert all(item["complexity"] is None for item in items)
    assert all(item["estimated_hours"] is None for item in items)
    assert all(item["actual_hours"] is None for item in items)

    print("PASS: estimation items initialized without suggestions")

    # STEP 2: Cannot finalize incomplete estimates.
    expect_value_error(
        lambda: finalize_estimation(items),
        "Missing or invalid complexity",
    )

    print("PASS: incomplete estimation cannot be finalized")

    # STEP 3: Reviewer estimates S001.
    items = update_estimation_item(
        items,
        item_id="S001",
        complexity="L",
        estimated_hours=16,
        estimation_rationale="Multiple signer workflow changes.",
    )

    assert items[0]["complexity"] == "L"
    assert items[0]["estimated_hours"] == 16.0
    assert items[0]["actual_hours"] is None

    print("PASS: complexity and estimated hours updated")

    # STEP 4: Optional fields can remain empty.
    items = update_estimation_item(
        items,
        item_id="S002",
        complexity="M",
        estimated_hours=3,
    )

    assert items[1]["estimation_rationale"] == ""
    assert items[1]["assumptions"] == ""

    print("PASS: rationale and assumptions are optional")

    # STEP 5: Manual scope item can be estimated.
    items = update_estimation_item(
        items,
        item_id="S003",
        complexity="S",
        estimated_hours=2,
        assumptions="Existing documentation can be reused.",
    )

    print("PASS: manual scope item can be estimated")

    # STEP 6: Invalid inputs are rejected.
    expect_value_error(
        lambda: update_estimation_item(
            items, "S001", complexity="XL"
        ),
        "Complexity must be",
    )

    expect_value_error(
        lambda: update_estimation_item(
            items, "S001", estimated_hours=-2
        ),
        "Estimated hours must be",
    )

    expect_value_error(
        lambda: update_estimation_item(
            items, "S001", estimated_hours=float("nan")
        ),
        "Estimated hours must be",
    )

    expect_value_error(
        lambda: update_estimation_item(
            items, "S001", estimated_hours=True
        ),
        "Estimated hours must be",
    )

    expect_value_error(
        lambda: update_estimation_item(
            items, "S999", complexity="S"
        ),
        "Estimation item not found",
    )

    print("PASS: invalid estimation inputs rejected")

    # STEP 7: Finalize and calculate total.
    result = finalize_estimation(items)

    assert result["item_count"] == 3
    assert result["total_estimated_hours"] == 21.0
    assert all(
        item["estimation_status"] == "finalized"
        for item in result["items"]
    )

    print("PASS: total estimated hours calculated correctly")

    # STEP 8: Original scope and draft remain unchanged.
    assert "estimated_hours" not in finalized_scope[0]
    assert "estimation_status" not in items[0]

    print("PASS: original data remains unchanged")

    # STEP 9: Unfinalized scope cannot enter estimation.
    invalid_scope = [
        {
            **finalized_scope[0],
            "scope_status": "draft",
        }
    ]

    expect_value_error(
        lambda: prepare_estimation_items(invalid_scope),
        "not finalized",
    )

    print("PASS: unfinalized scope rejected")

    # STEP 10: Duplicate scope IDs cannot be finalized.
    duplicate_items = result["items"] + [result["items"][0]]

    expect_value_error(
        lambda: finalize_estimation(duplicate_items),
        "Duplicate estimation item ID",
    )

    print("PASS: duplicate estimation IDs rejected")

    # Final summary.
    print("\nSIMULATED ESTIMATION SUMMARY")

    for item in result["items"]:
        print(
            f"{item['id']}: {item['title']} | "
            f"{item['complexity']} | "
            f"{item['estimated_hours']}h"
        )

    print(
        f"\nTOTAL ESTIMATED HOURS: "
        f"{result['total_estimated_hours']}h"
    )

    print("\nPASS: all Estimation checks completed.")
    print("NOTE: Estimates are simulated, not expert benchmarks.")


if __name__ == "__main__":
    main()