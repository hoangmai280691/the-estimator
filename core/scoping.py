
from copy import deepcopy


def create_scope_item(
    scope_items,
    title,
    description,
    source_finding_ids=None,
    rationale="",
):
    """
    Create a scope item from confirmed findings
    or manually with a documented rationale.

    Returns a new list without modifying the input.
    """
    source_finding_ids = (
        list(source_finding_ids)
        if source_finding_ids is not None
        else []
    )

    if not isinstance(title, str) or not title.strip():
        raise ValueError("Scope item title is required")

    if not isinstance(description, str):
        raise ValueError("Description must be a string")

    if not source_finding_ids and not rationale.strip():
        raise ValueError(
            "Manual scope items require a rationale"
        )

    existing_ids = {
        item["id"] for item in scope_items
    }

    index = 1
    while f"S{index:03d}" in existing_ids:
        index += 1

    new_item = {
        "id": f"S{index:03d}",
        "title": title.strip(),
        "description": description.strip(),
        "source_finding_ids": source_finding_ids,
        "rationale": rationale.strip(),
        "scope_status": "draft",
    }

    updated = deepcopy(scope_items)
    updated.append(new_item)
    return updated


def add_scope_from_findings(
    scope_items,
    review_items,
    finding_ids,
    title,
    description,
):
    """
    Create one scope item from one or more
    confirmed findings.
    """
    if not finding_ids:
        raise ValueError("At least one finding is required")

    if len(set(finding_ids)) != len(finding_ids):
        raise ValueError("Duplicate finding IDs are not allowed")

    findings_by_id = {
        item["id"]: item for item in review_items
    }

    for finding_id in finding_ids:
        finding = findings_by_id.get(finding_id)

        if finding is None:
            raise ValueError(
                f"Finding not found: {finding_id}"
            )

        if finding["review_status"] != "confirmed":
            raise ValueError(
                f"Finding {finding_id} is not confirmed"
            )

    already_linked = {
        finding_id
        for scope in scope_items
        for finding_id in scope["source_finding_ids"]
    }

    overlapping = already_linked.intersection(finding_ids)

    if overlapping:
        raise ValueError(
            f"Findings already linked: {sorted(overlapping)}"
        )

    return create_scope_item(
        scope_items=scope_items,
        title=title,
        description=description,
        source_finding_ids=finding_ids,
    )


def finalize_scope(scope_items, review_items):
    """
    Validate scope completeness and return
    finalized scope items.

    Does not modify the original input.
    """
    pending = [
        item["id"]
        for item in review_items
        if item["review_status"] == "pending"
    ]

    if pending:
        raise ValueError(
            f"Cannot finalize: {len(pending)} findings "
            "still pending review"
        )

    confirmed_ids = {
        item["id"]
        for item in review_items
        if item["review_status"] == "confirmed"
    }

    linked_ids = [
        finding_id
        for scope in scope_items
        for finding_id in scope["source_finding_ids"]
    ]

    if len(linked_ids) != len(set(linked_ids)):
        raise ValueError(
            "A finding is linked to multiple scope items"
        )

    if not set(linked_ids).issubset(confirmed_ids):
        raise ValueError(
            "Scope contains unconfirmed findings"
        )

    missing = confirmed_ids - set(linked_ids)

    if missing:
        raise ValueError(
            f"Confirmed findings not scoped: {sorted(missing)}"
        )

    finalized = deepcopy(scope_items)

    for item in finalized:
        if not item["title"].strip():
            raise ValueError("Scope item title is required")

        if (
            not item["source_finding_ids"]
            and not item["rationale"].strip()
        ):
            raise ValueError(
                "Manual scope item is missing rationale"
            )

        item["scope_status"] = "finalized"

    return finalized
