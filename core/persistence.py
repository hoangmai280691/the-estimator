
import json
import os
import tempfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


SCHEMA_VERSION = 1

VALID_WORKFLOW_STAGES = {
    "review",
    "scoping",
    "estimation",
    "completed",
}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def create_session(
    reference_filename,
    incoming_filename,
    findings,
    review_items,
):
    """
    Create a new session in memory.
    No file is written until save_session() is called.
    """
    return {
        "schema_version": SCHEMA_VERSION,
        "session_id": str(uuid4()),
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "reference_filename": reference_filename,
        "incoming_filename": incoming_filename,
        "workflow_stage": "review",
        "findings": deepcopy(findings),
        "review_items": deepcopy(review_items),
        "scope_items": [],
        "estimation_items": [],
        "final_estimation": None,
    }


def validate_session(session):
    """
    Validate the basic session structure before saving
    or after loading.
    """
    if not isinstance(session, dict):
        raise ValueError("Session must be a dictionary")

    if session.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported session schema version")

    session_id = session.get("session_id")

    try:
        parsed_id = str(uuid4()) if session_id is None else str(
            __import__("uuid").UUID(session_id)
        )
    except (ValueError, TypeError, AttributeError):
        raise ValueError("Invalid session ID")

    if session_id is None or parsed_id != session_id:
        raise ValueError("Invalid session ID")

    if session.get("workflow_stage") not in VALID_WORKFLOW_STAGES:
        raise ValueError("Invalid workflow stage")

    for field in (
        "findings",
        "review_items",
        "scope_items",
        "estimation_items",
    ):
        if not isinstance(session.get(field), list):
            raise ValueError(f"{field} must be a list")

    if session.get("final_estimation") is not None:
        if not isinstance(session["final_estimation"], dict):
            raise ValueError("final_estimation must be a dictionary")

    for field in ("reference_filename", "incoming_filename"):
        if not isinstance(session.get(field), str):
            raise ValueError(f"{field} must be a string")

    return True


def save_session(session, sessions_dir):
    """
    Save a session to a JSON file.

    Uses a temporary file and atomic replacement to reduce
    the risk of partially written JSON files.
    """
    validate_session(session)

    updated = deepcopy(session)
    updated["updated_at"] = utc_now()

    directory = Path(sessions_dir)
    directory.mkdir(parents=True, exist_ok=True)

    destination = directory / f"{updated['session_id']}.json"

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=directory,
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)

            json.dump(
                updated,
                temporary_file,
                ensure_ascii=False,
                indent=2,
                allow_nan=False,
            )

            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        os.replace(temporary_path, destination)

    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return updated


def load_session(session_id, sessions_dir):
    """
    Load a previously saved session by ID.
    """
    directory = Path(sessions_dir)
    path = directory / f"{session_id}.json"

    with path.open("r", encoding="utf-8") as file:
        session = json.load(file)

    validate_session(session)

    if session["session_id"] != session_id:
        raise ValueError("Session ID does not match filename")

    return session


def list_sessions(sessions_dir):
    """
    Return basic information about saved sessions,
    ordered by last update (newest first).
    """
    directory = Path(sessions_dir)

    if not directory.exists():
        return []

    summaries = []

    for path in directory.glob("*.json"):
        with path.open("r", encoding="utf-8") as file:
            session = json.load(file)

        validate_session(session)

        summaries.append({
            "session_id": session["session_id"],
            "reference_filename": session["reference_filename"],
            "incoming_filename": session["incoming_filename"],
            "workflow_stage": session["workflow_stage"],
            "updated_at": session["updated_at"],
        })

    return sorted(
        summaries,
        key=lambda item: item["updated_at"],
        reverse=True,
    )
