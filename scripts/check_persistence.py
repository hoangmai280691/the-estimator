
from pathlib import Path
from tempfile import TemporaryDirectory
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.findings import prepare_review_items, update_review_item
from core.persistence import (
    create_session,
    save_session,
    load_session,
    list_sessions,
)


def main():
    print("\n=== PERSISTENCE TEST ===")

    findings = [
        {
            "section": "Signatures",
            "change_type": "modified",
            "categories": ["signatures"],
            "reference_text": "One signer required.",
            "incoming_text": "Two signers required.",
        },
        {
            "section": "Validation",
            "change_type": "modified",
            "categories": ["validation"],
            "reference_text": "Tax ID optional.",
            "incoming_text": "Tax ID required.",
        },
    ]

    review_items = prepare_review_items(findings)

    # STEP 1: Create a session.
    session = create_session(
        reference_filename="Reference.pdf",
        incoming_filename="Incoming.pdf",
        findings=findings,
        review_items=review_items,
    )

    assert session["workflow_stage"] == "review"
    assert len(session["review_items"]) == 2

    print("PASS: session created")

    # Use a temporary directory so tests do not
    # create permanent files in the project.
    with TemporaryDirectory() as temp_dir:

        # STEP 2: Save an unfinished draft.
        saved = save_session(session, temp_dir)

        path = Path(temp_dir) / f"{saved['session_id']}.json"

        assert path.exists()

        print("PASS: unfinished draft saved")

        # STEP 3: Load the session.
        loaded = load_session(
            saved["session_id"],
            temp_dir,
        )

        assert loaded["session_id"] == saved["session_id"]
        assert len(loaded["findings"]) == 2
        assert all(
            item["review_status"] == "pending"
            for item in loaded["review_items"]
        )

        print("PASS: session loaded with pending findings")

        # STEP 4: Simulate reviewer resuming work.
        loaded["review_items"] = update_review_item(
            loaded["review_items"],
            item_id="F001",
            review_status="confirmed",
            reviewer_notes="Reviewed after reopening session.",
        )

        updated = save_session(loaded, temp_dir)

        print("PASS: resumed review saved again")

        # STEP 5: Reload and verify persistence.
        reloaded = load_session(
            updated["session_id"],
            temp_dir,
        )

        assert reloaded["review_items"][0]["review_status"] == (
            "confirmed"
        )
        assert reloaded["review_items"][0]["reviewer_notes"] == (
            "Reviewed after reopening session."
        )
        assert reloaded["review_items"][1]["review_status"] == (
            "pending"
        )

        print("PASS: review decision persisted")

        # STEP 6: Check session listing.
        sessions = list_sessions(temp_dir)

        assert len(sessions) == 1
        assert sessions[0]["session_id"] == (
            updated["session_id"]
        )

        print("PASS: saved session appears in session list")

        # STEP 7: Confirm evidence is preserved.
        assert reloaded["findings"] == findings

        print("PASS: original evidence preserved")

    print("\nPASS: all Persistence checks completed.")
    print("NOTE: Test files were automatically cleaned up.")


if __name__ == "__main__":
    main()
