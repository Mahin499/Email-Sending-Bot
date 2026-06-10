# Edge Case Analysis: Cold Email Writer & Send Bot

This document catalogs critical edge cases, expected system behavior, and handling mechanisms for "The Closer" Cold Email Writer & Send Bot.

---

## 1. Input & Data Parsing Edge Cases

| Edge Case | Expected System Behavior | Implementation / Handling |
| :--- | :--- | :--- |
| **Missing `recipient_name`** | The generator should gracefully fall back to a generic greeting rather than crashing or displaying empty spaces. | Resolved in `email_generator.py` by converting to `"Hi there,"` or `"Hi team at {company},"`. |
| **Missing `recipient_email`** | The CLI loop must skip the record entirely. It should write a skip log to `outreach_log.csv` so it isn't repeatedly scanned. | Bypassed in `main.py` with an error message and a skip status entry. |
| **Malformed JSON syntax in `contacts.json`** | The orchestrator should print a user-friendly JSON parsing error and terminate, rather than crashing with a full traceback. | Wrapped in `try-except json.JSONDecodeError` inside `main.py`. |
| **Extra/Unexpected fields in input** | The parser should ignore unused keys and not crash during template replacement. | Done by using `.get()` dictionary retrieval instead of direct index formatting. |
| **Unicode or special characters in names** | Names like "Müller" or "Añigo" must be correctly represented. | Handled by reading input files and writing output logs explicitly with `utf-8` encoding. |

---

## 2. Generation & Validation Edge Cases

| Edge Case | Expected System Behavior | Implementation / Handling |
| :--- | :--- | :--- |
| **Email length exceeds 150 words** | The system must flag a warning to the user before they approve sending the email. | Handled by `validate_email()` counting words and returning warnings displayed in the review prompt. |
| **Unreplaced brace placeholders** | If the template includes braces like `{recipient_name}` and the variable context fails to substitute it, the system must raise a warning. | RegEx lookup `r"\{[a-zA-Z_]+\}"` catches unreplaced markers in `validate_email()`. |
| **Missing Call-to-Action (No clear ask)** | The bot must warn the user that the email does not contain a question mark (`?`). | Checked via `validate_email()` structural heuristics. |
| **Missing sign-off / signature** | The email must have a clean signature containing standard closures like "Best," "Regards," or "Thanks,". | Checks presence of common signatures during validation. |

---

## 3. Safety & Deduplication Edge Cases

| Edge Case | Expected System Behavior | Implementation / Handling |
| :--- | :--- | :--- |
| **Double outreach to same contact** | The system must screen the email address against previously logged entries. | `OutreachLogger.is_already_contacted(email)` returns `True` if log contains `sent` or `drafted`. |
| **Re-sending a failed email** | If an email previously failed (`failed` status) or was skipped (`skipped`), the system should allow outreach retry. | `is_already_contacted` returns `False` for `failed` or `skipped` statuses. |
| **Concurrency or double-run logs** | If two CLI commands run simultaneously, logs could get corrupted. | Log file operations open and close immediately in append mode `mode="a"` to prevent locks. |
| **Safety switch disabled by accident** | If `DRY_RUN` is set to anything but `true`, double-verify credentials to prevent crashes on launch. | Done in `main.py` by requiring non-empty `SMTP_USER` if `DRY_RUN` is false. |

---

## 4. Mail Server & Delivery Edge Cases

| Edge Case | Expected System Behavior | Implementation / Handling |
| :--- | :--- | :--- |
| **SMTP Authentication Failure** | The system should capture the authentication exception, output a clear error message (e.g. "Check your Gmail App Password"), log the status as `failed` with details, and proceed to the next target. | Wrapped in try-catch in `main.py` with log details saved to CSV. |
| **Gmail Draft Folder Mismatch** | Different locales or servers name the Drafts folder differently (e.g. `[Gmail]/Drafts`, `Drafts`, `DRAFTS`). | Iterates through a fallback array of common names in `email_sender.py`. |
| **Connection Timeout or Internet Loss** | If internet connectivity is interrupted mid-outreach, the current target fails and the app terminates safely without corrupting past logs. | SMTP connection block wraps the network socket, and the error writes to the CSV logger. |
| **Provider Rate Limiting** | Sending emails too rapidly can flag spam detectors or hit daily Gmail SMTP limits (500/day). | Managed by Human-in-the-Loop pacing: the user must manually confirm each email, preventing instantaneous automated bursts. |
