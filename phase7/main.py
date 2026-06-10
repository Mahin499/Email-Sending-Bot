import os
import json
import sys
from dotenv import load_dotenv

from email_generator import EmailGenerator
from email_sender import EmailSender
from logger import OutreachLogger

def load_config() -> dict:
    """
    Loads environment variables from .env and ensures standard variables are set.
    """
    load_dotenv()
    config = {
        "SMTP_HOST": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "SMTP_PORT": os.getenv("SMTP_PORT", "587"),
        "SMTP_USER": os.getenv("SMTP_USER", ""),
        "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD", ""),
        "SENDER_NAME": os.getenv("SENDER_NAME", "Job Seeker"),
        "DRY_RUN": os.getenv("DRY_RUN", "true"),
        "USE_LLM": os.getenv("USE_LLM", "false"),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY", "")
    }
    return config

def load_contacts(filepath: str) -> list[dict]:
    """
    Reads outreach targets from a JSON file.
    """
    if not os.path.exists(filepath):
        print(f"Error: Target data file '{filepath}' not found.")
        sys.exit(1)
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                print("Error: Input data must be a JSON array of contact records.")
                sys.exit(1)
            return data
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON data: {e}")
        sys.exit(1)

def get_multiline_input(current_text: str) -> str:
    """
    Allows the user to input a multi-line string in the terminal.
    Typing 'EOF' on a new line completes the input.
    """
    print("\n--- ENTER NEW EMAIL BODY below ---")
    print("(Type 'EOF' on a new line and press Enter to finish editing. Press Enter on a blank line to keep original.)")
    print("-----------------------------------------------------------------")
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == "EOF":
                break
            lines.append(line)
        except EOFError:
            break
            
    content = "\n".join(lines).strip()
    return content if content else current_text

def run():
    print("=" * 65)
    print("   THE CLOSER — Cold Email Writer & Send Bot CLI Orchestrator")
    print("=" * 65)

    config = load_config()
    dry_run = config["DRY_RUN"].lower() == "true"
    use_llm = config["USE_LLM"].lower() == "true"
    
    print(f"[*] Configuration Loaded:")
    print(f"    - Sender Email : {config['SMTP_USER']}")
    print(f"    - Sender Name  : {config['SENDER_NAME']}")
    print(f"    - Dry Run Mode : {'ACTIVE (No real emails will be sent)' if dry_run else 'OFF (EMAILS WILL SEND REAL OUTBOXES!)'}")
    print(f"    - LLM Refiner  : {'ENABLED (Groq API)' if use_llm else 'DISABLED (Templates only)'}")
    print(f"    - SMTP Host    : {config['SMTP_HOST']}:{config['SMTP_PORT']}")
    print("-" * 65)

    # Validate SMTP setup if dry run is off
    if not dry_run and not config["SMTP_USER"]:
        print("[!] Error: SMTP_USER must be configured in .env to disable DRY_RUN.")
        sys.exit(1)

    contacts = load_contacts("contacts.json")
    print(f"[*] Loaded {len(contacts)} target records from 'contacts.json'.\n")

    # Instantiate modules
    generator = EmailGenerator(
        use_llm=use_llm,
        groq_api_key=config["GROQ_API_KEY"]
    )
    sender = EmailSender(config)
    logger = OutreachLogger()

    stats = {"processed": 0, "sent": 0, "drafted": 0, "skipped": 0, "failed": 0}

    for idx, contact in enumerate(contacts, 1):
        email = contact.get("recipient_email", "").strip()
        company = contact.get("company", "Unknown Company")
        role = contact.get("role", "Unknown Role")

        print(f"[{idx}/{len(contacts)}] Processing target: {company} - {role} ({email})")

        if not email:
            print("    [!] Missing recipient email. Skipping target.")
            stats["skipped"] += 1
            continue

        # Step 1: De-duplication check
        if logger.is_already_contacted(email):
            print(f"    [-] Already contacted {email} (status: sent/drafted). Skipping target to prevent spam.")
            stats["skipped"] += 1
            logger.log(contact, "[System Skip]", "skipped", "Duplicate recipient - already contacted.")
            print("-" * 65)
            continue

        # Step 2: Generation
        subject, body = generator.generate(contact)

        # Interactive loop for this target (to handle edit flow)
        while True:
            # Step 3: Validation checks
            warnings = generator.validate_email(subject, body)
            
            print("\n" + "=" * 65)
            print(f"EMAIL PREVIEW FOR: {email}")
            print("=" * 65)
            print(f"Subject: {subject}")
            print("-" * 65)
            print(body)
            print("=" * 65)

            if warnings:
                print("\n[!] Validation Warnings:")
                for warning in warnings:
                    print(f"    - {warning}")
                print()

            action = input("Select Action: [S]end Email, [D]raft Email, [E]dit body, [K]ip, [Q]uit: ").strip().lower()

            if action == "s":
                try:
                    print("Sending email...")
                    status = sender.send_email(email, subject, body)
                    logger.log(contact, subject, status)
                    stats["sent"] += 1
                    print("[+] Email successfully sent.")
                except Exception as e:
                    logger.log(contact, subject, "failed", str(e))
                    stats["failed"] += 1
                    print(f"[!] Error sending email: {e}")
                break

            elif action == "d":
                try:
                    print("Creating draft...")
                    status = sender.create_draft(email, subject, body)
                    logger.log(contact, subject, status)
                    stats["drafted"] += 1
                    print("[+] Draft successfully created.")
                except Exception as e:
                    logger.log(contact, subject, "failed", str(e))
                    stats["failed"] += 1
                    print(f"[!] Error creating draft: {e}")
                break

            elif action == "e":
                body = get_multiline_input(body)
                continue

            elif action == "k":
                print("Skipping target.")
                logger.log(contact, subject, "skipped")
                stats["skipped"] += 1
                break

            elif action == "q":
                print("\nExiting outreach session.")
                print_summary(stats)
                sys.exit(0)

            else:
                print("[!] Invalid option. Please select S, D, E, K, or Q.")

        stats["processed"] += 1
        print("\n" + "-" * 65 + "\n")

    print_summary(stats)

def print_summary(stats: dict):
    print("=" * 65)
    print("OUTREACH RUN SUMMARY:")
    print("=" * 65)
    print(f"  Total Processed : {stats['processed']}")
    print(f"  Sent Emails     : {stats['sent']}")
    print(f"  Drafted Emails  : {stats['drafted']}")
    print(f"  Skipped Targets : {stats['skipped']}")
    print(f"  Failed Delivery : {stats['failed']}")
    print("=" * 65)

if __name__ == "__main__":
    run()
