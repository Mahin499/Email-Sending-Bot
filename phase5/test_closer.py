import os
import unittest
import tempfile
import csv
from email_generator import EmailGenerator
from logger import OutreachLogger

class TestEmailGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = EmailGenerator()

    def test_default_generation_with_full_details(self):
        contact = {
            "recipient_name": "Priya Sharma",
            "company": "Acme AI",
            "role": "Backend Engineering Intern",
            "candidate_name": "Jane",
            "candidate_background": "Python development and agent automation",
            "personalization_note": "I read your tech blog about workflow optimizations.",
            "portfolio_url": "https://github.com/jane"
        }
        subject, body = self.generator.generate(contact)
        
        # Verify subject structure
        self.assertIn("Backend Engineering Intern", subject)
        self.assertIn("Acme AI", subject)
        
        # Verify body placeholders substituted correctly
        self.assertIn("Hi Priya,", body)
        self.assertIn("Acme AI is hiring for a Backend Engineering Intern", body)
        self.assertIn("I read your tech blog about workflow optimizations.", body)
        self.assertIn("Jane", body)
        self.assertIn("https://github.com/jane", body)

    def test_generation_fallback_for_missing_recipient_name(self):
        contact = {
            "company": "Acme AI",
            "role": "Backend Engineering Intern",
            "candidate_name": "Jane",
            "candidate_background": "Python development",
            "personalization_note": "Nice website.",
            "portfolio_url": "https://github.com/jane"
        }
        subject, body = self.generator.generate(contact)
        self.assertIn("Hi there,", body)

    def test_validation_warnings_for_oversized_email(self):
        subject = "Quick Note"
        # 160 word body to trigger warnings
        body = "word " * 160 + "?" + "\nBest,\nJane"
        warnings = self.generator.validate_email(subject, body)
        
        self.assertTrue(any("exceeds 150 words" in w for w in warnings))

    def test_validation_warnings_for_missing_components(self):
        # Missing call to action (question mark) and missing signature
        subject = "Quick Note"
        body = "Hi Priya, this is a message with no question and no proper signoff."
        warnings = self.generator.validate_email(subject, body)
        
        self.assertTrue(any("lacks a clear question" in w for w in warnings))
        self.assertTrue(any("missing a closing signature" in w for w in warnings))


class TestOutreachLogger(unittest.TestCase):
    def setUp(self):
        # Use a temporary file for logging tests
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_path = os.path.join(self.temp_dir.name, "test_log.csv")
        self.logger = OutreachLogger(self.log_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_log_file_initialization(self):
        self.assertTrue(os.path.exists(self.log_path))
        with open(self.log_path, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
            self.assertEqual(headers, ["timestamp", "recipient_email", "company", "role", "subject", "status", "error_message"])

    def test_log_and_deduplication(self):
        contact = {
            "recipient_email": "test@example.com",
            "company": "Test Co",
            "role": "Dev"
        }
        
        # Initially false
        self.assertFalse(self.logger.is_already_contacted("test@example.com"))

        # Log skipped - should still be false (we want to retry if skipped)
        self.logger.log(contact, "Test Subject", "skipped")
        self.assertFalse(self.logger.is_already_contacted("test@example.com"))

        # Log drafted - should be true
        self.logger.log(contact, "Test Subject", "drafted")
        self.assertTrue(self.logger.is_already_contacted("test@example.com"))

        # Log sent - should be true
        contact_other = {
            "recipient_email": "other@example.com",
            "company": "Other Co",
            "role": "Designer"
        }
        self.logger.log(contact_other, "Other Subject", "sent")
        self.assertTrue(self.logger.is_already_contacted("other@example.com"))
        
        # Log failed - should be false (so we can retry)
        contact_fail = {
            "recipient_email": "fail@example.com",
            "company": "Fail Co",
            "role": "Admin"
        }
        self.logger.log(contact_fail, "Fail Subject", "failed", "SMTP Connection Error")
        self.assertFalse(self.logger.is_already_contacted("fail@example.com"))

if __name__ == "__main__":
    unittest.main()
