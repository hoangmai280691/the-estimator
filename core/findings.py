
from copy import deepcopy

VALID_REVIEW_STATUSES = {"pending", "confirmed", "rejected"}


def prepare_review_items(findings):
    """
    Convert detected findings into reviewable items.

    Keeps original evidence and detector suggestions.
    Every finding starts as pending.
    """
    review_items = []

    for index, finding in enumerate(findings, start=1):
        suggested_categories = list(finding["categories"])

        review_item = {
            "id": f"F{index:03d}",
            "section": finding["section"],
            "change_type": finding["change_type"],
            "reference_text": finding["reference_text"],
            "incoming_text": finding["incoming_text"],

            # Preserve the detector's original suggestion.
            "suggested_categories": suggested_categories,

            # Reviewer can change these without overwriting suggestions.
            "final_categories": suggested_categories.copy(),

            "review_status": "pending",
            "reviewer_notes": "",
        }

        review_items.append(review_item)

    return review_items


def update_review_item(
    review_items,
    item_id,
    review_status=None,
    final_categories=None,
    reviewer_notes=None,
):
    """
    Update one review item by ID.

    Returns a new list without modifying the original.
    """
    updated_items = deepcopy(review_items)

    if review_status is not None:
        if review_status not in VALID_REVIEW_STATUSES:
            raise ValueError(
                f"Invalid review status: {review_status}"
            )

    if final_categories is not None:
        if (
            not isinstance(final_categories, list)
            or not final_categories
            or not all(
                isinstance(category, str) and category.strip()
                for category in final_categories
            )
        ):
            raise ValueError(
                "final_categories must be a non-empty list of strings"
            )

    if reviewer_notes is not None:
        if not isinstance(reviewer_notes, str):
            raise ValueError(
                "reviewer_notes must be a string"
            )

    for item in updated_items:
        if item["id"] != item_id:
            continue

        if review_status is not None:
            item["review_status"] = review_status

        if final_categories is not None:
            item["final_categories"] = final_categories.copy()

        if reviewer_notes is not None:
            item["reviewer_notes"] = reviewer_notes

        return updated_items

    raise ValueError(f"Review item not found: {item_id}")
