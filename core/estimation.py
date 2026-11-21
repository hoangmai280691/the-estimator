
from copy import deepcopy
from math import isfinite


VALID_COMPLEXITIES = {"S", "M", "L"}


def prepare_estimation_items(finalized_scope_items):
    """
    Convert finalized scope items into estimation items.

    Each scope item receives its own estimation fields.
    No estimate is generated automatically.
    """
    estimation_items = []

    for scope in finalized_scope_items:
        if scope["scope_status"] != "finalized":
            raise ValueError(
                f"Scope item {scope['id']} is not finalized"
            )

        item = deepcopy(scope)

        item.update({
            "complexity": None,
            "estimated_hours": None,
            "estimation_rationale": "",
            "assumptions": "",
            "actual_hours": None,
        })

        estimation_items.append(item)

    return estimation_items


def update_estimation_item(
    estimation_items,
    item_id,
    complexity=None,
    estimated_hours=None,
    estimation_rationale=None,
    assumptions=None,
):
    """
    Update an estimation item without modifying
    the original list.

    Actual hours are deliberately excluded:
    they belong to the post-delivery workflow.
    """
    if complexity is not None:
        if complexity not in VALID_COMPLEXITIES:
            raise ValueError(
                "Complexity must be S, M, or L"
            )

    if estimated_hours is not None:
        if (
            isinstance(estimated_hours, bool)
            or not isinstance(estimated_hours, (int, float))
            or not isfinite(estimated_hours)
            or estimated_hours < 0
        ):
            raise ValueError(
                "Estimated hours must be a finite, "
                "non-negative number"
            )

    if estimation_rationale is not None:
        if not isinstance(estimation_rationale, str):
            raise ValueError(
                "Estimation rationale must be a string"
            )

    if assumptions is not None:
        if not isinstance(assumptions, str):
            raise ValueError(
                "Assumptions must be a string"
            )

    updated = deepcopy(estimation_items)

    for item in updated:
        if item["id"] != item_id:
            continue

        if complexity is not None:
            item["complexity"] = complexity

        if estimated_hours is not None:
            item["estimated_hours"] = float(estimated_hours)

        if estimation_rationale is not None:
            item["estimation_rationale"] = (
                estimation_rationale.strip()
            )

        if assumptions is not None:
            item["assumptions"] = assumptions.strip()

        return updated

    raise ValueError(f"Estimation item not found: {item_id}")


def finalize_estimation(estimation_items):
    """
    Validate all estimation items and calculate
    total estimated hours.

    Returns a new finalized result.
    """
    if not estimation_items:
        raise ValueError("No estimation items to finalize")

    finalized = deepcopy(estimation_items)

    seen_ids = set()
    total_hours = 0.0

    for item in finalized:
        item_id = item["id"]

        if item_id in seen_ids:
            raise ValueError(
                f"Duplicate estimation item ID: {item_id}"
            )

        seen_ids.add(item_id)

        if item["scope_status"] != "finalized":
            raise ValueError(
                f"Scope item {item_id} is not finalized"
            )

        if item["complexity"] not in VALID_COMPLEXITIES:
            raise ValueError(
                f"Missing or invalid complexity: {item_id}"
            )

        hours = item["estimated_hours"]

        if (
            isinstance(hours, bool)
            or not isinstance(hours, (int, float))
            or not isfinite(hours)
            or hours < 0
        ):
            raise ValueError(
                f"Missing or invalid estimated hours: {item_id}"
            )

        total_hours += hours
        item["estimation_status"] = "finalized"

    return {
        "items": finalized,
        "total_estimated_hours": round(total_hours, 2),
        "item_count": len(finalized),
    }
