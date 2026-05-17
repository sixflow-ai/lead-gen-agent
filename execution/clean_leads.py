"""
Lead Cleaning Pipeline — Normalize, deduplicate, validate, and score.

Takes raw leads from any source and produces a clean, standardized list.

Usage:
    python execution/clean_leads.py --input .tmp/raw_leads.csv --output clean_leads.csv
    python execution/clean_leads.py --merge .tmp/prospeo.csv,.tmp/apollo.csv --output merged_clean.csv
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import load_leads_csv, save_leads_csv, dedupe_leads, TMP_DIR


# Standard output fields — every lead gets normalized to this schema
STANDARD_FIELDS = [
    "first_name", "last_name", "email", "job_title", "company",
    "company_domain", "linkedin_url", "phone", "location",
    "industry", "company_size", "source",
]


def normalize_lead(lead: dict) -> dict:
    """Normalize a single lead to standard fields."""
    normalized = {}
    for field in STANDARD_FIELDS:
        normalized[field] = (lead.get(field) or "").strip()

    # Name cleanup
    normalized["first_name"] = normalized["first_name"].title()
    normalized["last_name"] = normalized["last_name"].title()

    # Email cleanup
    normalized["email"] = normalized["email"].lower().strip()

    # Domain cleanup — extract from email if missing
    if not normalized["company_domain"] and normalized["email"] and "@" in normalized["email"]:
        domain = normalized["email"].split("@")[1]
        # Skip free email providers
        free_providers = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "icloud.com", "mail.com", "protonmail.com"}
        if domain not in free_providers:
            normalized["company_domain"] = domain

    # Clean domain
    normalized["company_domain"] = (
        normalized["company_domain"]
        .replace("https://", "")
        .replace("http://", "")
        .replace("www.", "")
        .rstrip("/")
        .lower()
    )

    return normalized


def validate_email(email: str) -> bool:
    """Basic email format validation."""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_generic_email(email: str) -> bool:
    """Check if email is generic (info@, admin@, etc.)."""
    if not email:
        return False
    prefix = email.split("@")[0].lower()
    generic_prefixes = {
        "info", "admin", "support", "contact", "hello", "help",
        "sales", "marketing", "hr", "office", "team", "general",
        "service", "billing", "accounts", "noreply", "no-reply",
    }
    return prefix in generic_prefixes


def clean_leads(
    leads: list[dict],
    dedupe_key: str = "email",
    remove_generic: bool = True,
    require_email: bool = True,
) -> list[dict]:
    """Full cleaning pipeline: normalize → validate → dedupe → filter."""
    print(f"Starting with {len(leads)} raw leads")

    # 1. Normalize
    normalized = [normalize_lead(l) for l in leads]

    # 2. Validate emails
    if require_email:
        valid = [l for l in normalized if validate_email(l["email"])]
        removed = len(normalized) - len(valid)
        if removed:
            print(f"Removed {removed} leads with invalid/missing emails")
        normalized = valid

    # 3. Remove generic emails
    if remove_generic:
        before = len(normalized)
        normalized = [l for l in normalized if not is_generic_email(l["email"])]
        removed = before - len(normalized)
        if removed:
            print(f"Removed {removed} generic emails (info@, admin@, etc.)")

    # 4. Deduplicate
    normalized = dedupe_leads(normalized, key=dedupe_key)

    print(f"Cleaning complete: {len(normalized)} clean leads")
    return normalized


def merge_and_clean(csv_files: list[str], dedupe_key: str = "email") -> list[dict]:
    """Merge multiple CSV files and clean the combined list."""
    all_leads = []
    for filepath in csv_files:
        filepath = filepath.strip()
        if not filepath:
            continue
        leads = load_leads_csv(filepath)
        print(f"Loaded {len(leads)} from {filepath}")
        all_leads.extend(leads)

    print(f"Total raw leads across all files: {len(all_leads)}")
    return clean_leads(all_leads, dedupe_key=dedupe_key)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean and normalize a lead list")
    parser.add_argument("--input", default="", help="Single CSV to clean")
    parser.add_argument("--merge", default="", help="Comma-separated CSVs to merge and clean")
    parser.add_argument("--output", default="clean_leads.csv")
    parser.add_argument("--dedupe-by", default="email", choices=["email", "domain", "both"])
    parser.add_argument("--keep-generic", action="store_true", help="Keep generic emails")
    parser.add_argument("--no-email-required", action="store_true", help="Keep leads without email")
    args = parser.parse_args()

    if args.merge:
        leads = merge_and_clean(args.merge.split(","), dedupe_key=args.dedupe_by)
    elif args.input:
        raw = load_leads_csv(args.input)
        leads = clean_leads(raw, dedupe_key=args.dedupe_by, remove_generic=not args.keep_generic, require_email=not args.no_email_required)
    else:
        print("Provide --input or --merge")
        sys.exit(1)

    if leads:
        save_leads_csv(leads, args.output)
    else:
        print("No leads survived cleaning.")
