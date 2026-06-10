# The Closer — Cold Email Writer & Send Bot

Hey! Welcome to **The Closer**. 

Applying to jobs is already tedious, and sending generic cold emails usually ends up in the spam folder. But writing personalized emails manually for every role takes hours. 

I built this bot to solve that. It takes a list of job listings or company contacts, pulls candidate background details, refines the email tone using Groq's LLM (`llama-3.1-8b-instant`), and lets you review, edit, and send or draft them directly to Gmail via secure SMTP/IMAP.

No automated spam. It’s built around **Human-in-the-Loop** confirmation: you inspect and tweak every email before it goes out.

---

## 🚀 Key Features

* **Groq LLM Integration**: Uses llama-3.1-8b-instant to polish outreach emails to sound natural and highly specific to the company's recent news.
* **Streamlit Web Dashboard**: A modern dark-mode web UI to manage targets, edit emails, and check logs.
* **Interactive CLI**: A terminal-based review loop (`[S]end`, `[D]raft`, `[E]dit`, `[K]ip`).
* **Anti-Spam Deduplication**: Logs every outreach attempt in `outreach_log.csv` and automatically screens out contacts you've already emailed.
* **Heuristic Warnings**: Alerts you if an email is too long (> 150 words), missing a call-to-action (`?`), or lacks a standard sign-off.
* **Safety First (`DRY_RUN=true`)**: Active by default so you can test templates safely without sending anything real.

---

## 🛠️ Folder Structure

For teachers or students tracking the progression, this repository is organized into step-by-step checkpoints:
* `phase0/` - Bare minimum setup, hardcoded contact data.
* `phase1/` - Environment settings, requirements, and JSON loading.
* `phase2/` - CSV logging and deduplication logic.
* `phase3/` - Base email template generation & validation guardrails.
* `phase4/` - SMTP delivery engine & IMAP draft appending.
* `phase5/` - Full interactive CLI loop & Groq API refinement.
* `phase6/` - Standalone tests & verification.
* `phase7/` - Setting configuration to live-send mode (`DRY_RUN=false`).
* `phase8/` - Handover documentation & audit history logs.

---

## ⚙️ How to Set Up

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to a new `.env` file at the root:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_gmail@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SENDER_NAME=Your Name
DRY_RUN=true
USE_LLM=true
GROQ_API_KEY=your_groq_api_key
```
*(Use a **Gmail App Password** instead of your raw password if you use 2-Factor Authentication on your Google Account).*

### 3. Add Your Targets
Edit the `contacts.json` file in the root to add your job target contacts.

---

## 💻 Running the App

### Option A: Streamlit Web UI (Recommended)
Launch the web dashboard:
```bash
python -m streamlit run app.py
```
This will spin up a local server at **`http://localhost:8501`** where you can edit templates and review drafts in your browser.

### Option B: Terminal CLI
Run the interactive console script:
```bash
python main.py
```
Type `S` to send, `D` to save a draft, `E` to edit, or `K` to skip the contact.

### Option C: Run Tests
Verify modules are operating correctly:
```bash
python -m unittest test_closer.py
```
