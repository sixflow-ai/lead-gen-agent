"""
Email Verification — MillionVerifier integration.

Verifies a list of emails to protect sender reputation.
Removes invalid, disposable, and risky emails before outreach.

Usage:
    python execution/verify_emails.py --input .tmp/prospeo_leads.csv --output verified_leads.csv
"""

import argparse
import csv
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_env, load_leads_csv, save_leads_csv, TMP_DIR


MILLION_BASE = "https://api.millionverifier.com/api/v3"


def verify_single(email: str, api_key: str) -> dict:
    """Verify a single email address."""
    resp = requests.get(
        f"{MILLION_BASE}/",
        params={"api": api_key, "email": email},
    )
    if resp.status_code != 200:
        return {"email": email, "result": "unknown", "quality": 0}

    data = resp.json()
    return {
        "email": email,
        "result": data.get("result", "unknown"),
        "quality": data.get("quality_score", 0),
        "is_free": data.get("free", False),
        "is_disposable": data.get("disposable", False),
    }


def verify_bulk_file(input_csv: Path, api_key: str) -> dict:
    """Upload a CSV file for bulk verification. Returns job ID."""
    with open(input_csv, "rb") as f:
        resp = requests.post(
            f"{MILLION_BASE}/bulkapi/upload",
            params={"api": api_key},
            files={"file": f},
        )
    if resp.status_code != 200:
        print(f"Bulk upload failed: {resp.text}")
        return None
    return resp.json()


def verify_leads(leads: list[dict], method: str = "single") -> list[dict]:
    """
    Verify emails in a lead list.
    method: 'single' (one-by-one, good for <500) or 'bulk' (file upload, for 500+)
    Returns leads with verification status added.
    """
    api_key = get_env("MILLIONVERIFIER_API_KEY")

    if method == "single":
        for i, lead in enumerate(leads):
            email = lead.get("email", "")
            if not email:
                lead["email_status"] = "missing"
                continue

            print(f"[{i+1}/{len(leads)}] Verifying {email}...")
            result = verify_single(email, api_key)
            lead["email_status"] = result["result"]
            lead["email_quality"] = result["quality"]

            time.sleep(0.2)  # Rate limit

    # Filter: keep only good emails
    good_statuses = {"ok", "ok_for_all", "valid"}
    verified = [l for l in leads if l.get("email_status", "").lower() in good_statuses]
    risky = [l for l in leads if l.get("email_status", "").lower() not in good_statuses and l.get("email")]

    print(f"Verification complete: {len(verified)} valid, {len(risky)} removed")
    return verified


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify emails in a lead list")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", default="verified_leads.csv")
    parser.add_argument("--keep-unverified", action="store_true", help="Keep leads that fail verification (flagged)")
    args = parser.parse_args()

    leads = load_leads_csv(args.input)
    print(f"Loaded {len(leads)} leads for verification")

    verified = verify_leads(leads)

    if verified:
        save_leads_csv(verified, args.output)
        print(f"Done. {len(verified)} verified leads saved.")
    else:
        print("No leads passed verification.")
