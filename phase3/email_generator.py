import re

class EmailGenerator:
    def __init__(self, template: str = None):
        """
        Initializes the generator with a custom template or fallback to default.
        :param template: Format string with placeholders matching contact fields.
        """
        self.template = template or self.get_default_template()

    def get_default_template(self) -> str:
        """
        Returns the default Cold Email template.
        """
        return (
            "Hi {recipient_greeting},\n\n"
            "I noticed {company} is hiring for a {role}. {personalization_note}\n\n"
            "I'm {candidate_name}, and I’ve been building projects around {candidate_background}. "
            "The role stood out because it connects closely with my interest in automation and product-focused engineering.\n\n"
            "Would you be open to a quick look at my profile or pointing me to the right person?\n\n"
            "Best,\n"
            "{candidate_name}\n"
            "{portfolio_url}"
        )

    def generate(self, contact: dict) -> tuple[str, str]:
        """
        Generates the email subject line and body using contact variables.
        :param contact: Dictionary with target contact information.
        :return: A tuple of (subject, body).
        """
        # Resolve recipient greeting fallback
        recipient_name = contact.get("recipient_name") or ""
        recipient_name = recipient_name.strip()
        if recipient_name:
            # Take the first name only for a natural tone
            first_name = recipient_name.split()[0]
            recipient_greeting = first_name
        else:
            recipient_greeting = "there"

        # Resolve portfolio URL fallback
        portfolio_url = contact.get("portfolio_url") or ""

        # Construct variables context
        context = {
            "recipient_greeting": recipient_greeting,
            "company": contact.get("company", "your company"),
            "role": contact.get("role", "the open role"),
            "personalization_note": contact.get("personalization_note", ""),
            "candidate_name": contact.get("candidate_name", "a candidate"),
            "candidate_background": contact.get("candidate_background", ""),
            "portfolio_url": portfolio_url
        }

        # Generate subject line
        subject = f"Quick note on the {context['role']} role at {context['company']}"

        # Generate email body
        body = self.template.format(**context)

        # Standardize whitespace (remove trailing newlines and strip whitespace)
        body = body.strip()

        return subject, body

    def validate_email(self, subject: str, body: str) -> list[str]:
        """
        Validates the generated email against length and structure constraints.
        :param subject: Email subject line.
        :param body: Email body.
        :return: List of warning/error messages. If empty, the email is valid.
        """
        warnings = []
        words = body.split()
        word_count = len(words)

        # Constraint: Word count limit
        if word_count > 150:
            warnings.append(f"Email body exceeds 150 words (current: {word_count} words).")

        # Constraint: Needs subject line
        if not subject or len(subject.strip()) == 0:
            warnings.append("Subject line is empty.")

        # Constraint: Call to action check
        # Looks for question marks as indicators of asks
        if "?" not in body:
            warnings.append("Email lacks a clear question or call to action (missing '?').")

        # Constraint: Signature check
        # Verify the body ends or contains a closing signature
        closing_patterns = ["Best", "Regards", "Sincerely", "Thanks"]
        if not any(pattern in body for pattern in closing_patterns):
            warnings.append("Email is missing a closing signature (e.g. 'Best', 'Regards').")

        # Check for unreplaced bracket placeholders
        placeholder_regex = re.compile(r"\{[a-zA-Z_]+\}")
        unreplaced = placeholder_regex.findall(body)
        if unreplaced:
            warnings.append(f"Email contains unreplaced template placeholders: {', '.join(unreplaced)}")

        return warnings
