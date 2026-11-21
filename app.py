
import streamlit as st
from pathlib import Path
from tempfile import TemporaryDirectory

from core.document import extract_pdf_text, extract_sections
from core.matching import match_sections
from core.comparison import compare_sections
from core.detection import detect_all_findings
from core.findings import (
    prepare_review_items,
    update_review_item,
)
from core.persistence import (
    create_session,
    save_session,
    load_session,
    list_sessions,
)
from core.scoping import add_scope_from_findings
from core.ai_explanation import explain_finding

REVIEW_CATEGORIES = [
    "required_optional",
    "investor_types",
    "conditional_logic",
    "supporting_documents",
    "validation",
    "signatures",
    "others",
]

SESSIONS_DIR = Path(__file__).resolve().parent / "data" / "sessions"

st.set_page_config(
    page_title="The Estimator",
    page_icon="📋",
    layout="wide",
)

st.title("The Estimator")
st.caption(
    "Evidence-backed PDF change detection and implementation scoping"
)


def process_documents(reference_file, incoming_file):
    """
    Run the existing detection pipeline on uploaded PDFs.

    Temporary files are used because the current PDF
    extraction function expects a file path.
    """
    with TemporaryDirectory() as temp_dir:
        folder = Path(temp_dir)

        reference_path = folder / "reference.pdf"
        incoming_path = folder / "incoming.pdf"

        reference_path.write_bytes(reference_file.getvalue())
        incoming_path.write_bytes(incoming_file.getvalue())

        reference_sections = extract_sections(
            extract_pdf_text(reference_path)
        )

        incoming_sections = extract_sections(
            extract_pdf_text(incoming_path)
        )

        matched = match_sections(
            reference_sections,
            incoming_sections,
        )

        comparisons = compare_sections(matched)
        findings = detect_all_findings(comparisons)

    return findings


# Initialize Streamlit session state.
if "review_items" not in st.session_state:
    st.session_state.review_items = []

if "findings" not in st.session_state:
    st.session_state.findings = []

if "document_names" not in st.session_state:
    st.session_state.document_names = None

if "active_session" not in st.session_state:
    st.session_state.active_session = None

if "scope_items" not in st.session_state:
    st.session_state.scope_items = []

if "final_estimation" not in st.session_state:
    st.session_state.final_estimation = None

if "upload_version" not in st.session_state:
    st.session_state.upload_version = 0


st.subheader("Your Work")

save_col, resume_col = st.columns(2)

with save_col:
    can_save = (
        st.session_state.document_names is not None
        and st.session_state.active_session is not None
    )

    if st.button(
        "Save Draft",
        disabled=not can_save,
        use_container_width=True,
    ):
        session = st.session_state.active_session.copy()

        # Synchronize the latest UI state before saving.
        session["findings"] = st.session_state.findings
        session["review_items"] = st.session_state.review_items
        session["scope_items"] = st.session_state.scope_items
        session["final_estimation"] = st.session_state.final_estimation
        session["workflow_stage"] = (
            "completed"
            if st.session_state.final_estimation is not None
            else "review"
        )
        
        saved = save_session(session, SESSIONS_DIR)

        st.session_state.active_session = saved

        st.success("Draft saved successfully.")

with resume_col:
    saved_sessions = list_sessions(SESSIONS_DIR)

    if saved_sessions:
        session_options = {
                f"{item['reference_filename'].removesuffix('.pdf')[:16]} "
                f"· {item['updated_at'][:16]} "
                f"· {item['session_id'][:8]}": item["session_id"]
            for item in saved_sessions
    }

        selected_label = st.selectbox(
            "Saved sessions",
            options=list(session_options.keys()),
        )

        if st.button(
            "Resume Session",
            use_container_width=True,
        ):
            loaded = load_session(
                session_options[selected_label],
                SESSIONS_DIR,
            )

            st.session_state.active_session = loaded
            st.session_state.findings = loaded["findings"]
            st.session_state.review_items = loaded["review_items"]
            st.session_state.scope_items = loaded.get("scope_items", [])
            st.session_state.document_names = (
                loaded["reference_filename"],
                loaded["incoming_filename"],
            )
            st.session_state.final_estimation = loaded.get(
                "final_estimation"
         )
            # Clear AI explanations from the previous session
            for key in list(st.session_state.keys()):
                if key.startswith("ai_explanation_"):
                   del st.session_state[key]
            st.session_state.upload_version += 1
            st.rerun()
    else:
        st.info("No saved sessions yet.")

if st.session_state.active_session is not None:
    st.caption(
        "Active session: "
        + st.session_state.active_session["session_id"][:8]
    )

st.divider()

st.subheader("1. Upload & Compare")

left, right = st.columns(2)

with left:
    reference_file = st.file_uploader(
        "Reference PDF",
        type=["pdf"],
        key=f"reference_pdf_{st.session_state.upload_version}",
    )

with right:
    incoming_file = st.file_uploader(
        "Incoming PDF",
        type=["pdf"],
        key=f"incoming_pdf_{st.session_state.upload_version}",
    )


if st.button(
    "Compare Documents",
    type="primary",
    disabled=reference_file is None or incoming_file is None,
):
    with st.spinner("Extracting and comparing documents..."):
        try:
            findings = process_documents(
                reference_file,
                incoming_file,
            )

        except Exception as error:
            st.error(f"Comparison failed: {error}")

        
        else:
            review_items = prepare_review_items(findings)

            new_session = create_session(
            reference_filename=reference_file.name,
            incoming_filename=incoming_file.name,
            findings=findings,
            review_items=review_items,
           )

            st.session_state.findings = findings
            st.session_state.review_items = review_items
            st.session_state.document_names = (
                reference_file.name,
                incoming_file.name,
            )
            st.session_state.active_session = new_session
            st.session_state.scope_items = []
            # Clear AI explanations when starting a new comparison
            for key in list(st.session_state.keys()):
                if key.startswith("ai_explanation_"):
                   del st.session_state[key]

            st.success(
            "Document comparison completed. "
            "A new session has been created. "
            "Click Save Draft to save your work."
        )



# Display results from the current comparison.
if st.session_state.document_names is not None:
    reference_name, incoming_name = (
        st.session_state.document_names
    )

    st.divider()
    st.subheader("Detection Results")

    st.write(f"**Reference:** {reference_name}")
    st.write(f"**Incoming:** {incoming_name}")

    findings = st.session_state.findings
    review_items = st.session_state.review_items

    pending_count = sum(
    item["review_status"] == "pending"
    for item in review_items
    )

    confirmed_count = sum(
    item["review_status"] == "confirmed"
    for item in review_items
    )

    rejected_count = sum(
    item["review_status"] == "rejected"
    for item in review_items
)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Detected Findings", len(findings))
    col2.metric("Pending", pending_count)
    col3.metric("Confirmed", confirmed_count)
    col4.metric("Rejected", rejected_count)

review_items = st.session_state.review_items
    
if not review_items:
    st.info("No changes were detected.")

else:
    st.markdown("### 2. Human Review")

    st.caption(
        "Review each detected change. "
        "Suggested categories are preserved separately "
        "from reviewer decisions."
    )

    if pending_count == 0:
        st.success("All findings have been reviewed.")
    else:
        st.info(
            f"{pending_count} findings still need review."
        )

    for item in review_items:
        item_id = item["id"]

        with st.expander(
            f"{item_id} — {item['section']} "
            f"({item['change_type']}) "
            f"· {item['review_status'].upper()}"
        ):
            st.write(
                "**Suggested categories:** "
                + ", ".join(item["suggested_categories"])
            )

            evidence_left, evidence_right = st.columns(2)

            with evidence_left:
                st.markdown("**Reference evidence**")
                st.text(item["reference_text"])

            with evidence_right:
                st.markdown("**Incoming evidence**")
                st.text(item["incoming_text"])

            st.divider()

            # Explain with AI (on demand)
            if st.button(
                "✨ Explain with AI",
                key=f"explain_ai_{item_id}",
            ):
                finding_for_ai = {
                    "id": item_id,
                    "section": item["section"],
                    "change_type": item["change_type"],
                    "reference_evidence": item["reference_text"],
                    "incoming_evidence": item["incoming_text"],
                }

                try:
                    with st.spinner("Generating AI explanation..."):
                        explanation = explain_finding(finding_for_ai)

                    st.session_state[f"ai_explanation_{item_id}"] = (
                        explanation
                    )

                except Exception:
                    st.error(
                        "AI explanation is temporarily unavailable. "
                        "Please try again."
                    )

            # Display saved explanation after Streamlit reruns
            saved_explanation = st.session_state.get(
                f"ai_explanation_{item_id}"
            )

            if saved_explanation:
                st.markdown(saved_explanation)

            st.divider()

            status_options = [
                "pending",
                "confirmed",
                "rejected",
            ]

            with st.form(key=f"review_form_{item_id}"):

                selected_status = st.selectbox(
                    "Review status",
                    options=status_options,
                    index=status_options.index(
                        item["review_status"]
                    ),
                )

                selected_categories = st.multiselect(
                    "Final categories",
                    options=REVIEW_CATEGORIES,
                    default=item["final_categories"],
                    help=(
                        "Edit categories if detection "
                        "classification is incorrect."
                    ),
                )

                notes = st.text_area(
                    "Reviewer notes (optional)",
                    value=item["reviewer_notes"],
                    placeholder=(
                        "Explain corrections, decisions, "
                        "or relevant assumptions..."
                    ),
                )

                submitted = st.form_submit_button(
                    "Save Review",
                    type="primary",
                )

                if submitted:
                    try:
                        updated_items = update_review_item(
                            review_items=st.session_state.review_items,
                            item_id=item_id,
                            review_status=selected_status,
                            final_categories=selected_categories,
                            reviewer_notes=notes,
                        )

                    except ValueError as error:
                        st.error(str(error))

                    else:
                        st.session_state.review_items = (
                            updated_items
                        )

                        st.success(
                            f"Saved {item_id}: "
                            f"{selected_status} | "
                            f"Notes: {notes!r}"
                        )
                        st.rerun()


@st.dialog("Delete Scope Item?")
def confirm_delete_scope(scope_id, scope_title):
    st.warning(
        f"Are you sure you want to delete "
        f"{scope_id} — {scope_title}?"
    )

    st.write(
        "This will also remove its estimation "
        "and invalidate the final estimate."
    )

    cancel_col, delete_col = st.columns(2)

    with cancel_col:
        if st.button(
            "Cancel",
            use_container_width=True,
        ):
            st.rerun()

    with delete_col:
        if st.button(
            "Confirm Delete",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.scope_items = [
                item
                for item in st.session_state.scope_items
                if item["id"] != scope_id
            ]

            # Invalidate final estimation only after deletion.
            st.session_state.final_estimation = None

            st.rerun()


# STEP 3 — IMPLEMENTATION SCOPING

st.divider()
st.subheader("3. Implementation Scoping")

confirmed_findings = [
    item
    for item in st.session_state.review_items
    if item["review_status"] == "confirmed"
]

if not confirmed_findings:
    st.info(
        "No confirmed findings yet. "
        "Confirm findings in Human Review before scoping."
    )
else:
    st.caption(
        f"{len(confirmed_findings)} confirmed findings "
        "available for implementation scoping."
    )

    for item in confirmed_findings:
        st.write(
            f"**{item['id']}** — "
            f"{item['section'].title()} "
            f"({', '.join(item['final_categories'])})"
        )


# CREATE SCOPE ITEM

if confirmed_findings:
    finding_options = {
        f"{item['id']} — {item['section'].title()}": item["id"]
        for item in confirmed_findings
    }

    with st.form("create_scope_form",clear_on_submit=True):
        selected_labels = st.multiselect(
            "Confirmed findings to include",
            options=list(finding_options.keys()),
        )

        scope_title = st.text_input(
            "Scope item title",
            placeholder="e.g. Update subscription validation",
        )

        scope_description = st.text_area(
            "Implementation description",
            placeholder=(
                "Describe what needs to change in the "
                "implementation, not just the PDF wording."
            ),
        )

        create_scope = st.form_submit_button(
            "Create Scope Item",
            type="primary",
        )

        if create_scope:
            selected_ids = [
                finding_options[label]
                for label in selected_labels
            ]

            if not selected_ids:
                st.error(
                    "Select at least one confirmed finding."
                )

            elif not scope_title.strip():
                st.error("Enter a scope item title.")

            elif not scope_description.strip():
                st.error("Enter an implementation description.")

            else:
                try:
                    st.session_state.scope_items = (
                        add_scope_from_findings(
                            scope_items=st.session_state.scope_items,
                            review_items=st.session_state.review_items,
                            finding_ids=selected_ids,
                            title=scope_title.strip(),
                            description=scope_description.strip(),
                        )
                    )

                except ValueError as error:
                    st.error(str(error))

                else:
                    # New scope changes the estimation baseline.
                    st.session_state.final_estimation = None

                    st.success(
                        "Scope item created successfully."
                    )
                    st.rerun()


# DISPLAY CREATED SCOPE ITEMS

st.subheader("Created Scope Items")

if not st.session_state.scope_items:
    st.info("No scope items created yet.")

else:
    for scope_item in st.session_state.scope_items:
        scope_id = scope_item["id"]

        with st.container(border=True):
            st.write(
                f"**{scope_id} — {scope_item['title']}**"
            )

            st.write(scope_item["description"])

            st.caption(
                "Source findings: "
                + ", ".join(scope_item["source_finding_ids"])
            )

            if st.button(
                "Delete Scope Item",
                key=f"delete_scope_{scope_id}",
            ):
                confirm_delete_scope(
                    scope_id,
                    scope_item["title"],
                )

# STEP 4 — EFFORT ESTIMATION

st.divider()
st.subheader("4. Effort Estimation")

if not st.session_state.scope_items:
    st.info("Create scope items before estimating effort.")

else:
    st.caption(
        "Estimate each scope item in hours. "
        "1 person-day = 8 hours."
    )

    for index, scope_item in enumerate(st.session_state.scope_items):
        current_status = scope_item.get("estimate_status", "Draft")
        is_confirmed = current_status == "Confirmed"
        with st.expander(
            f"Estimate — {scope_item['title']}"
        ):
            with st.form(f"estimate_form_{index}"):

                hours = st.number_input(
                        "Estimated hours",
                    min_value=0.0,
                    step=0.5,
                    value=float(scope_item.get("estimated_hours", 0)),
                    disabled=is_confirmed,
            )

                complexity_options = [
                    "Low", "Medium", "High"
                ]

                current_complexity = scope_item.get(
                    "complexity", "Medium"
                )

                complexity = st.selectbox(
                    "Complexity",
                    options=complexity_options,
                    index=complexity_options.index(
                        current_complexity),
                    disabled=is_confirmed,
                    
                )

                assumptions = st.text_area(
                    "Estimation assumptions",
                    value=scope_item.get("assumptions", ""),
                )

                status_options = ["Draft", "Confirmed"]

                current_status = scope_item.get(
                    "estimate_status", "Draft"
                )

                estimate_status = st.selectbox(
                    "Estimate status",
                    options=status_options,
                    index=status_options.index(current_status),
                )

                submitted = st.form_submit_button(
                    "Save Estimate",
                    type="primary",
                )
                
                if submitted:
                    if is_confirmed:
                       # Only allow status change.
                       st.session_state.scope_items[index]["estimate_status"] = (
                                         estimate_status
                        )
                    else:
                        st.session_state.scope_items[index].update({
                        "estimated_hours": hours,
                        "complexity": complexity,
                        "assumptions": assumptions,
                        "estimate_status": estimate_status,
                    })

                    st.success("Estimate updated.")
                    st.rerun()

    st.divider()
    st.subheader("Total Project Estimate")

    estimated_items = [
        item for item in st.session_state.scope_items
        if "estimated_hours" in item
    ]

    total_hours = sum(
        float(item["estimated_hours"])
        for item in estimated_items
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Hours", f"{total_hours:g} h")
    col2.metric("Person-days", f"{total_hours / 8:.2f}")
    col3.metric(
        "Estimated Items",
        f"{len(estimated_items)}/{len(st.session_state.scope_items)}"
    )


# STEP 5 — FINAL ESTIMATION

st.divider()
st.subheader("5. Final Estimation")

scope_items = st.session_state.scope_items

if not scope_items:
    st.info("Create and estimate scope items before finalizing.")

else:
    estimated = [
        item for item in scope_items
        if "estimated_hours" in item
    ]

    confirmed = [
        item for item in estimated
        if item.get("estimate_status") == "Confirmed"
    ]

    all_estimated = len(estimated) == len(scope_items)
    all_confirmed = len(confirmed) == len(scope_items)

    total_hours = sum(
        float(item["estimated_hours"]) for item in estimated
    )

    st.metric("Total Estimated Hours", f"{total_hours:g} h")
    st.metric("Total Person-days", f"{total_hours / 8:.2f}")

    st.write(
        f"**Confirmed estimates:** "
        f"{len(confirmed)}/{len(scope_items)}"
    )

    if not all_estimated:
        st.warning("Some scope items have not been estimated.")

    elif not all_confirmed:
        st.warning(
            "All estimates must be confirmed before finalization."
        )

    else:
        st.success("All scope estimates are confirmed.")

    # Prevent outdated finalization after estimate changes.
    current_snapshot = [
        {
            "scope_id": item["id"],
            "estimated_hours": float(item["estimated_hours"]),
            "complexity": item.get("complexity"),
            "assumptions": item.get("assumptions", ""),
            "estimate_status": item.get("estimate_status"),
        }
        for item in scope_items
    ]

    final = st.session_state.final_estimation

    if final is not None:
        if final.get("items") != current_snapshot:
            st.session_state.final_estimation = None
            final = None
            st.warning(
                "Estimates changed. Please finalize again."
            )

    if st.button(
        "Finalize Estimate",
        type="primary",
        disabled=not (all_estimated and all_confirmed),
    ):
        st.session_state.final_estimation = {
            "total_hours": total_hours,
            "total_person_days": total_hours / 8,
            "scope_count": len(scope_items),
            "items": current_snapshot,
        }

        st.success(
            "Estimate finalized. Click Save Draft to persist it."
        )

    if st.session_state.final_estimation is not None:
        st.success("Final estimation is ready.")
        #st.json(st.session_state.final_estimation)
