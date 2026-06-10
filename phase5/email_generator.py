import re
import json
from groq import Groq

class EmailGenerator:
    def __init__(self, template: str = None, use_llm: bool = False, groq_api_key: str = None):
        """
        Initializes the generator with a custom template or fallback to default.
        :param template: Format string with placeholders matching contact fields.
        :param use_llm: Whether to use Groq LLM to refine the template.
        :param groq_api_key: The Groq API Key string.
        """
        self.template = template or self.get_default_template()
        self.use_llm = use_llm
        self.groq_api_key = groq_api_key

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

        if self.use_llm and self.groq_api_key:
            subject, body = self._refine_with_llm(subject, body, contact)

        return subject, body

    def _refine_with_llm(self, subject: str, body: str, contact: dict) -> tuple[str, str]:
        """
        Uses Groq API to refine/polish the base email layout and tone.
        Falls back to base email on failure.
        """
        try:
            client = Groq(api_key=self.groq_api_key)
            prompt = (
                f"You are a professional recruiting cold outreach writer. "
                f"Refine the following base outreach email to make it punchy, engaging, and professional. "
                f"Ensure the tone is warm and personalized, but completely free from exaggerated claims. "
                f"Do not invent fake experience or relationships.\n\n"
                f"Base Subject: {subject}\n"
                f"Base Body:\n{body}\n\n"
                f"CRITICAL CONSTRAINTS:\n"
                f"1. The email body MUST be under 150 words.\n"
                f"2. You must output a JSON object with keys 'subject' and 'body'.\n"
                f"3. Do NOT wrap the JSON in markdown blocks (e.g. ```json). Output the raw JSON text directly."
            )

            completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that writes cold outreach emails in raw JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.1-8b-instant",
                temperature=0.7,
                max_tokens=1024,
                response_format={"type": "json_object"}
            )
            
            response_text = completion.choices[0].message.content.strip()
            data = json.loads(response_text)
            
            refined_subject = data.get("subject", subject)
            refined_body = data.get("body", body)
            return refined_subject.strip(), refined_body.strip()
            
        except Exception as e:
            print(f"    [!] LLM Refinement failed (falling back to base template): {e}")
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
