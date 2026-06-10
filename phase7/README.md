# "The Closer" — Phase 7 Live Test Send

Phase 7 is configured to support real email dispatches by setting `DRY_RUN=false` in [.env](file:///c:/Users/mahin/Desktop/COLD-EMAIL-PARSER/phase7/.env).

---

## Safety Notice
> [!CAUTION]
> Always verify that your recipient configuration points to your own email address when executing a test run for the first time. Do not spam real recruiters.

---

## Setup & Verification Steps

### Step 1: Set credentials
Open [.env](file:///c:/Users/mahin/Desktop/COLD-EMAIL-PARSER/phase7/.env) and populate the values:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_gmail_address@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SENDER_NAME=Your Name
DRY_RUN=false
USE_LLM=true
GROQ_API_KEY=gsk_your_groq_api_key
```

### Step 2: Configure target list
Open [contacts.json](file:///c:/Users/mahin/Desktop/COLD-EMAIL-PARSER/phase7/contacts.json) and set the `recipient_email` of the first target to your own email address:
```json
  {
    "recipient_name": "Myself",
    "recipient_email": "your_gmail_address@gmail.com",
    "company": "My Target Company",
    ...
  }
```

### Step 3: Run outreach and verify
Run the CLI:
```bash
python main.py
```
- Select **[S]** to send a real email or **[D]** to save a real Gmail Draft.
- Check your Inbox/Outbox or Drafts folder to confirm the email was delivered or drafted successfully.
