# Evaluation Suite: Phase-Wise Verification

This document provides structured guidelines and test procedures to verify the correctness of each build phase of "The Closer" cold email outreach bot.

---

## Phase 1: Environment & Setup Verification

### Objective
Ensure that environment variables and inputs are parsed without throwing exceptions, and that dependencies install correctly.

* **Dependencies Check**:
  ```bash
  pip show python-dotenv
  ```
  *Pass Criteria*: Outputs details for `python-dotenv` (e.g. version `1.0.1`).
  
* **Mock Data Integrity Check**:
  Ensure [contacts.json](file:///c:/Users/mahin/Desktop/COLD-EMAIL-PARSER/contacts.json) contains all minimum required fields:
  * `recipient_email`
  * `company`
  * `role`
  * `candidate_name`
  * `candidate_background`

---

## Phase 2: Audit & Logging Verification

### Objective
Verify that log entries are correctly appended to the CSV audit log, and that de-duplication behaves accurately.

* **Automated Unit Tests**:
  ```bash
  python -m unittest test_closer.TestOutreachLogger
  ```
  *Pass Criteria*: All logger tests pass without errors.
  
* **Log Behavior Verification**:
  1. Delete `outreach_log.csv` if it exists.
  2. Run unit tests to recreate a test file.
  3. Verify `outreach_log.csv` has headers: `timestamp,recipient_email,company,role,subject,status,error_message`.
  4. Ensure duplicate check queries for `sent` and `drafted` return `True` (Skipped), while queries for `failed` or `skipped` return `False` (Retry).

---

## Phase 3: Email Generation & Safety Verification

### Objective
Validate that text formatting functions successfully replace parameters, respect fallbacks, and highlight validation warnings for edge cases.

* **Automated Unit Tests**:
  ```bash
  python -m unittest test_closer.TestEmailGenerator
  ```
  *Pass Criteria*: All generator validation and fallback tests pass.

* **Warning Guardrail Check**:
  Verify the warning engine flags the following issues correctly:
  - Over 150 words in length.
  - Missing question/ask (`?`).
  - Missing standard closing signature.
  - Unreplaced braces (e.g., `{company}`).

---

## Phase 4: Sender Interface Verification

### Objective
Validate delivery simulations (Console logging in `DRY_RUN`) and verify actual sending/drafting interfaces.

* **Dry Run Verification**:
  Ensure `DRY_RUN=true` prints the email body clearly to stdout with standard boundaries:
  ```text
  [DRY RUN - SMTP SEND] Simulating Email to: ...
  ```
  *Pass Criteria*: No network connection calls are made; no exceptions are thrown.
  
* **Production Draft Check (Optional)**:
  Configure `DRY_RUN=false` and run the script. Select `[D]raft`. Check your Gmail box `Drafts` folder.
  *Pass Criteria*: A drafted email matches the subject and body generated, with no raw curly placeholders.

---

## Phase 5: CLI Orchestrator Verification

### Objective
Verify the end-to-end user experience, interactive prompt choices, and editing flows.

* **Simulation Verification**:
  Run the loop simulating distinct actions:
  ```powershell
  "s`nd`nk" | python main.py
  ```
  *Pass Criteria*:
  - Target 1 triggers simulated Send.
  - Target 2 triggers simulated Draft.
  - Target 3 is skipped.
  - Summary stats show: Processed = 3, Sent = 1, Drafted = 1, Skipped = 1, Failed = 0.
  
* **Deduplication CLI Integration Check**:
  Run `"k" | python main.py` immediately after.
  *Pass Criteria*:
  - Target 1 and 2 skip automatically (not printed for approval).
  - Target 3 prompts normally.
  - Summary stats show: Processed = 1, Sent = 0, Drafted = 0, Skipped = 3, Failed = 0.

* **Edit Interaction Check**:
  Run the app and type `E` to edit. Provide some test text, end with `EOF`.
  *Pass Criteria*: Email preview updates immediately with the edited content and displays new warning counts if word limit constraints are breached.
