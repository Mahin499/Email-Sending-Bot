import os
import csv
from datetime import datetime

class OutreachLogger:
    def __init__(self, filepath: str = "outreach_log.csv"):
        """
        Initializes the OutreachLogger with a target file path.
        :param filepath: Path to the CSV log file.
        """
        self.filepath = filepath
        self._init_file()

    def _init_file(self) -> None:
        """
        Initializes the CSV file with headers if it does not already exist.
        """
        headers = ["timestamp", "recipient_email", "company", "role", "subject", "status", "error_message"]
        if not os.path.exists(self.filepath):
            with open(self.filepath, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(headers)

    def log(self, contact: dict, subject: str, status: str, error_message: str = "") -> None:
        """
        Appends an outreach attempt log to the CSV file.
        :param contact: Dictionary containing recipient details.
        :param subject: Email subject line.
        :param status: Status string ('sent', 'drafted', 'skipped', 'failed').
        :param error_message: Optional error message if the attempt failed.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        recipient_email = contact.get("recipient_email", "")
        company = contact.get("company", "")
        role = contact.get("role", "")

        row = [timestamp, recipient_email, company, role, subject, status, error_message]
        with open(self.filepath, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(row)

    def is_already_contacted(self, email: str) -> bool:
        """
        Scans the log file to check if the recipient has already been contacted (sent or drafted).
        :param email: Recipient email address to check.
        :return: True if the email was successfully sent or drafted previously, False otherwise.
        """
        if not os.path.exists(self.filepath):
            return False

        with open(self.filepath, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # We consider 'sent' or 'drafted' as contacted to avoid duplicates.
                if row.get("recipient_email") == email and row.get("status") in ("sent", "drafted"):
                    return True
        return False
