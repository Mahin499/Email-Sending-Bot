# "The Closer" — Phase 8 Final Submission & Proof

Phase 8 satisfies the final demo submission requirements. This directory represents the completed submission package including logs, execution explanations, and configurations.

---

## 1. System Explanation (How it Works)
"The Closer" is a CLI-based agent designed to personalize and automate job outreach while keeping a human review loop:
1. **Target Selection**: Loads outreach targets from [contacts.json](file:///c:/Users/mahin/Desktop/COLD-EMAIL-PARSER/phase8/contacts.json).
2. **Duplicate Screening**: Consults [outreach_log.csv](file:///c:/Users/mahin/Desktop/COLD-EMAIL-PARSER/phase8/outreach_log.csv) to automatically skip previously drafted/sent recipients.
3. **Generation & AI Polishing**: Formats contact details into a structured base layout and personalizes the tone dynamically via Groq's LLM (`llama-3.1-8b-instant`).
4. **Heuristic Warnings**: Evaluates parameters (like word counts, signature presence, call-to-actions) to warn the user of potential quality issues.
5. **Interactive Review**: User reviews generated drafts in the terminal and chooses to Send, Draft, Edit, or Skip.
6. **Logging**: Saves timestamped records in `outreach_log.csv`.

---

## 2. Sending Method Notes
The delivery engine supports two verified modes:
* **SMTP (Send Mode)**: Connects securely over SSL/TLS (`smtp.gmail.com` on port `587`) using a Gmail App Password to dispatch outbound emails directly.
* **IMAP (Draft Mode)**: Logs in securely and appends the MIME outreach directly to Gmail's server Draft folder (`[Gmail]/Drafts`), allowing manual inspection before sending.
