import smtplib
import imaplib
import time
from email.mime.text import MIMEText
from email.header import Header

class EmailSender:
    def __init__(self, config: dict):
        """
        Initializes the EmailSender with SMTP and safety configurations.
        Expected config:
            - SMTP_HOST
            - SMTP_PORT
            - SMTP_USER
            - SMTP_PASSWORD
            - SENDER_NAME
            - DRY_RUN (boolean or string 'true'/'false')
        """
        self.config = config
        
        # Parse DRY_RUN safety switch
        dry_run_val = config.get("DRY_RUN", True)
        if isinstance(dry_run_val, str):
            self.dry_run = dry_run_val.lower() == "true"
        else:
            self.dry_run = bool(dry_run_val)

        self.smtp_host = config.get("SMTP_HOST", "smtp.gmail.com")
        try:
            self.smtp_port = int(config.get("SMTP_PORT", 587))
        except ValueError:
            self.smtp_port = 587
            
        self.smtp_user = config.get("SMTP_USER", "")
        self.smtp_password = config.get("SMTP_PASSWORD", "")
        self.sender_name = config.get("SENDER_NAME", "Job Seeker")

    def _create_mime_message(self, to_email: str, subject: str, body: str) -> MIMEText:
        """
        Helper to construct a MIMEText email object.
        """
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = Header(subject, "utf-8")
        msg["From"] = f"{self.sender_name} <{self.smtp_user}>"
        msg["To"] = to_email
        return msg

    def send_email(self, to_email: str, subject: str, body: str) -> str:
        """
        Delivers the email to the recipient.
        If DRY_RUN is active, it only prints the email representation.
        :return: 'sent' on success.
        """
        if self.dry_run:
            print("\n" + "="*50)
            print(f"[DRY RUN - SMTP SEND] Simulating Email to: {to_email}")
            print(f"From: {self.sender_name} <{self.smtp_user}>")
            print(f"Subject: {subject}")
            print("-" * 50)
            print(body)
            print("="*50 + "\n")
            return "sent"

        # Construct MIME Message
        msg = self._create_mime_message(to_email, subject, body)

        # Connect and send
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.smtp_user, [to_email], msg.as_string())

        return "sent"

    def create_draft(self, to_email: str, subject: str, body: str) -> str:
        """
        Appends the email directly to the email server's Drafts folder using IMAP.
        If DRY_RUN is active, it only prints the draft representation.
        :return: 'drafted' on success.
        """
        if self.dry_run:
            print("\n" + "="*50)
            print(f"[DRY RUN - CREATE DRAFT] Simulating Draft for: {to_email}")
            print(f"From: {self.sender_name} <{self.smtp_user}>")
            print(f"Subject: {subject}")
            print("-" * 50)
            print(body)
            print("="*50 + "\n")
            return "drafted"

        # Construct MIME Message
        msg = self._create_mime_message(to_email, subject, body)
        msg_bytes = msg.as_bytes()

        # Connect to IMAP (we assume same host domain but imap prefix, e.g. imap.gmail.com)
        imap_host = self.smtp_host.replace("smtp.", "imap.")
        
        # Connect to IMAP secure
        mail = imaplib.IMAP4_SSL(imap_host)
        mail.login(self.smtp_user, self.smtp_password)

        # Standard folder options for drafts
        draft_folders = ["[Gmail]/Drafts", "Drafts", "DRAFTS"]
        success = False
        error_msg = ""

        # Try common draft folder names
        for folder in draft_folders:
            try:
                # Append to the IMAP folder
                res = mail.append(folder, "", imaplib.Time2Internaldate(time.time()), msg_bytes)
                if res[0] == "OK":
                    success = True
                    break
            except Exception as e:
                error_msg = str(e)
                continue

        # Clean cleanup
        try:
            mail.logout()
        except:
            pass

        if not success:
            raise Exception(f"Failed to create draft in IMAP folders {draft_folders}. Error: {error_msg}")

        return "drafted"
