# phase0/main.py
# Phase 0: Bare minimum start with hardcoded data and simple terminal generation.

contacts = [
    {
        "recipient_name": "Priya Sharma",
        "recipient_email": "priya@example.com",
        "company": "Acme AI",
        "role": "Backend Engineering Intern",
        "personalization_note": "Acme AI recently launched a new open-source agent workflow automation engine.",
        "candidate_name": "Mahin",
        "candidate_background": "Python backend developer with experience in API development and building LLM agents.",
        "portfolio_url": "https://github.com/mahin"
    },
    {
        "recipient_name": "Alex Mercer",
        "recipient_email": "alex@startupcorp.io",
        "company": "StartupCorp",
        "role": "Junior Software Engineer",
        "personalization_note": "StartupCorp just secured a Series A funding round and is expanding the core product engineering team.",
        "candidate_name": "Mahin",
        "candidate_background": "full-stack developer with experience in building clean, responsive user interfaces and robust APIs.",
        "portfolio_url": "https://github.com/mahin"
    }
]

template = """Hi {recipient_name},

I noticed {company} is hiring for a {role}. {personalization_note}

I'm {candidate_name}, and I’ve been building projects around {candidate_background}.

Best,
{candidate_name}
{portfolio_url}"""

def generate_email(contact):
    subject = f"Quick note on the {contact['role']} role"
    body = template.format(**contact)
    return subject, body

def main():
    print("=== PHASE 0: Starting Basic Email Generation ===")
    for contact in contacts:
        subject, body = generate_email(contact)
        print(f"\nSubject: {subject}")
        print("-" * 50)
        print(body)
        print("=" * 50)

if __name__ == "__main__":
    main()
