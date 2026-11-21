from openai import OpenAI
import streamlit as st


def explain_finding(finding: dict) -> str:
    """Explain a detected PDF change using OpenAI."""

    client = OpenAI(
        api_key=st.secrets["OPENAI_API_KEY"]
    )

    prompt = f"""
    You are assisting a business analyst reviewing
    differences between two PDF forms.

    Finding ID: {finding.get("id", "")}
    Section: {finding.get("section", "")}
    Change type: {finding.get("change_type", "")}

    Reference evidence:
    {finding.get("reference_evidence") or "Not provided"}

    Incoming evidence:
    {finding.get("incoming_evidence") or "Not provided"}

    Explain the finding using three sections:

    1. What changed?
    2. Why does it matter?
    3. What should be checked?

    Use only the provided finding as evidence.
    Do not invent requirements.
    Do not estimate implementation effort.
    Keep the explanation concise.
    """

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        max_output_tokens=350,
    )

    return response.output_text