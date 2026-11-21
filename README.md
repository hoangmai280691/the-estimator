# The Estimator

**A rule-based form comparison, implementation scoping, and effort estimation MVP with AI-assisted explanations.**

## 1. Overview

The Estimator is a 10-day MVP designed to support the early stages of form digitization projects.

When a new form is received, scoping owners often need to compare it against an existing reference, identify changes, understand implementation implications, and estimate the required effort.

This process can be time-consuming and dependent on individual experience, particularly when requirements are unclear or seemingly small changes introduce hidden complexity.

The Estimator provides a structured workflow from **change detection to human review, implementation scoping, and effort estimation**.

## 2. Problem & Objective

**Problem**

- Changes between reference and incoming forms can be difficult to identify consistently.
- Small textual differences may introduce additional requirements or conditional logic.
- Scoping decisions may lack clearly documented supporting evidence.
- Different interpretations can lead to misalignment on delivery scope.

**Objective**

Help scoping owners identify unclear requirements and hidden complexity so they can make evidence-backed decisions and align on implementation scope.

## 3. MVP Workflow

### Step 1 — Form Comparison

Upload a reference PDF and an incoming PDF.

The tool processes the documents, compares their content, and generates structured findings with supporting evidence.

### Step 2 — Human Review

Review each detected finding and decide whether to confirm or reject it.

Users can adjust suggested categories and add reviewer notes.

An optional **Explain with AI** feature provides contextual explanations to support understanding.

### Step 3 — Implementation Scoping

Select confirmed findings and organize them into implementation scope items.

Users can document assumptions and manage scope-item status.

### Step 4 — Effort Estimation

Assign complexity levels and estimated hours to scope items.

Complexity and effort are determined manually by the user, not automatically predicted by AI.

### Step 5 — Finalization & Persistence

Generate an estimation summary with total hours and person-days.

Save a draft session and resume the workflow later.

## 4. Technical Approach

**Rule-based detection**

The MVP uses deterministic comparison and detection logic to identify potential changes between forms.

It produces suggested categories and supporting evidence for human verification.

**AI-assisted explanation**

The optional AI feature uses the OpenAI API to explain detected changes and highlight questions that may require further review.

AI does not automatically approve findings, define implementation scope, or estimate effort.

**Human-in-the-loop decisions**

Users remain responsible for confirming findings, defining scope, selecting complexity, and estimating hours.

**Session persistence**

Workflow information can be saved and restored to support continued review and estimation.

## 5. Technology

- Python
- Streamlit
- Rule-based document comparison and detection
- OpenAI API for on-demand explanations
- JSON-based session persistence

## Run Locally

**Requirements**
- Python 3.10 or later
- An OpenAI API key (for the optional AI explanation feature)

**Installation**

1. Clone the repository:

   ```bash
   git clone https://github.com/hoangmai280691/the-estimator.git
   cd the-estimator
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure the OpenAI API key using the application's supported secret configuration.

4. Start the application:

   ```bash
   streamlit run app.py
   ```

The application opens in a browser. The main comparison and estimation workflow is rule-based; AI explanations are an optional supporting feature.

## 6. Limitations

This is an exploratory MVP, not a production-ready estimation system.

- Detection quality depends on the structure and content of the input PDFs.
- Rule-based logic may miss changes or produce findings that require correction.
- AI explanations are supporting information and must be reviewed by users.
- Complexity and estimated hours are manually assigned.
- Estimation accuracy and time savings have not yet been validated through systematic user testing.
- The MVP does not include form building, implementation execution, or actual-effort tracking.

## 7. Future Improvements

Potential next steps include:

- Evaluating detection performance against manually reviewed examples.
- Conducting user testing to assess workflow usability and scoping confidence.
- Improving detection coverage and handling of complex document structures.
- Introducing historical estimation references and actual-effort feedback.

## 8. Demo

**Video walkthrough:** https://www.youtube.com/watch?v=It8GTXasKTI

The demo covers the end-to-end workflow, from PDF comparison to final estimation.