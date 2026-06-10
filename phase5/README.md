# "The Closer" — Phase 5 Cold Email Send Bot

Phase 5 represents the final, fully-orchestrated, production-ready version of the Cold Email Send Bot. It connects the data parser, log deduplication engine, warning checker, Groq LLM personalizer, and direct SMTP/IMAP draft sender into a unified CLI client.

---

## 1. Safety Guardrails & Principles
1. **Dry Run Switch (`DRY_RUN=true`)**: Active by default. The CLI prints all outgoing emails and draft creations to the terminal instead of executing network calls.
2. **Human-in-the-Loop Approval**: Every email is previewed along with any structure warnings (word counts, signatures) and must be confirmed before send.
3. **De-duplication**: Previously contacted recipients (status: `sent` or `drafted` in `outreach_log.csv`) are bypassed automatically.

---

## 2. Interactive CLI Commands
During verification runs, you can trigger five choices for each contact record:
* **`S` (Send)**: Dispatches the email immediately using SMTP.
* **`D` (Draft)**: Saves the email directly to your IMAP Drafts folder (e.g. Gmail Drafts).
* **`E` (Edit)**: Allows typing a custom body. Type `EOF` on a new line and press Enter to save.
* **`K` (Skip)**: Bypasses the contact.
* **`Q` (Quit)**: Instantly halts the CLI and reports summary statistics.

---

## 3. Running Instructions

### Step 1: Install Dependencies
Ensure you are in the phase 5 directory and install requirements:
```bash
pip install -r requirements.txt
```

### Step 2: Configure Keys
Initialize `.env` (copied from `.env.example`) and edit with your parameters:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SENDER_NAME=Your Name
DRY_RUN=true
USE_LLM=true
GROQ_API_KEY=gsk_your_groq_api_key
```

### Step 3: Launch CLI Client
```bash
python main.py
```

### Step 4: Run Automated Tests
```bash
python -m unittest test_closer.py
```
