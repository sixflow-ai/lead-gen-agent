"""
Domain Enrichment — Find contacts for businesses that only have a domain/website.

Takes Google Maps or similar output (businesses with domains but no contacts)
and enriches with decision-maker contacts via Prospeo domain search or Blitz.

Usage:
    python execution/enrich_domains.py --input .tmp/gmaps_leads.csv --output enriched_leads.csv
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_env, load_leads_csv, save_leads_csv, TMP_DIR


def enrich_via_prospeo(domain: str, api_key: str, limit: int = 3) -> list[dict]:
    """Find contacts at a domain using Prospeo."""
    import requests

    headers = {"Content-Type": "application/json", "X-KEY": api_key}
    resp = requests.post(
        "https://api.prospeo.io/v1/domain-search",
        headers=headers,
        json={"domain": domain, "limit": limit},
    )

    if resp.status_code != 200:
        return []

    results = resp.json().get("response", {}).get("results", [])
    contacts = []
    for r in results:
        contacts.append({
            "first_name": r.get("first_name", ""),
            "last_name": r.get("last_name", ""),
            "email": r.get("email", ""),
            "job_title": r.get("title", ""),
            "linkedin_url": r.get("linkedin_url", ""),
        })
    return contacts


def enrich_leads(
    leads: list[dict],
    contacts_per_domain: int = 3,
    title_filter: list[str] = None,
) -> list[dict]:
    """Enrich leads that have company_domain but no email."""
    api_key = get_env("PROSPEO_API_KEY")
    enriched = []
    skipped = 0

    for i, lead in enumerate(leads):
        domain = lead.get("company_domain", "").strip()
        email = lead.get("email", "").strip()

        # Already has an email — keep as-is
        if email:
            enriched.append(lead)
            continue

        if not domain:
            skipped += 1
            continue

        print(f"[{i+1}/{len(leads)}] Enriching {domain}...")
        contacts = enrich_via_prospeo(domain, api_key, limit=contacts_per_domain)

        if not contacts:
            # Keep the business record even without contacts
            enriched.append(lead)
            skipped += 1
            continue

        # Apply title filter if specified
        if title_filter:
            filter_lower = [t.lower() for t in title_filter]
            contacts = [
                c for c in contacts
                if any(ft in (c.get("job_title") or "").lower() for ft in filter_lower)
            ] or contacts[:1]  # Fallback to first contact if no title matches

        for contact in contacts:
            merged = {**lead, **contact}
            merged["company_domain"] = domain
            enriched.append(merged)

        time.sleep(0.5)

    print(f"Enrichment complete: {len(enriched)} leads ({skipped} domains had no contacts)")
    return enriched


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enrich business leads with contact data")
    parser.add_argument("--input", required=True, help="Input CSV with company_domain column")
    parser.add_argument("--output", default="enriched_leads.csv")
    parser.add_argument("--contacts-per-domain", type=int, default=3)
    parser.add_argument("--title-filter", default="", help="Comma-separated titles to prioritize")
    args = parser.parse_args()

    leads = load_leads_csv(args.input)
    print(f"Loaded {len(leads)} leads for enrichment")

    title_filter = [t.strip() for t in args.title_filter.split(",") if t.strip()] or None
    enriched = enrich_leads(leads, contacts_per_domain=args.contacts_per_domain, title_filter=title_filter)

    if enriched:
        save_leads_csv(enriched, args.output)
    else:
        print("No enriched leads to save.")
