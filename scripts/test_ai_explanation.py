from core.ai_explanation import explain_finding

finding = {
    "id": "F003",
    "section": "signature",
    "change_type": "added",
    "reference_evidence": None,
    "incoming_evidence": (
        "If an entity has multiple required signatories, "
        "each required signatory must sign."
    ),
}

explanation = explain_finding(finding)

print("\n=== AI EXPLANATION ===\n")
print(explanation)